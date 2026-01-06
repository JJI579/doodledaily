from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite
from funcs import get_current_user, get_session
from sqlalchemy import case, func
from .schema import PhotoCreate, PhotoReturn, CommentCreate, CommentReturn, LikesPhotoReturn

from .auth import fetchNotificationTokens
from fcm_messaging import dispatchNotification
router = APIRouter(
	prefix="/photos",
	tags=["photos"],
)

@router.post('/create')
async def savePhoto(photoData: PhotoCreate, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	photoObject = Photo(
		photoName=photoData.photoName,
		photoType=photoData.photoType,
		photoData=photoData.photoData,
		photoOwnerID=current_user.userID
	)

	session.add(photoObject)
	await session.commit()

@router.get('/fetch')
async def fetchPhotos(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> list[LikesPhotoReturn]:


	statement = (
        select(
            Photo,
            # isliked for the current user
            func.max(case((Favourite.userID == current_user.userID, 1), else_=0)).label("isliked"),
            # total likes
            func.count(func.distinct(Favourite.userID)).label("likes_count"),
            # total comments
            func.count(func.distinct(Comment.commentID)).label("comments_count")
        )
        .join(Favourite, (Favourite.photoID == Photo.photoID) & (Favourite.isFavourited == True), isouter=True)
        .join(Comment, Comment.photoID == Photo.photoID, isouter=True)
        .group_by(
            Photo.photoID,
            Photo.photoName,
            Photo.photoType,
            Photo.photoCreatedAt,
            Photo.photoData,
            Photo.photoOwnerID
        )
		.where(Photo.isDeleted == False)
    )

	# statement = (
	# 	select(
	# 		Photo,
	# 		# case({Favourite.isFavourited == True: 1}, else_=0).label("isFavourited"),
	# 		# func.count(Favourite.photoID).label('likes_count')
	# 	)
	# 	# TODO: reenable as today
	# 	# .where(func.date(Photo.photoCreatedAt) == func.current_date())
	# 	# .join(
	# 	# 	Favourite,
	# 	# 	(Photo.photoID == Favourite.photoID),
	# 	# 	isouter=False
	# 	# )
	# 	# .group_by(Photo.photoID)
	# )
	result = await session.execute(statement)
	
	x =  [
		LikesPhotoReturn(commentCount=commentcount, photoData=photo.photoData, photoCreatedAt=photo.photoCreatedAt, photoID=photo.photoID, photoName=photo.photoName, photoOwnerID=photo.photoOwnerID, photoType=photo.photoType, isFavourited=is_fav, likesCount=likescount) for photo, is_fav, likescount, commentcount in result.all()
	]
	return list(reversed(x))


@router.post('/{photo_id}/delete')
async def deletePhoto(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	resp = await session.execute(select(Photo).where(Photo.photoID == photoID, Photo.photoOwnerID == current_user.userID))
	result = resp.scalar_one_or_none()
	if not result:
		raise HTTPException(status_code=404, detail="Photo not found")
	print(result)
	print("Deleting photo")
	result.isDeleted = True # type: ignore
	await session.commit()
	return {
		"detail": "Deleted Post."
	}

@router.post('/{photo_id}/favourite')
async def favouriteImage(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	resp = await session.execute(select(Favourite).where(Favourite.photoID == photoID, Favourite.userID == current_user.userID))
	favouriteObj = resp.scalars().first()
	if not favouriteObj:
		session.add(Favourite(userID=current_user.userID, photoID=photoID, isFavourited=True))
		await session.commit()

	
	return {'detail': 'Favourited'}

@router.post('/{photo_id}/comments/create')
async def createComment(request: Request, commentData: CommentCreate, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	statement = select(Photo).where(Photo.photoID == photoID)
	result = await session.execute(statement)
	photoObj = result.scalars().first()
	if not photoObj:
		raise HTTPException(status_code=404, detail="Photo not found")
	
	USER_ID = current_user.userID
	commentModel = Comment(
		photoID=photoID,
		userID=USER_ID,
		comment=commentData.comment
	)
	
	tokens = await fetchNotificationTokens(photoObj.photoOwnerID) # type: ignore
	# TODO: make notification with change to notifications page.
	print(tokens)
	session.add(commentModel)
	await session.commit()
	await session.refresh(commentModel)
	await dispatchNotification(tokens, f"{current_user.userName} commented on your pibble post!", f"photos/showComment={commentModel.commentID}")
	return commentModel

@router.get('/{photo_id}/fetch')
async def fetchPhoto(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> PhotoReturn:
	statement = select(Photo).where(Photo.photoID == int(request.path_params.get('photo_id', -1)), Photo.isDeleted == False)
	result = await session.execute(statement)
	return result.scalars().first()

@router.get('/{photo_id}/comments')
async def fetchPhotoComments(request: Request, session: AsyncSession=Depends(get_session)) -> list[CommentReturn]:
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")

	photoRes =await session.execute(select(Photo).where(Photo.photoID == photoID, Photo.isDeleted == False)) 
	if not photoRes.scalar_one_or_none():
		raise HTTPException(status_code=404, detail="Photo not found")
	statement = select(Comment).where(Comment.photoID == photoID)
	result = await session.execute(statement)
	commentsObj = result.scalars().all()
	return list(commentsObj) if len(commentsObj) > 0 else []

