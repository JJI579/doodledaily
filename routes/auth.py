from fastapi import APIRouter, Depends, Request, HTTPException
from sqlmodel import select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Token, FCMToken
import hashlib 
import secrets
import datetime
import os
from funcs import get_session, get_current_user
from .schema import refreshForm, loginForm, registerForm, TokenForm
from Authentication import Authentication

router = APIRouter(
	prefix="",
	tags=["auth"],
)

jwtAuthentication = Authentication()
async def fetchNotificationTokens(*users: int) -> list[str]:
	print(users)
	async for session in get_session():
	
		tokens = []
		for user in users:
			resp = await session.execute(select(FCMToken).where(FCMToken.userID == user))
			tokens.extend([x.tokenID for x in resp.scalars().all()])
		return tokens
	return []



@router.post('/refresh')
async def refresh(refreshData: refreshForm, session: AsyncSession = Depends(get_session)):
	resp = await session.execute(select(Token).where(Token.tokenID == refreshData.token))
	tokenData: Token = resp.scalars().first()
	if tokenData:
		accessToken, expiry = jwtAuthentication.create_access_token(tokenData.userID) # type: ignore
		return {'access_token': accessToken, 'token_type': 'bearer', 'expires_in': expiry}
	else:
		raise HTTPException(status_code=401, detail="Invalid refresh token")
	
@router.post('/login')
async def login(loginData: loginForm, session: AsyncSession = Depends(get_session)):
	resp = await session.execute(select(User).where(User.userName == loginData.username)) 
	user: User = resp.scalars().first() 
	if not user:
		raise HTTPException(status_code=401, detail="Incorrect password or username invalid")

	mysalt = os.getenv('SALT')
	saltedPassword = f'{mysalt}:{loginData.password}'
	hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
	if hashedPassword == (user.userPassword): # pyright: ignore[reportOptionalMemberAccess]
		accessToken, expiry = jwtAuthentication.create_access_token(user.userID) # type: ignore

		refresh_token = secrets.token_urlsafe(56)
		while True:
			if not (await session.execute(select(Token).where(Token.tokenID == refresh_token))).scalar_one_or_none() :
				break
			else:
				refresh_token = secrets.token_urlsafe(56)

		refreshTokenObject = Token(tokenID=refresh_token, userID=user.userID, isActive=True)
		session.add(refreshTokenObject)
		await session.commit()

		return {
			"type": "Bearer",
			"id": user.userID,
			"token": accessToken,
			"refresh_token": refresh_token,
			"expires_at": expiry
		}
	raise HTTPException(status_code=401, detail="Incorrect password or username invalid")

@router.post('/register')
async def register(registerData: registerForm, session: AsyncSession = Depends(get_session)):

	resp = await session.execute(select(User).where(User.userName == registerData.username))
	user = resp.scalars().first()
	if user: 
		raise HTTPException(status_code=404, detail="User already exists")
	
	# check password length
	if len(registerData.password) < 8:
		raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

	mysalt = os.getenv('SALT')
	saltedPassword = f'{mysalt}:{registerData.password}'
	hashedPassword = hashlib.sha256(saltedPassword.encode('utf-8')).hexdigest()
	newUser = User(userName=registerData.username, userPassword=hashedPassword, userCreatedAt=datetime.datetime.now(datetime.timezone.utc))
	session.add(newUser)
	await session.commit()
	return {"message": "User created successfully"}

@router.post('/token')
async def fcmToken(tokenFormData: TokenForm, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
	resp = await session.execute(select(FCMToken).where(FCMToken.tokenID == tokenFormData.token))
	tokenData: Token = resp.scalars().first()
	if tokenData:
		# TODO: if token data, consider what to do 
		# await session.delete(tokenData)
		# await session.commit()
		return {"message": "Token has been found."}
	else:
		# create token
		refreshTokenObject = FCMToken(platform=tokenFormData.platform, tokenID=tokenFormData.token, userID=user.userID)
		session.add(refreshTokenObject)
		await session.commit()
		return {"message": "Token created successfully"}