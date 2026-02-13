# Cred Authentication API

FastAPI-powered authentication service following a lightweight MVC layering (router ➜ controller ➜ service ➜ repository). It exposes user registration and login routes, stores data in MySQL (via SQLAlchemy), secures passwords with bcrypt, and mints JWT access tokens.

## Features
- FastAPI 1.0 app structured with clear MVC-style layers
- User registration with strong validation (email/username uniqueness, password confirmation)
- Login using either username or email plus password, returning JWT bearer tokens
- Forgot-password flow with expiring tokens and SMTP email delivery
- SQLAlchemy models and Alembic-ready migrations targeting MySQL
- Pytest coverage for happy-path and failure-path auth flows
- Dockerfile and docker compose stack bundling the API and MySQL

## Getting Started
1. **Clone & install**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Environment variables**
   ```bash
   cp .env.example .env
  # edit secrets such as DATABASE_URL, JWT_SECRET_KEY, and SMTP_* values
   ```
3. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Interactive docs** live at http://127.0.0.1:8000/docs once the server is up.

## Running Tests
```bash
pytest
```

## Docker Workflow
```bash
docker compose up --build
```
The compose stack starts:
- `api`: FastAPI app served by Uvicorn
- `db`: MySQL 8 with persistence via the `db_data` volume

## Database Migrations
Generate a migration:
```bash
alembic revision --autogenerate -m "describe changes"
```
Apply migrations:
```bash
alembic upgrade head
```
Ensure `DATABASE_URL` is set before running Alembic commands.

## API Overview
- `POST /api/v1/auth/register`: Create a user
- `POST /api/v1/auth/login`: Exchange username/email + password for a bearer token
- `POST /api/v1/auth/forgot-password`: Request a reset token (always returns 202 to avoid account enumeration)
- `POST /api/v1/auth/reset-password`: Submit the token + new password to finish the reset

### Sample Registration Payload
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+15555550123",
  "contact": "email",
  "short_description": "Platform admin",
  "username": "janedoe",
  "password": "supersecret",
  "confirm_password": "supersecret"
}
```

### Sample Login Payload
```json
{
  "identifier": "janedoe",
  "password": "supersecret"
}
```

The login response returns:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Sample Forgot Password Payload
```json
{
  "identifier": "jane.doe@example.com"
}
```

### Sample Reset Password Payload
```json
{
  "token": "<token-from-email>",
  "new_password": "brandnewpass",
  "confirm_password": "brandnewpass"
}
```

To enable real SMTP delivery, set `SMTP_SUPPRESS_SEND=false` and configure the other `SMTP_*` values with your provider. By default emails are logged instead of sent, which keeps automated tests hermetic.

Feel free to adapt the layers (controllers, services, repositories) as your domain grows.
