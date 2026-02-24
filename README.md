# Price Analyzer

REST API for tracking product price dynamics across multiple online stores.

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose

---

## Local setup

**1. Start infrastructure**

```bash
docker compose -f docker-compose.local.yml up -d
```

**2. Install dependencies**

```bash
uv sync
```

**3. Configure environment**

Set `DJANGO_SETTINGS_MODULE=config.settings.local` in your environment.

**4. Apply migrations**

```bash
uv run python manage.py migrate
```

**5. Run the server**

```bash
uv run python manage.py runserver
```

API is available at `http://localhost:8000/api/v1/`.  
Swagger UI: `http://localhost:8000/api/docs/`.

---

## Production setup

**1. Prepare environment**

```bash
cp .env.sample .env
```

Fill in all values in `.env`.

**2. Build and start**

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**3. Apply migrations**

```bash
docker compose -f docker-compose.prod.yml exec api uv run python manage.py migrate
```

**4. Create superuser**

```bash
docker compose -f docker-compose.prod.yml exec api uv run python manage.py createsuperuser
```
