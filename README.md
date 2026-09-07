# Real Estate Platform Backend

A production-ready real estate platform backend built with FastAPI, SQLAlchemy, and PostgreSQL.

## Tech Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Pydantic v2
- Alembic
- Redis
- JWT Authentication
- Docker

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Run `docker-compose up -d`
4. Access API at `http://localhost:8000`
5. View docs at `http://localhost:8000/docs`

## Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
app/
├── core/          # Configuration, database, security
├── common/        # Shared utilities, exceptions, responses
├── modules/       # Business domain modules
├── workers/       # Background tasks
└── tests/         # Unit and integration tests
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
