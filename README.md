
# What is Pibble?

Pibble is Social Media Platform where you draw with your friends

# How to Setup?

## Configuration

### Frontend

Create .env in `_frontend` with configuration
```
VITE_ENVIRONMENT=dev
VITE_PROD_API_URL=https://YOUR-URL-HERE
```

dev means it API_URL will default to FastAPI localhost of 8000
Any other string defaults to your API_URL

## Environment

### Frontend
```
cd _frontend
npm i
```

### Backend
```
Create virtual environment for python (typically python -m venv venv)
~ activate environment

cd backend
pip install -r requirements.txt
```

---

Through doing commands above environment will be activated, with such you can either run via gunicorn or to run in dev environment

```
fastapi dev main.py
```


