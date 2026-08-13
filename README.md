# Digital Trophy MVP

**Online service for digital measurement of hunting trophies from 3D models**
*Method 6 — Carnivores*

Digital Trophy is a web application that enables hunters, measurers, and experts to upload 3D models of hunting trophies, perform calibrated length and width measurements using a two-point calibration mode, and generate certified PDF reports — all within a role-based, auditable workflow.

---

## Features

- **Trophy Management** — Full CRUD for hunting trophy records
- **STL Upload** — Validate and store 3D model files (up to 500 MB)
- **3D Calibration** — Two-point calibration mode for accurate real-world scale
- **Longitudinal Axis Definition** — Define the trophy's primary axis
- **Length & Width Measurements** — Record and version measurement data
- **Measurement Versioning** — Track changes with a history of measurement versions
- **Expert Review Workflow** — Submit, review, and approve measurement results
- **PDF Export** — Generate measurement certificates as PDF documents
- **JWT Authentication** — Secure login with access and refresh tokens
- **Role-Based Access Control (RBAC)** — Four roles: `USER`, `MEASURER`, `EXPERT`, `ADMIN`
- **Audit Logging** — Every significant action is recorded with timestamp, actor, and details

---

## Tech Stack

| Layer       | Technology                                           |
| ----------- | ---------------------------------------------------- |
| Backend     | Python 3.12 · FastAPI · SQLAlchemy (async)           |
| Database    | PostgreSQL 16                                        |
| Migrations  | Alembic                                              |
| 3D Handling | `stl` / `numpy`                                      |
| PDF Gen     | ReportLab                                            |
| Auth        | python-jose (JWT) · Passlib                          |
| Frontend    | Three.js · Tailwind CSS · Jinja2 templates           |
| Deployment  | Docker · docker-compose                              |

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd MVP
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and other settings (see **Environment Variables** below).

### 5. Start the application

Choose either the Docker or manual approach described below.

---

## Quick Start (Docker)

The simplest way to run the full stack:

```bash
docker compose up
```

This starts:
- **PostgreSQL 16** with a health check on `localhost:5432`
- **FastAPI** application on `localhost:8000`

Database migrations are applied automatically on startup.

---

## Quick Start (Manual)

Ensure PostgreSQL is running and your `DATABASE_URL` is correct, then:

```bash
# Apply database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API Documentation

Interactive API documentation is available after the server is running:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **Health check:** http://localhost:8000/api/health

---

## API Endpoints

### Authentication

| Method   | Endpoint                          | Description           |
| -------- | --------------------------------- | --------------------- |
| `POST`   | `/api/v1/auth/register`           | Register a new user   |
| `POST`   | `/api/v1/auth/login`              | Login (returns JWT)   |
| `GET`    | `/api/v1/auth/me`                 | Get current user info |

### Trophies

| Method   | Endpoint                          | Description              |
| -------- | --------------------------------- | ------------------------ |
| `GET`    | `/api/v1/trophies`                | List trophies             |
| `POST`   | `/api/v1/trophies`                | Create a trophy           |
| `GET`    | `/api/v1/trophies/{id}`           | Get trophy details        |
| `PUT`    | `/api/v1/trophies/{id}`           | Update a trophy           |
| `DELETE` | `/api/v1/trophies/{id}`           | Delete a trophy           |

### File Upload

| Method   | Endpoint                                | Description             |
| -------- | --------------------------------------- | ----------------------- |
| `POST`   | `/api/v1/trophies/{id}/model/upload`    | Upload STL model file   |

### Calibration

| Method   | Endpoint                                | Description              |
| -------- | --------------------------------------- | ------------------------ |
| `POST`   | `/api/v1/trophies/{id}/calibration`     | Define two-point calibration |

### Measurements

| Method   | Endpoint                                | Description              |
| -------- | --------------------------------------- | ------------------------ |
| `POST`   | `/api/v1/trophies/{id}/measurements`    | Record a measurement     |

### Review

| Method   | Endpoint                                | Description              |
| -------- | --------------------------------------- | ------------------------ |
| `POST`   | `/api/v1/trophies/{id}/review`          | Submit for expert review |

### PDF Export

| Method   | Endpoint                                | Description              |
| -------- | --------------------------------------- | ------------------------ |
| `GET`    | `/api/v1/trophies/{id}/pdf`             | Download PDF certificate |

### Audit

| Method   | Endpoint                            | Description              |
| -------- | ----------------------------------- | ------------------------ |
| `GET`    | `/api/v1/audit/logs`                | Retrieve audit logs      |

---

## Project Structure

```
MVP/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings from .env
│   ├── database.py             # Async engine & session
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── auth.py         # Register, login, current user
│   │       ├── trophies.py    # Trophy CRUD
│   │       ├── upload.py       # STL file upload
│   │       ├── calibration.py  # Two-point calibration
│   │       ├── measurements.py # Measurement creation
│   │       ├── review.py       # Expert review workflow
│   │       ├── pdf.py          # PDF report generation
│   │       └── audit.py        # Audit log retrieval
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mixins.py           # Base model mixin
│   │   ├── user.py             # User + RBAC roles
│   │   ├── trophy.py           # Trophy record
│   │   ├── calibration.py      # Calibration data
│   │   ├── measurement.py      # Measurements & versions
│   │   └── session.py          # Audit log
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic user schemas
│   │   ├── trophy.py           # Pydantic trophy schemas
│   │   └── measurement.py      # Pydantic measurement schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audit_logger.py     # Audit logging utility
│   │   ├── file_validator.py   # STL file validation
│   │   ├── pdf_generator.py    # ReportLab PDF builder
│   │   └── init_db.py          # Database seed / initial setup
│   ├── core/
│   │   └── auth.py             # JWT helpers, password hashing
│   ├── static/
│   │   └── js/
│   │       └── app.js          # Three.js client-side logic
│   └── templates/
│       └── index.html          # Frontend template
├── tests/
│   └── __init__.py
└── uploads/                    # Uploaded STL files
```

---

## Environment Variables

| Variable                  | Default                                          | Description                            |
| ------------------------- | ------------------------------------------------ | -------------------------------------- |
| `APP_NAME`                | `Digital Trophy MVP`                             | Application name                       |
| `APP_VERSION`             | `0.1.0`                                          | Application version                    |
| `DEBUG`                   | `true`                                           | Enable debug mode                      |
| `HOST`                    | `0.0.0.0`                                        | Bind host                              |
| `PORT`                    | `8000`                                           | Bind port                              |
| `DATABASE_URL`            | `postgresql+asyncpg://trophy_user:trophy_pass@localhost:5432/trophy_db` | Async PostgreSQL connection string     |
| `JWT_SECRET_KEY`          | *(change in production)*                         | Secret key for JWT signing             |
| `JWT_ALGORITHM`           | `HS256`                                          | JWT signing algorithm                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                         | Access token lifetime                  |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                                          | Refresh token lifetime               |
| `MAX_FILE_SIZE_MB`        | `500`                                            | Maximum uploaded file size (MB)        |
| `UPLOAD_DIR`              | `/app/uploads`                                   | Directory for uploaded STL files       |
| `ALLOWED_ORIGINS`         | `["http://localhost:8000"]`                      | CORS allowed origins (JSON array)      |

---

## License

This project is licensed under the [MIT License](LICENSE).
