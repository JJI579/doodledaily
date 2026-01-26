from fastapi.websockets import WebSocket
from models import Token, User, Friend
from sqlalchemy import and_, select, or_
from modules.database import get_session
import json
from typing import Optional

class WebsocketPacket:
	def createPacket(self, packetType: str, content):

		content = {
			't': packetType.upper(),
			'd': content if type(content) == dict else {'text': content} # pyright: ignore[reportCallIssue]
		}
		return content
	
	def photo_created(self, message: str):
		return self.createPacket("PHOTO_CREATE", message)	

	def comment_created(self, message: str, photoID: int):
		x = {
			'text': message,
			"onclick": photoID
		}
		return self.createPacket("COMMENT_CREATE", x)

	def friend_request(self, message: str):
		return self.createPacket("FRIEND_REQUEST", message)

	def photo_liked(self, message: str, photoID: int):
		x = {
			'text': message,
			'photoID': photoID 
		}

		return self.createPacket("PHOTO_LIKE", x)
	
	def photo_update(self, photoID: int):
		x = {
			'photoID': photoID
		}
		return self.createPacket("PHOTO_UPDATE", x)
	
class WebsocketManager:

	def __init__(self) -> None:
		self.connections = {}
		
	async def send_message(self, websocket: WebSocket, message: str):
		await websocket.send_text(message)

	async def send_direct_message(self, message, userID: int):
		if type(message) == dict:
			message = json.dumps(message)
		if userID in self.connections:
			await self.send_message(self.connections[userID]['websocket'], message)

	async def broadcast(self, message, userID: Optional[int]=None):
		origMessage = message
		if type(message) == dict:
			message = json.dumps(message)
		if userID is not None:

			# NEED TO MAKE THIS PERSONALISED PER CONNECTION
			if userID in self.connections:
				for toSendID in self.connections[userID]['friends']:
					if toSendID in self.connections:
						await self.send_message(self.connections[toSendID]['websocket'], message)
			if origMessage.get('t') == 'PHOTO_UPDATE':
				if userID in self.connections:
					await self.send_message(self.connections[userID]['websocket'], message)
			else:
				return
		else:
			for connection in self.connections:
				await self.send_message(self.connections[connection]['websocket'], message)

	async def remove(self, userID: int):
		if userID in self.connections:
			try:
				# incase websocket already closing.
				await self.connections[userID]["websocket"].close()
			except:
				pass
			del self.connections[userID]

	async def identify(self, websocket: WebSocket, token: str):
		# They are added to connection manager once they have sent through their bearer token for me to identify.
		async for session in get_session():
			resp = await session.execute(select(Token.userID, User).where(and_(Token.bearerTokenID == token, Token.isActive == True)).join(
				User, User.userID == Token.userID
			))
			result = resp.all()
			if not result: 
				# close websocket.
				return False
			else:
				# fetch user info, friends' ids and add to connection manager to handle.
				userID, userInfo = result[0]

				fetchFriends = await session.execute(select(Friend, User).where(and_(
					or_(
						Friend.senderID == userID,
						Friend.receiverID == userID
					),
					Friend.status == "accepted"
				)).join(
					User,
					or_(
						Friend.senderID == User.userID,
						Friend.receiverID == User.userID
					),
					isouter=True
				).group_by(User.userID).distinct()
				)

				allFriends = set([friendInfo.userID for _, friendInfo in fetchFriends.all() if friendInfo.userID != userID])
				self.connections[userID] = {
					"websocket": websocket,
					"info": userInfo,
					"friends": allFriends
				}
				return userID
			
	async def close_all(self):
		for connection in self.connections:
			await connection.close()

global manager, packetClass
packetClass = WebsocketPacket()
manager = WebsocketManager()