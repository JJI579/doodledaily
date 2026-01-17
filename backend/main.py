from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from database import init_db, close_db, init_db_sync, get_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import json
from WebsocketManager import manager
from sqlalchemy import select, and_, or_
from models import User, Token, Friend
currentPath = Path.cwd()

@asynccontextmanager
async def lifespan(app: FastAPI):
	init_db_sync()
	await init_db()
	# async with engine.begin() as conn:
	# 	await conn.run_sync(Base.metadata.create_all)
	yield
	await close_db()

app = FastAPI(title="Basic FastAPI", lifespan=lifespan)

origins = [
	"http://127.0.0.1:5173",
	"http://localhost:5173",
	"https://pibble.pics/api",
	"https://pibble.pics",
]


# this is great
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,      # explicit allowed origins
	allow_credentials=True,     # allow cookies or Authorization headers
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/")
async def root():
	return {"message": "Hello World"}

tempString = ""
from pydantic import BaseModel
class tempForm(BaseModel):
	string: str

@app.get('/temp')
async def fetchtemp():
	return {
		"detail": tempString
	}
@app.post('/temp')
async def tempDebug(tempData: tempForm):
	global tempString
	tempString = tempData.string
	return {
		"detail": "ok"
	}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	userIdentified = False
	while True:
		# await websocket.send_text(f"Message text was: {data}")	
		try:
			data = await websocket.receive_json()
			packetType = data.get('t', '')
			if packetType == "IDENTIFY" and not userIdentified:
				identifyResponse = await manager.identify(websocket, data['d']['token'])
				if not identifyResponse:
					return await websocket.close()
				userIdentified = identifyResponse
				print(userIdentified)
				websocket.user_id = userIdentified # pyright: ignore[reportAttributeAccessIssue]
			else:
				# trying to send data without identifying
				print("doing")
				await websocket.close()
		except Exception as e:
			print("ws error:", e)
			print("closing")
			try:
				potentialID	 = getattr(websocket, "user_id")
				if potentialID:
					await manager.remove(potentialID)
			except AttributeError:
				break
			break
			



from routes import users, auth, friends, photos, notifications

app.mount('/static', StaticFiles(directory=currentPath / 'photos'), name='static')

app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(photos.router)
app.include_router(auth.router)

