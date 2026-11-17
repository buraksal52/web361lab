# web361lab

Project documentation is in [docs/README.md](docs/README.md).

## Development

Frontend (Node.js and npm required):

```sh
cd frontend
npm install
npm run dev
```

Backend (Python required):

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL='postgresql+psycopg://web361lab:web361lab@localhost:5432/web361lab'
alembic upgrade head
python seed.py
uvicorn main:app --reload
```

Create the PostgreSQL database and a local development user first; the URL above is an example and must match your local setup. The seed contains fictional users only. Demo login lets anyone choose a listed identity and is intended for local demonstrations, not production deployment.

The API provides `GET /hello`. Run tests with `npm test` in `frontend/` and `pytest` in `backend/`. The API tests use an isolated in-memory database; PostgreSQL migrations must also be verified against a PostgreSQL instance.
