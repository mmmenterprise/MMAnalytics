# MMA Server
FastAPI backend for M&M RPro Analytics.

## Run locally
```bash
cd mma_server
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints
- `GET  /onboard/token`          → short-lived onboarding token
- `POST /onboard`                → create/update user, returns long-term Bearer token
- `POST /upload`                 → all data uploads (Authorization: Bearer <token>)
- `GET  /health`

## Environment
Set `DATABASE_URL`, `SECRET_KEY`, and `ENCRYPTION_KEY` in production (Render).
