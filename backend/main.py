from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, close_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

from routes import users, auth, friends, photos, notifications

app.mount('/static', StaticFiles(directory=currentPath / 'photos'), name='static')

app.include_router(notifications.router)
app.include_router(users.router)
app.include_router(friends.router)
app.include_router(photos.router)
app.include_router(auth.router)

