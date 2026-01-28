import datetime, secrets
from fcm_messaging import dispatchNotification
from routes.auth import fetchNotificationTokens
from sqlalchemy import select, update, and_
from models import PushCreated, User
from database import get_session, init_db
import asyncio
from modules.logger import DailyNotificationLogger

logger = DailyNotificationLogger(name="DailyNotificationLogger", logFileName="daily_notification.log")


def provideRandomTime(focusedDay: datetime.datetime):
	# timeRange of 9am to 9pm
	currentHour = datetime.datetime.utcnow().hour
	hour = secrets.choice([x for x in range(currentHour if currentHour < 21 and currentHour > 9 else 9, 21)])
	minute = secrets.choice([x for x in range(0, 60)])
	return focusedDay.replace(hour=hour, minute=minute)


async def handle_daily_push_notification(resultID: int):
	async for session in get_session():
		allUsers = [x.userID for x in (await session.execute(select(User).where(User.deactivated == False))).scalars().all()]
		logger.info(f"Sending Daily Notification to {len(allUsers)} Users")
		tokens = await fetchNotificationTokens(*allUsers) # pyright: ignore[reportArgumentType]
		await dispatchNotification(tokens, "Time to create a pibble!", "draw") # type: ignore
		logger.info(f"Pushed Daily Notification to {len(tokens)} FCM Tokens")
		x = await session.execute(update(PushCreated).where(PushCreated.pushID == resultID).values(hasPushed=True).returning(PushCreated.pushID))
		await session.commit()
		logger.info(f"Updated Table's pushID: {x.all()} and set to sent")
		return
	
async def handle_daily_push(focusedDay = datetime.datetime.utcnow()):
	focusedDay = focusedDay.replace(hour=0, minute=0, second=0, microsecond=0)
	logger.info(str(focusedDay))
	resp = None
	async for session in get_session():
		resp = await session.execute(select(PushCreated).where(
			and_(PushCreated.pushTime > focusedDay,PushCreated.hasPushed == False)
		))
	if not resp:
		logger.info("this is true?")
		return
	results = resp.scalars().all()
	if results:

		result = results[0]
		logger.info(f"Result found: {result.pushTime}")
		if result.hasPushed: # type: ignore
			# move to the next day.
			return await handle_daily_push(focusedDay + datetime.timedelta(days=1))
		if datetime.datetime.now(datetime.timezone.utc).astimezone() > result.pushTime.astimezone(): # type: ignore
			await handle_daily_push_notification(int(result.pushID)) # pyright: ignore[reportArgumentType]
		else:
			# wait for it
			secondsTill = (result.pushTime.astimezone() - datetime.datetime.now(datetime.timezone.utc).astimezone()).total_seconds()
			logger.info(f"Waiting {secondsTill} till distributing the notification")
			while True:
				if datetime.datetime.now(datetime.timezone.utc).astimezone() > result.pushTime.astimezone(): # type: ignore
					logger.info("Breaking and executing daily push notification")
					break
				await asyncio.sleep(60)
			logger.info("Executing daily push notification")
			await handle_daily_push_notification(int(result.pushID)) # pyright: ignore[reportArgumentType]
		return
	else:
		logger.info(f"Generating time to push notification for: {focusedDay}")
		timetoSend = provideRandomTime(focusedDay)
		obj = PushCreated(pushTime=timetoSend, hasPushed=False)
		async for session in get_session():
			logger.info(f"Generated next time to push data: {timetoSend}")
			session.add(obj)
			await session.commit()
		return
	
async def daily_handler():
	# this just needs to run once per day via cronjob, and its sorted.
	try:
		focusedDay = None
		while True:
			resp = await handle_daily_push(focusedDay if focusedDay else datetime.datetime.utcnow())
			if resp:
				logger.info("Pushed Notification returned next day, quitting for cronjob to handle.")
				quit()
				# let cronjob handle the next day's push.
			await asyncio.sleep(3)
	except Exception as e:
		quit()



if __name__ == "__main__":
	try:
		asyncio.run(init_db())
		x = asyncio.run(daily_handler())
		logger.info(str(x))
		loop = asyncio.get_event_loop()
		loop.run_forever()
	except Exception as er:
		logger.info(str(er))
		quit()
