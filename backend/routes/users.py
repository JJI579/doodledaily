from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Friend
from modules.funcs import get_current_user, get_session
from .schema import UserFetch, ExtendedUserFetch, RequestFetch, SelfFetch
from sqlalchemy import case, or_, and_
from typing import Union

router = APIRouter(
	prefix="/users",
	tags=["users"],
)


@router.get('/fetch/@me')
async def fetch_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> SelfFetch:

	fetchFriends = await session.execute(select(Friend, User).where(and_(
		or_(
			Friend.senderID == current_user.userID,
			Friend.receiverID == current_user.userID
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

	allFriends = fetchFriends.all()
	
	return SelfFetch(friends=[x for _, x in allFriends if x.userID != current_user.userID], userName=str(current_user.userName), userID=current_user.userID, userCreatedAt=current_user.userCreatedAt) # pyright: ignore[reportArgumentType]

@router.get('/{user_id}/fetch')
async def fetchUser(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> Union[UserFetch, ExtendedUserFetch]:
	userID = request.path_params.get('user_id', None)
	implementFriend = True if  request.query_params.get('checkfriend', 'false') == 'true' else False
	
	if not userID:
		raise HTTPException(status_code=400, detail="User ID is required")
	userID = int(userID)
	if implementFriend:
		statement = select(
				User,
				case(
					(Friend.status == "accepted", 1),
					else_=0
				).label("isFriend")
			).join(
				Friend,
				and_(
					or_(Friend.senderID == current_user.userID, Friend.receiverID == current_user.userID),
					or_(
						Friend.status == "accepted",
						Friend.status == "cancelled",
						Friend.status == "declined"
					)
				),
				isouter=True
			).where(User.userID == userID)
		resp = await session.execute(statement)
			
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
	
		
@router.get('/fetch')
async def fetchUsers(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> list[RequestFetch]:
	
	query = request.query_params.get('q')
	if query:
		statement = select(
			User.userID, User.userName, User.userCreatedAt, Friend.status
		).join(Friend, or_(
			and_(
			Friend.receiverID == User.userID,
			Friend.senderID == current_user.userID
		),
		and_(
			Friend.senderID == User.userID,
			Friend.receiverID == current_user.userID
		)
		), isouter=True).where(and_(
			User.userName.like(f"%{query}%"),
			User.deactivated==False
		))
	else:
		statement = select(
			User, Friend.status,
			case(
				(Friend.receiverID == current_user.userID, 1),
				else_=0
			).label("wasSent")
		).join(Friend, or_(
			and_(
			Friend.receiverID == User.userID,
			Friend.senderID == current_user.userID
		),
		and_(
			Friend.senderID == User.userID,
			Friend.receiverID == current_user.userID
		)
		), isouter=True).where(User.deactivated==False)
	resp = await session.execute(statement)
	return [RequestFetch(wasSent=wasSent, status=friendStatus if friendStatus else "none", userID=user.userID, userName=user.userName, userCreatedAt=user.userCreatedAt) for user, friendStatus, wasSent in resp.all() if user.userID != current_user.userID]


@router.delete('/delete/@me')
async def delete_self(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	setattr(current_user, 'deactivated', True)
	session.add(current_user)
	await session.commit()
	return {"detail": "Account deactivated successfully."}