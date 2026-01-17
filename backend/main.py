from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from database import init_db, close_db, init_db_sync, get_session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import json

from sqlalchemy import select, and_
from models import User, Token
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




class WebsocketManager:

	
	def __init__(self) -> None:
		# user_id, {}
		self.connections = {}
		

	async def connect(self, websocket: WebSocket):
		pass
	
	async def broadcast(self, message: str):
		# NEED TO MAKE THIS PERSONALISED PER CONNECTION
		for connection in self.connections:
			await connection.send_text(message)

	async def identify(self, websocket: WebSocket, token: str):
		# They are added to connection manager once they have sent through their bearer token for me to identify.
		async for session in get_session():
			resp = await session.execute(select(Token).where(and_(Token.tokenID == token, Token.isActive == True) ))
			result = resp.scalar_one_or_none()
			print(result)
			if not result: 
				return False
			else:
				pass
		

manager = WebsocketManager()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	while True:
		# await websocket.send_text(f"Message text was: {data}")	
		try:
			hasIdentified = False
			data = await websocket.receive_json()
			if data.get('t', '') == "IDENTIFY" and not hasIdentified:
				await manager.identify(websocket, data['d']['token'])
			elif hasIdentified:
				pass
			else:
				# trying to send data without identifying
				await websocket.close()

		except:
			pass
			



from routes import users, auth, friends, photos, notifications

app.mount('/static', StaticFiles(directory=currentPath / 'photos'), name='static')

app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(photos.router)
app.include_router(auth.router)

