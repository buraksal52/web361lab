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
uvicorn main:app --reload
```

The API provides `GET /hello`. Run tests with `npm test` in `frontend/` and `pytest` in `backend/`.
