from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, close_db, init_db_sync
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from funcs import get_session

from pathlib import Path


from sqlmodel import select, update
from sqlalchemy import and_
import asyncio
from models import PushCreated, User
from routes.auth import fetchNotificationTokens
from fcm_messaging import dispatchNotification
import datetime
import secrets
currentPath = Path.cwd()

def provideRandomTime(focusedDay: datetime.datetime):

	# timeRange of 9am to 9pm
	currentHour = datetime.datetime.utcnow().hour
	hour = secrets.choice([x for x in range(currentHour if currentHour < 21 and currentHour > 9 else 9, 21)])
	minute = secrets.choice([x for x in range(0, 60)])
	return focusedDay.replace(hour=hour, minute=minute)


async def handle_daily_push_notification(resultID: int):
	async for session in get_session():
		allUsers = [x.userID for x in (await session.execute(select(User).where(User.deactivated == False))).scalars().all()]
		tokens = await fetchNotificationTokens(*allUsers)
		await dispatchNotification(tokens, "Time to create a pibble!", "draw")
		await session.execute(update(PushCreated).where(PushCreated.pushID == resultID).values(hasPushed=True))
		await session.commit()
		return
	
async def handle_daily_push(focusedDay = datetime.datetime.utcnow()):
	focusedDay = focusedDay.replace(hour=0, minute=0, second=0, microsecond=0)
	print(focusedDay)
	resp = None
	async for session in get_session():

		resp = await session.execute(select(PushCreated).where(
			PushCreated.pushTime > focusedDay
		))
	if not resp:
		return
	results = resp.scalars().all()
	if results:
		result = results[0]
		if result.hasPushed:
			# move to the next day.
			return await handle_daily_push(focusedDay + datetime.timedelta(days=1))
		if datetime.datetime.now(datetime.timezone.utc).astimezone() > result.pushTime.astimezone(): # type: ignore
			await handle_daily_push_notification(int(result.pushID)) # pyright: ignore[reportArgumentType]
		else:
			# wait for it
			secondsTill = (result.pushTime.astimezone() - datetime.datetime.now(datetime.timezone.utc).astimezone()).total_seconds()
			print(f"Waiting {secondsTill} till distributing the notification")
			while True:
				if datetime.datetime.now(datetime.timezone.utc).astimezone() > result.pushTime.astimezone(): # type: ignore
					break
				await asyncio.sleep(60)

			await handle_daily_push_notification(int(result.pushID)) # pyright: ignore[reportArgumentType]
		return await handle_daily_push()
	else:
		timetoSend = provideRandomTime(focusedDay)
		obj = PushCreated(pushTime=timetoSend, hasPushed=False)
		async for session in get_session():
			session.add(obj)
			await session.commit()
		return await handle_daily_push()

async def push_handler():
	while True:
		try:
			await handle_daily_push()
		except:
			print("Error in push handler")
			raise


@asynccontextmanager
async def lifespan(app: FastAPI):
	init_db_sync()
	await init_db()
	task = asyncio.create_task(push_handler())
	yield
	task.cancel()
	try:
		await task
	except:
		print("Cancelled correctly.")
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

