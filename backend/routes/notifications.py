from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select, update, and_
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


@router.get('/')
async def fetchNotifications(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> list[NotificationReturn]:
	resp = await session.execute(select(Friend).where(
		and_(
			Friend.status == "pending",
			Friend.receiverID == current_user.userID
		)
	))
	result = resp.scalars().all()
	result: Sequence[Friend]
	return [NotificationReturn(userID=FriendRequest.senderID, name="Friend Request", description=f"{FriendRequest.senderID} has requested to be your friend", createdAt=str(FriendRequest.createdAt), type="request") for FriendRequest in result] # type: ignore

