# CI Demo API

A small REST service for managing articles and user accounts, built with FastAPI, SQLAlchemy and PostgreSQL.

Based on [fastapi-sqlalchemy-postgres-template](https://github.com/mdhishaamakhtar/fastapi-sqlalchemy-postgres-template) by mdhishaamakhtar, and modified from the original. Licensed under GPLv3; see [LICENSE](LICENSE).

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Health check |
| POST | `/articles` | Create an article |
| GET | `/articles` | List all articles |
| GET | `/articles/{article_id}` | Read one article |
| PATCH | `/articles/{article_id}` | Edit an article |
| DELETE | `/articles/{article_id}` | Delete an article |
| POST | `/users` | Create a user account |
| GET | `/users` | List all users |
| GET | `/users/{user_id}` | Read one user |
| PATCH | `/users/{user_id}` | Edit a user (send only the fields to change) |
| DELETE | `/users/{user_id}` | Delete a user |

Passwords are stored as salted scrypt hashes and are never returned. The API has no login yet, so these endpoints are open to anyone who can reach it.

Interactive docs are at `/docs` and `/redoc` while the server is running.

## Run with Docker

1. Create your settings file, then set `POSTGRES_PASSWORD` in it:

   ```bash
   cp .env.example .env
   ```

2. Start the API and database:

   ```bash
   docker compose up --build
   ```

3. Open <http://127.0.0.1:8000/docs>.

Compose refuses to start without the `POSTGRES_*` values, and builds the API's `DATABASE_URL` from them.

## Run without Docker

You need Python 3.10+ and a running PostgreSQL server.

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` from `.env.example` and set `DATABASE_URL` to your own database:

   ```env
   DATABASE_URL=postgresql://admin:<password>@localhost:5432/demo_db
   ```

4. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

## Development

```bash
pytest         # uses a local SQLite file unless DATABASE_URL is set in your shell
black .        # format the code
```

## CI/CD

GitHub Actions runs these workflows from `.github/workflows/`:

| Workflow | Runs on | What it does |
| --- | --- | --- |
| `tests.yml` | Pull requests and pushes to other branches | Checks formatting, then runs unit and integration tests against PostgreSQL |
| `docker.yml` | Pushes to `main` or `master` | Runs `tests.yml`, then publishes a Docker image to `ghcr.io` if the tests pass |
| `linter.yml` | Pushes and pull requests on `master` | Runs Super-Linter |
| `commit.yml` | Pushes and pull requests on `master` | Checks commit message format |

Dependabot (`.github/dependabot.yml`) opens weekly pull requests for package, action and base image updates.
