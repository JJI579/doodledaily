

from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from typing import TypedDict, Annotated
from Authentication import Authentication
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from models import User

JWTToken = TypedDict('JWTToken', {
	"type": str,
	"id": int,
	"exp": float
})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

jwtAuthentication = Authentication()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_session)):
	credentialsException = HTTPException(status_code=401, detail="Invalid or expired Bearer Token")
	try:
		decodedToken: JWTToken = jwtAuthentication.decode_access_token(token)
	except:
		raise credentialsException

	user = await session.execute(select(User).where(User.userID == decodedToken["id"]))
	user = user.scalars().first()
	if not user:
		raise credentialsException
	return user