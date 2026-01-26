# FastAPI Backend Solution

This is made using SQLModel to use a ORM based database making it compatible with mysql, sqlite3 etc depending on how I want to host it in production

All my main routes are in /routes
main.py just hosts and merges it all into one working API

## Production

This is setup on /api route with an nginx reverse proxy to handle the incoming requests.

## FCM 

To handle push notifications, I have pushed this off to the "fcm_messaging.py" which handles all of the FCM related functions

## Authentication

I am using JWT tokens which I handle in "Authentication.py"
Implemented using Bearer, and added refresh tokens for users to automatically be able to refresh their tokens.

Their tokens last a long time, however are stored in backend and can be disabled if in the instance the Account is breaching terms or anything of that sort.
