from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select, and_, or_, exists
from typing import Annotated, Union, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Photo, Comment, Favourite, Friend, LikeComment
from modules.funcs import get_current_user, get_session
from sqlalchemy import case, func
from .schema import PhotoCreate, PhotoReturn, CommentCreate, CommentReturn, LikesPhotoReturn, EditPhoto
import secrets

from base64 import b64decode
from .auth import fetchNotificationTokens
from modules.fcm_messaging import dispatchNotification
import datetime

from modules.WebsocketManager import manager, packetClass

from modules.logger import APILogger

apiLog = APILogger()

router = APIRouter(
	prefix="/photos",
	tags=["photos"],
)

def friend_exists(userID: int, friendID: int):
	return exists().where(
		or_(
			and_(
				Friend.senderID == userID,
				Friend.receiverID == friendID,
			),
			and_(
				Friend.receiverID == userID,
				Friend.senderID == friendID,
			),
		),
	)

from pathlib import Path

photosDir = Path.cwd() / "photos"
photosDir.mkdir(exist_ok=True)

@router.post('/create')
async def savePhoto(request: Request, photoData: PhotoCreate, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> PhotoReturn:
	photoName = f"{secrets.token_urlsafe(64)}.png"
	apiLog.info(f"/photos/create | Creating Photo | Username: {current_user.userName}")
	with open(photosDir / photoName, "wb") as f:
		f.write(b64decode(photoData.photoData.split('base64,')[1]))
	apiLog.info(f"/photos/create | Wrote photo | Username: {current_user.userName} | {photoName}")
	photoURL = f'{request.base_url}{"api/" if "127" not in str(request.base_url) else ""}static/{photoName}'
	photoObject = Photo(
		photoName=photoData.photoName,
		photoType=photoData.photoType,
		photoCaption=photoData.photoCaption,
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
	await session.commit()
	await session.refresh(photoObject)
	apiLog.info(f"/photos/create | Committed photo to database | Username: {current_user.userName}")
	if results:
		friend_ids = [x.senderID if x.senderID != current_user.userID else x.receiverID for x in results] # type: ignore
		apiLog.info(f"/photos/create | Found friends, sending notification | Username: {current_user.userName}")
		tokens = await fetchNotificationTokens(*friend_ids) # type: ignore
		apiLog.info(f"/photos/create | Sending notification to {len(friend_ids)} Friends | Username: {current_user.userName}")
		await dispatchNotification(tokens, f"{current_user.userName} has posted a Pibble!")
	await manager.broadcast(packetClass.photo_created(f"{current_user.userName} has posted a Pibble!"), current_user.userID) # pyright: ignore[reportArgumentType]
	apiLog.info(f"/photos/create | Broadcasting to active users | Username: {current_user.userName}")
	return photoObject

@router.get('/fetch')
async def fetch_photos(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession = Depends(get_session)) -> Sequence[Union[LikesPhotoReturn, PhotoReturn]]:
	apiLog.info(f"/photos/fetch | -- Fetch Photos start -- | Username: {current_user.userName}")

	specificUser = request.query_params.get('user')
 
	if specificUser != None:
		# yark fix this
		apiLog.info(f"/photos/fetch | Specific user parameter found: {specificUser}  | Username: {current_user.userName} | {current_user.userID}")
		result = await session.execute(select(Friend).where(
			and_(
				or_(
					Friend.senderID == specificUser,
					Friend.receiverID == specificUser
				),
				or_(
					Friend.senderID == current_user.userID,
					Friend.receiverID == current_user.userID
				),
				Friend.status == "accepted"
			)
		 )) # type: ignore
		results = result.scalars().all()
		
  
		if results or specificUser == str(current_user.userID):
			print("they are friends")
			statement = select(Photo).where(Photo.photoOwnerID == specificUser, Photo.isDeleted == False).order_by(Photo.photoCreatedAt.desc())
			result = await session.execute(statement)
			photos = result.scalars().all()
		else:
			# TODO: change status code to be correct?
			raise HTTPException(status_code=403, detail="Not friends")
		return photos


	afterTimestamp = request.query_params.get('after')
	if afterTimestamp != None:
		apiLog.info(f"/photos/fetch | After parameter found: {afterTimestamp}  | Username: {current_user.userName}")
		after = datetime.datetime.fromisoformat(afterTimestamp.replace('Z', '+00:00'))
	else:
		after = -1
  
	
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
        .join(User, User.userID == Photo.photoOwnerID)
        .group_by(
            Photo.photoID,
            Photo.photoName,
            Photo.photoType,
            Photo.photoCreatedAt,
            Photo.photoData,
            Photo.photoOwnerID
        )
		.where(
			Photo.isDeleted == False, 
			User.deactivated == False,
			or_(
				friend_exists(current_user.userID, Photo.photoOwnerID), # type: ignore
				Photo.photoOwnerID == current_user.userID
			)
		).limit(20).order_by(Photo.photoCreatedAt.desc())
    )
	
	if after != -1:
		apiLog.info(f"/photos/fetch | Applied after timestamp onto statement   | Username: {current_user.userName}")
		statement = statement.where(Photo.photoCreatedAt >= after)
	result = await session.execute(statement)
	x =  [
		LikesPhotoReturn(commentCount=commentcount, photoData=photo.photoData, photoCreatedAt=photo.photoCreatedAt, photoID=photo.photoID, photoName=photo.photoName, photoOwnerID=photo.photoOwnerID, photoType=photo.photoType, isFavourited=is_fav, likesCount=likescount, photoCaption=photo.photoCaption) for photo, is_fav, likescount, commentcount in result.all() 
	]
	apiLog.info(f"/photos/fetch | Returning {len(x)} Photos | Username: {current_user.userName}")
	apiLog.info(f"/photos/fetch | -- Photos Fetch End -- | Username: {current_user.userName}")
	return x

@router.patch('/{photoID}/edit')
async def editPhoto(request: Request, formData: EditPhoto, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photoID', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	apiLog.info(f"/{photoID}/edit | Initiating edit of Photo: {photoID} | Username: {current_user.userName}")
	
	resp = await session.execute(select(Photo).where(Photo.photoID == photoID, Photo.photoOwnerID == current_user.userID))
	photoResult = resp.scalar_one_or_none()
	if not photoResult:
		apiLog.warning(f"/{photoID}/edit | Photo not found in database: {photoID} / {current_user.userName} not the owner. | Username: {current_user.userName}")
		raise HTTPException(status_code=404, detail="Photo not found")
	
	
	if formData.title is not None:
		photoResult.photoName = formData.title # type: ignore
		apiLog.info(f"/{photoID}/edit | Updated title to: {formData.title} | Username: {current_user.userName}")
	
	caption = formData.caption
	if caption is None:
		caption = ""
	caption = caption[:60]
	print(caption)
	photoResult.photoCaption = caption # type: ignore
	apiLog.info(f"/{photoID}/edit | Updated caption | Username: {current_user.userName}")
	await session.commit()
	apiLog.info(f"/{photoID}/edit | Photo updated successfully | Username: {current_user.userName}")
	await manager.broadcast(packetClass.photo_update(photoID), photoResult.photoOwnerID) # type: ignore
	return {
		"detail": "Photo updated successfully"
	}

@router.post('/{photo_id}/delete')
async def deletePhoto(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	apiLog.info(f"/{photoID}/delete | Initiating deletion of Photo: {photoID}  | Username: {current_user.userName}")	
	resp = await session.execute(select(Photo).where(Photo.photoID == photoID, Photo.photoOwnerID == current_user.userID))
	result = resp.scalar_one_or_none()
	if not result:
		apiLog.warning(f"/{photoID}/delete | Photo not found in database: {photoID} / {current_user.userName} not the owner.  | Username: {current_user.userName}")	
		raise HTTPException(status_code=404, detail="Photo not found")
	result.isDeleted = True # type: ignore
	await session.commit()
	apiLog.info(f"/{photoID}/delete | Deleted photo: {photoID} | Username: {current_user.userName}")	
	return {
		"detail": "Deleted Post."
	}

@router.post('/{photo_id}/favourite')
async def favouriteImage(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	apiLog.info(f"/{photoID}/favourite | Initiating favourite action | Username: {current_user.userName}")
	
	resp = await session.execute(select(Photo.photoOwnerID).where(Photo.photoID == photoID))
	ownerID = resp.scalar_one_or_none()
	if not ownerID:
		apiLog.warning(f"/{photoID}/favourite | Photo not found | Username: {current_user.userName}")
		raise HTTPException(status_code=404, detail="Photo not found")

	resp = await session.execute(select(Favourite).where(Favourite.photoID == photoID, Favourite.userID == current_user.userID))
	favouriteObj = resp.scalars().first()
	if not favouriteObj:
		session.add(Favourite(userID=current_user.userID, photoID=photoID, isFavourited=True))
		await session.commit()
		apiLog.info(f"/{photoID}/favourite | Added favourite to database | Username: {current_user.userName}")
	await manager.broadcast(packetClass.photo_update(photoID), ownerID)
	if ownerID != current_user.userID:	
		apiLog.info(f"/{photoID}/favourite | Sending like notification to owner | Username: {current_user.userName}")
		await manager.send_direct_message(packetClass.photo_liked(f"{current_user.userName} liked your Pibble!", photoID), ownerID)
	return {'detail': 'Favourited'}

@router.get('/{photo_id}/fetch')
async def fetchPhoto(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> LikesPhotoReturn:
	photoID = int(request.path_params.get('photo_id', -1))
	apiLog.info(f"/{photoID}/fetch | Fetching single photo | Username: {current_user.userName}")
	# TODO: make this only work for friends, as currently they can fetch anyones.

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
		.where(
			Photo.photoID == photoID,
			Photo.isDeleted == False, 
			or_(
				friend_exists(current_user.userID, Photo.photoOwnerID), # type: ignore
				Photo.photoOwnerID == current_user.userID
			)
		)
    )
	result = await session.execute(statement)
	results = result.all()
	
	if not results:
		apiLog.warning(f"/{photoID}/fetch | Photo not found | Username: {current_user.userName}")
	else:
		apiLog.info(f"/{photoID}/fetch | Photo retrieved successfully | Username: {current_user.userName}")
	return [
		LikesPhotoReturn(commentCount=commentcount, photoData=photo.photoData, photoCreatedAt=photo.photoCreatedAt, photoID=photo.photoID, photoName=photo.photoName, photoOwnerID=photo.photoOwnerID, photoType=photo.photoType, isFavourited=is_fav, likesCount=likescount, photoCaption=photo.photoCaption) for photo, is_fav, likescount, commentcount in results
	][0]

@router.post('/{photo_id}/comments/create')
async def createComment(request: Request, commentData: CommentCreate, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)):
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		raise HTTPException(status_code=400, detail="Photo ID is required")
	if len(commentData.comment.strip()) == 0:
		raise HTTPException(status_code=400, detail="Comment cannot be empty")
	apiLog.info(f"/{photoID}/comments/create | Creating comment | Username: {current_user.userName}")
	statement = select(Photo).where(Photo.photoID == photoID)
	result = await session.execute(statement)
	photoObj = result.scalars().first()
	if not photoObj:
		apiLog.warning(f"/{photoID}/comments/create | Photo not found | Username: {current_user.userName}")
		raise HTTPException(status_code=404, detail="Photo not found")
	
	USER_ID = current_user.userID
	commentModel = Comment(
		photoID=photoID,
		userID=USER_ID,
		comment=commentData.comment
	)
	
	session.add(commentModel)
	await session.commit()
	await session.refresh(commentModel)
	apiLog.info(f"/{photoID}/comments/create | Comment saved to database | Username: {current_user.userName}")
	await manager.broadcast(packetClass.photo_update(photoObj.photoID), photoObj.photoOwnerID) # type: ignore
	if photoObj.photoOwnerID != USER_ID: # type: ignore
		apiLog.info(f"/{photoID}/comments/create | Sending notification to photo owner | Username: {current_user.userName}")
		await manager.send_direct_message(packetClass.comment_created(f"{current_user.userName} commented on your Pibble!", photoObj.photoID), photoObj.photoOwnerID) # pyright: ignore[reportArgumentType]
		tokens = await fetchNotificationTokens(photoObj.photoOwnerID) # type: ignore
		await dispatchNotification(tokens, f"{current_user.userName} commented on your pibble post!", f"photos?showComment={commentModel.commentID}")
	
	return commentModel

@router.get('/{photo_id}/comments')
async def fetchPhotoComments(request: Request, current_user: Annotated[User, Depends(get_current_user)], session: AsyncSession=Depends(get_session)) -> Sequence[CommentReturn]:
	photoID = int(request.path_params.get('photo_id', -1))
	if photoID == -1:
		apiLog.warning(f"/photo_id/comments | Photo not found | Username: {current_user.userName}")
		raise HTTPException(status_code=400, detail="Photo ID is required")

	photoRes = await session.execute(
		select(Photo)
		.where(Photo.photoID == photoID, Photo.isDeleted == False)
	) 
	if not photoRes.scalar_one_or_none():
		apiLog.warning(f"/photo_id/comments | Photo not found to fetch comments | Username: {current_user.userName}")
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
	results = result.all()
	apiLog.info(f"/{photoID}/comments | Returning: {len(results)} | Username: {current_user.userName}")
	return [CommentReturn(commentID=comment.commentID, photoID=comment.photoID, userID=comment.userID, comment=comment.comment, createdAt=comment.createdAt, likeCount=likeCount, hasLiked=isLiked) for comment, likeCount, isLiked in results]

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
		apiLog.info(f"/{commentID}/like | Updated Like to Comment ID: {commentID} | Username: {current_user.userName}")
		await session.commit()
		return {
			"detail": "Liked comment"
		}
	else:
		session.add(LikeComment(commentID=commentID, userID=current_user.userID, isLiked=True))
		await session.commit()
		apiLog.info(f"/{commentID}/like | Inserted Like to Comment ID: {commentID} | Username: {current_user.userName}")

	commentRes = await session.execute(select(Comment).where(Comment.commentID == commentID))
	comment = commentRes.scalar_one_or_none()
	if not comment:
		apiLog.warning(f"/{commentID}/like | Comment not found | Username: {current_user.userName}")
		raise HTTPException(status_code=404, detail="Comment not found")
	if comment.userID != current_user.userID: # type: ignore
		apiLog.info(f"/{commentID}/like | Fetching {comment.userID} FCM tokens to send notification | Username: {current_user.userName}")
		tokens = await fetchNotificationTokens(comment.userID) # type: ignore
		apiLog.info(f"/{commentID}/like | Sending notification to {comment.userID}'s {len(tokens)} Tokens | Username: {current_user.userName}")
		await dispatchNotification(tokens, f"{current_user.userName} liked your comment on a Pibble Post!", f"photos?showComment={commentID}")
	return {
		"detail": "Liked comment"
	}	
		

