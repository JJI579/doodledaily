from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite, Token, FCMToken, Friend
from funcs import get_current_user, get_session
from .schema import UserFetch, ExtendedUserFetch
from sqlalchemy import case, or_, and_
from typing import Union

router = APIRouter(
	prefix="/users",
	tags=["users"],
)


@router.get('/fetch/@me')
async def fetch_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> UserFetch:
	return current_user

@router.get('/{user_id}/fetch')
async def fetchUser(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> Union[UserFetch, ExtendedUserFetch]:
	userID = request.path_params.get('user_id', None)
	implementFriend = True if  request.query_params.get('checkfriend', 'false') == 'true' else False
	
	if not userID:
		raise HTTPException(status_code=400, detail="User ID is required")
	userID = int(userID)
	if implementFriend:
		resp = await session.execute(
			select(
				User,
				case(
					(Friend.status == "accepted", 1),
					else_=0
				).label("isFriend")
			)
			.join(
				Friend,
				and_(
					or_(Friend.senderID == current_user.userID, Friend.receiverID == current_user.userID),
					Friend.status == "accepted"
				),
				isouter=True
			)
			.where(User.userID == userID)
		)
		test = [ExtendedUserFetch(
			userID=user.userID,
			userName=user.userName,
			userCreatedAt=user.userCreatedAt,
			isFriend=isFriend
		) for user, isFriend in resp.all()]

		if not test: 
			raise HTTPException(status_code=404, detail="User not found")
		return test[0]
	else:
		resp = await session.execute(select(User).where(User.userID == userID))
		userObj = resp.scalars().first()
		if not userObj:
			raise HTTPException(status_code=404, detail="User not found")
		return userObj
	
		

