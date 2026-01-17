from fastapi.websockets import WebSocket
from models import Token, User, Friend
from sqlalchemy import and_, select, or_
from database import get_session



class WebsocketManager:

	
	def __init__(self) -> None:
		# user_id, {}
		self.connections = {}
		

	async def connect(self, websocket: WebSocket):
		pass
	
	async def broadcast(self, message: str):
		# NEED TO MAKE THIS PERSONALISED PER CONNECTION
		for connection in self.connections:
			await connection.send_text(message)

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

manager = WebsocketManager()