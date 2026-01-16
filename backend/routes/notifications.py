from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select, update, and_, or_
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite, Token, FCMToken, Friend
from funcs import get_current_user, get_session
from typing import Sequence
from .auth import fetchNotificationTokens
from fcm_messaging import dispatchNotification

import datetime

router = APIRouter(
	prefix="/notifications",
	tags=["notifications"],
)

class NotificationReturn(BaseModel):
	name: str
	description: str
	createdAt: str
	type: str
	userID: int


@router.get('/fetch')
async def fetchNotifications(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> list[NotificationReturn]:
	resp = await session.execute(select(Friend, User.userName).where(
		or_(
			and_(
				Friend.status == "pending",
				Friend.receiverID == current_user.userID
		),
		and_(
			Friend.status == "accepted",
			or_(
				Friend.receiverID == current_user.userID,
				Friend.senderID == current_user.userID
			)
		))
	).join(
		User, 
		or_(
			and_(
			Friend.senderID != current_user.userID,
			Friend.senderID == User.userID
		) ,
		and_(
			Friend.receiverID != current_user.userID,
			Friend.receiverID == User.userID
		) 
		)
	))
	results = resp.all()


	def handleResult(values):
		result, userName = values
		result: Friend
		if result.status == "pending": # type: ignore
			return NotificationReturn(userID=result.senderID, name="Friend Request", description=f"{userName} has requested to be your friend", createdAt=str(result.createdAt), type="request") # type: ignore
		elif result.status == "accepted": # type: ignore
			return NotificationReturn(userID=result.senderID, name="Friends", description=f"You and {userName} are now friends", createdAt=str(result.createdAt), type="friends") # type: ignore
		
	return [handleResult(result) for result in results] # type: ignore

