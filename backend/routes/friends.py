from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select, update
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite, Token, FCMToken, Friend
from funcs import get_current_user, get_session

from .auth import fetchNotificationTokens
from fcm_messaging import dispatchNotification

router = APIRouter(
	prefix="/friends",
	tags=["friends"],
)

@router.post('/{user_id}/request')
async def requestFriend(request: Request, user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	receiverID = int(request.path_params.get('user_id', -1))
	if receiverID == -1:
		raise HTTPException(status_code=400, detail="User ID is required")
	
	# Check if receiver user exists.
	resp = await session.execute(select(User).where(User.userID == receiverID))
	if not resp.scalar_one_or_none():
		raise HTTPException(status_code=404, detail="User not found")
	
	# check if user already has a pending request
	resp = await session.execute(select(Friend).where(Friend.senderID==user.userID and Friend.receiverID==int(receiverID)))
	result = resp.scalar_one_or_none()
	if result:
		raise HTTPException(status_code=400, detail="Friend request already sent")
	else:
		# create request 
		session.add(Friend(senderID=user.userID, receiverID=receiverID, status="pending"))
		tokens = await fetchNotificationTokens(receiverID)
		await dispatchNotification(tokens, f"{user.userName} has requested you as a friend!")
		await session.commit()

@router.post('/{user_id}/accept')
async def acceptFriend(request: Request, user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	senderID = int(request.path_params.get('user_id', -1))
	if senderID == -1:
		raise HTTPException(status_code=400, detail="User ID is required")
	
	result = await session.execute(
		update(Friend)
		.where(
			Friend.senderID == senderID,
			Friend.receiverID == user.userID,
			Friend.status == "pending"
		)
		.values(status="accepted")
		.returning(Friend.senderID, Friend.receiverID, Friend.status)
	)
	await session.commit()
	if result.first():
		tokens = await fetchNotificationTokens(senderID)
		await dispatchNotification(tokens, f"{user.userName} accepted your friend request!")
		return {
			'detail': "Accepted Friend!"
		}
	
	else:
		raise HTTPException(status_code=404, detail="Friend request not found")

@router.post('/{user_id}/decline')
async def declineFriend(request: Request, user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	senderID = int(request.path_params.get('user_id', -1))
	if senderID == -1:
		raise HTTPException(status_code=400, detail="User ID is required")

	result = await session.execute(
		update(Friend)
		.where(
			Friend.senderID == senderID,
			Friend.receiverID == user.userID,
			Friend.status == "pending"
		)
		.values(status="declined")
		.returning(Friend.senderID, Friend.receiverID, Friend.status)
	)
	await session.commit()
	if result.first():
		tokens = await fetchNotificationTokens(senderID)
		await dispatchNotification(tokens, f"{user.userName} declined your friend request :(")
		return {
			'detail': "Declined Friend"
		}
	else:
		raise HTTPException(status_code=404, detail="Friend request not found")
	