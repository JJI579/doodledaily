import json
import firebase_admin
from firebase_admin import credentials, messaging
from pathlib import Path
import asyncio
from funcs import get_session

# database stuff
from sqlmodel import delete
from models import FCMToken

# Load service account
accountPath = Path('serviceAccountKey.json')
serviceInfo = json.load(open(accountPath.absolute()))
cred = credentials.Certificate(serviceInfo)
firebase_admin.initialize_app(cred)

async def dispatchNotification(tokens: list, text: str, urlSuffix: str="photos"):
	if not tokens:
		return

	message = messaging.MulticastMessage(
		tokens=tokens,
		webpush=messaging.WebpushConfig(
			headers={
				"Urgency": "high",
			},
			notification=messaging.WebpushNotification(
				title="Pib's Pics",
				body=text,
				icon="https://pibble.pics/pwa-192x192.png",
				badge="https://pibble.pics/pwa-64x64.png",
				require_interaction=True,
			),
			fcm_options=messaging.WebpushFCMOptions(
				link="https://pibble.pics"+'/'+("photos" if not urlSuffix else urlSuffix)
		)
		),
		
	)

	try:
		response = await messaging.send_each_for_multicast_async(message)
		failedTokens = [tokens[idx] for idx, r in enumerate(response.responses) if not r.success]
		
		# DELETE ALL FAILED TOKENS
		async for session in get_session():
			statement = delete(FCMToken).where(FCMToken.tokenID.in_(failedTokens))
			await session.execute(statement)
			await session.commit()
		
		print(f"Sent: {response.success_count}, Failed: {response.failure_count}")
		for idx, r in enumerate(response.responses):
			if not r.success:
				print(f"Token failed: {tokens[idx]}, Error: {r.exception}")
			else:
				print(f"Token sent: {tokens[idx]}")
	except Exception as e:
		print("Error sending message:", e)

# test the push
# from routes import auth

# tokens = asyncio.run(auth.fetchNotificationTokens(4))
# print(len(tokens))
# asyncio.run(dispatchNotification(tokens, "hello world"))