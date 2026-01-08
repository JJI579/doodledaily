from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
from database import init_db, close_db
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

currentPath = Path.cwd()

@asynccontextmanager
async def lifespan(app: FastAPI):
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
		self.connections = []

	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.connections.append(websocket)
		websocket.tester = "hello"
	
	async def broadcast(self, message: str):
		# NEED TO MAKE THIS PERSONALISED PER CONNECTION
		for connection in self.connections:
			await connection.send_text(message)


manager = WebsocketManager()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await manager.connect(websocket)
	while True:
		data = await websocket.receive_text()
		await websocket.send_text(f"Message text was: {data}")	


from routes import users, auth, friends, photos, notifications

app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(photos.router)
app.include_router(auth.router)

