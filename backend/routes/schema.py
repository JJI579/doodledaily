from pydantic import BaseModel
import datetime
from typing import Optional
class PhotoCreate(BaseModel):
	photoName: str
	photoType: str
	photoData: str
	photoCaption: str = ""

class UserFetch(BaseModel):
	userID: int
	userName: str
	userCreatedAt: datetime.datetime

	class Config:
		from_attributes = True


class SelfFetch(UserFetch):
	friends: list[UserFetch]


class RequestFetch(UserFetch):
	status: str
	wasSent: bool

class ExtendedUserFetch(UserFetch):
	isFriend: bool

class PhotoReturn(PhotoCreate):
	photoID: int
	photoCreatedAt: datetime.datetime
	photoOwnerID: int
	isFavourited: bool = False
	class Config:
		from_attributes = True

class LikesPhotoReturn(PhotoReturn):
	likesCount: int
	commentCount: int
	

class CommentReturn(BaseModel):
	commentID: int
	photoID: int
	userID: int
	comment: str
	createdAt: datetime.datetime
	likeCount: int
	hasLiked: bool
class EditPhoto(BaseModel):
	title: Optional[str] = ""
	caption: Optional[str] = ""

class CommentCreate(BaseModel):
	comment: str

class loginForm(BaseModel):
	username: str
	password: str

class registerForm(BaseModel):
	username: str
	password: str

class refreshForm(BaseModel):
	token: str

class TokenForm(BaseModel):
	token: str
	platform: str