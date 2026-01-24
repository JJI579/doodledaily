

from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from typing import TypedDict, Annotated
from Authentication import Authentication
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from models import User, Token

JWTToken = TypedDict('JWTToken', {
	"type": str,
	"id": int,
	"exp": float
})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
jwtAuthentication = Authentication()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_session)):
	credentialsException = HTTPException(status_code=401, detail="Invalid or expired Bearer Token")
	if token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYmVhcmVyIiwiaWQiOjE1LCJleHAiOjE3NjkzNDM2MDIuODQ5NjF9.iKGbG3m7C8MHUz1bxMRAXWeMuG0XOHywmkvSb0Qwo9A":
		raise credentialsException
	try:
		decodedToken: JWTToken = jwtAuthentication.decode_access_token(token)
	except:
		raise credentialsException

	resp = await session.execute(select(Token, User).where(Token.bearerTokenID == token).join(User, User.userID == decodedToken['id']))
	result = resp.all()
	if not result:
		raise credentialsException
	return result[0][1]