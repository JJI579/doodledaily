from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select, and_, or_, exists
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite, Friend, LikeComment
from funcs import get_current_user, get_session
from sqlalchemy import case, func
from .schema import PhotoCreate, PhotoReturn, CommentCreate, CommentReturn, LikesPhotoReturn
import secrets
from base64 import b64decode
from .auth import fetchNotificationTokens
from fcm_messaging import dispatchNotification

router = APIRouter(
	prefix="/photos",
	tags=["photos"],
)

from pathlib import Path

photosDir = Path.cwd() / "photos"
photosDir.mkdir(exist_ok=True)

@router.post('/create')
async def savePhoto(request: Request, photoData: PhotoCreate, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)):
	photoName = f"{secrets.token_urlsafe(64)}.png"
	
	with open(photosDir / photoName, "wb") as f:
		f.write(b64decode(photoData.photoData.split('base64,')[1]))
	
	photoURL = f'{request.base_url}{"api/" if "127" not in str(request.base_url) else ""}static/{photoName}'
	photoObject = Photo(
		photoName=photoData.photoName,
		photoType=photoData.photoType,
		photoData=photoURL,
		photoOwnerID=current_user.userID
	)
	session.add(photoObject)

	resp = await session.execute(select(Friend).where(
		and_(
			or_(
			Friend.senderID == current_user.userID,
			Friend.receiverID == current_user.userID
		),
		Friend.status == "accepted"
		)
	))
	results = resp.scalars().all()
	if results:
		friend_ids = [x.senderID if x.senderID != current_user.userID else x.receiverID for x in results] # type: ignore
		tokens = await fetchNotificationTokens(*friend_ids) # type: ignore
		await dispatchNotification(tokens, f"{current_user.userName} has posted a Pibble!")

	await session.commit()

@router.get('/fetch')
async def fetchPhotos(current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> list[LikesPhotoReturn]:

	friend_exists = exists().where(
		and_(
			# Friend.status == "accepted",
			or_(
				and_(
					Friend.senderID == current_user.userID,
					Friend.receiverID == Photo.photoOwnerID,
				),
				and_(
					Friend.receiverID == current_user.userID,
					Friend.senderID == Photo.photoOwnerID,
				),
			),
		)
	)
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
		.where(Photo.isDeleted == False, or_(
			friend_exists,
			Photo.photoOwnerID == current_user.userID
		))
    )
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

@router.get('/{photo_id}/fetch')
async def fetchPhoto(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> PhotoReturn:
	statement = select(Photo).where(Photo.photoID == int(request.path_params.get('photo_id', -1)), Photo.isDeleted == False)
	result = await session.execute(statement)
	return result.scalars().first()

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
	if len(commentData.comment.strip()) == 0:
		raise HTTPException(status_code=400, detail="Comment cannot be empty")
	
	USER_ID = current_user.userID
	commentModel = Comment(
		photoID=photoID,
		userID=USER_ID,
		comment=commentData.comment
	)
	
	tokens = await fetchNotificationTokens(photoObj.photoOwnerID) # type: ignore
	# TODO: make notification with change to notifications page.
	session.add(commentModel)
	await session.commit()
	await session.refresh(commentModel)
	await dispatchNotification(tokens, f"{current_user.userName} commented on your pibble post!", f"photos?showComment={commentModel.commentID}")
	return commentModel

@router.get('/{photo_id}/comments')
async def fetchPhotoComments(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> list[CommentReturn]:
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")

	photoRes = await session.execute(
		select(Photo)
		.where(Photo.photoID == photoID, Photo.isDeleted == False)
	) 
	if not photoRes.scalar_one_or_none():
		raise HTTPException(status_code=404, detail="Photo not found")

	result = await session.execute(
		select(
        Comment,
        func.count(LikeComment.commentID).label("likeCount"),
        func.max(
            case(
                (LikeComment.userID == current_user.userID, 1),
                else_=0,
            )
        ).label("isLiked"),
    )
    .join(
        LikeComment,
        LikeComment.commentID == Comment.commentID,
        isouter=True,
    )
    .where(Comment.photoID == photoID)
    .group_by(Comment.commentID))
	return [CommentReturn(commentID=comment.commentID, photoID=comment.photoID, userID=comment.userID, comment=comment.comment, createdAt=comment.createdAt, likeCount=likeCount, hasLiked=isLiked) for comment, likeCount, isLiked in result.all()]

@router.post('/{photo_id}/comments/{comment_id}/like')
async def likeComment(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	commentID = int(request.path_params.get('comment_id', -1))
	if commentID == -1:
		raise HTTPException(status_code=400, detail="Comment ID is required")
	
	resp = await session.execute(select(LikeComment).where(
		and_(
			LikeComment.commentID == commentID,
			LikeComment.userID == current_user.userID
		)
	))
	result = resp.scalar_one_or_none()
	if result:
		result.isLiked = True # type: ignore
		await session.commit()
		return {
			"detail": "Liked comment"
		}
	else:
		session.add(LikeComment(commentID=commentID, userID=current_user.userID, isLiked=True))
		await session.commit()

	commentRes = await session.execute(select(Comment).where(Comment.commentID == commentID))
	comment = commentRes.scalar_one_or_none()
	if not comment:
		raise HTTPException(status_code=404, detail="Comment not found")
	if comment.userID != current_user.userID: # type: ignore
		tokens = await fetchNotificationTokens(comment.userID) # type: ignore
		await dispatchNotification(tokens, f"{current_user.userName} liked your comment on pibble post!", f"photos?showComment={commentID}")
	return {
		"detail": "Liked comment"
	}	
		