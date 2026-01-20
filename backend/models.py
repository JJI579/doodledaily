from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
	__tablename__ = "tblUsers"

	userID = Column(Integer, primary_key=True, index=True)
	userName = Column(String, unique=True, nullable=False)
	userPassword = Column(String, nullable=False)
	userCreatedAt = Column(DateTime, default=datetime.utcnow)
	deactivated = Column(Boolean, default=False, nullable=False)
	photos = relationship("Photo", back_populates="owner")
	favourites = relationship(
		"Favourite",
		back_populates="user",
		cascade="all, delete-orphan",
	)
	comments = relationship(
		"Comment",
		back_populates="user",
		cascade="all, delete-orphan",
	)

class Token(Base):
	__tablename__ = "tblTokens"

	# these are JWT Tokens
	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, nullable=False)
	bearerTokenID = Column(String, primary_key=True, nullable=False)
	refreshTokenID = Column(String, primary_key=True, nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
	isActive = Column(Boolean, default=True, nullable=False)

class FCMToken(Base):
	__tablename__ = "tblFCMs"

	tokenID = Column(String(512), primary_key=True, nullable=False)
	userID = Column(Integer, ForeignKey("tblUsers.userID"), nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
	platform = Column(String, nullable=False)

	__table_args__ = (UniqueConstraint("tokenID", "userID", name="uix_token_user"),)


class Photo(Base):
	__tablename__ = "tblPhotos"

	photoID = Column(Integer, primary_key=True, index=True)
	photoName = Column(String, nullable=False)
	photoType = Column(String, nullable=False)
	photoCreatedAt = Column(DateTime, default=datetime.utcnow)
	photoData = Column(String, nullable=False)
	photoOwnerID = Column(Integer, ForeignKey("tblUsers.userID"), nullable=False)
	owner = relationship("User", back_populates="photos")
	isDeleted = Column(Boolean, default=False)
	favourited_by = relationship(
		"Favourite",
		back_populates="photo",
		cascade="all, delete-orphan",
	)
	comments = relationship(
		"Comment",
		back_populates="photo",
		cascade="all, delete-orphan",
	)


class Favourite(Base):
	__tablename__ = "tblFavourites"

	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, nullable=False)
	photoID = Column(Integer, ForeignKey("tblPhotos.photoID"), primary_key=True, nullable=False)
	isFavourited = Column(Boolean, default=True, nullable=False)

	user = relationship("User", back_populates="favourites")
	photo = relationship("Photo", back_populates="favourited_by")

	__table_args__ = (UniqueConstraint("userID", "photoID", name="uix_user_photo"),)


class Comment(Base):
	__tablename__ = "tblComments"

	commentID = Column(Integer, primary_key=True, index=True)
	photoID = Column(Integer, ForeignKey("tblPhotos.photoID"), nullable=False)
	userID = Column(Integer, ForeignKey("tblUsers.userID"), nullable=False)
	comment = Column(String, nullable=False)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

	photo = relationship("Photo", back_populates="comments")
	user = relationship("User", back_populates="comments")

class Friend(Base):
	__tablename__ = "tblFriends"
	 
	senderID = Column(Integer, ForeignKey("tblUsers.userID"),  primary_key=True, index=True)
	receiverID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, index=True)
	status = Column(String, index=True)
	createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)	
	dismissed = Column(Boolean, default=False, nullable=False)

class LikeComment(Base):
	__tablename__ = "tblLikesComments"

	commentID = Column(Integer, ForeignKey("tblComments.commentID"), primary_key=True, nullable=False)
	userID = Column(Integer, ForeignKey("tblUsers.userID"), primary_key=True, nullable=False)
	isLiked = Column(Boolean, default=False, nullable=False)
	likedAt = Column(DateTime, default=datetime.utcnow, nullable=False)

class PushCreated(Base):
	__tablename__ = "tblPushCreated"

	pushID = Column(Integer, primary_key=True, index=True)
	pushTime = Column(DateTime, default=datetime.utcnow, nullable=False)
	hasPushed = Column(Boolean, default=False, nullable=False)


Photo.comments = relationship(
	"Comment",
	back_populates="photo",
	cascade="all, delete-orphan",
)
User.comments = relationship(
	"Comment",
	back_populates="user",
	cascade="all, delete-orphan",
)





