FROM node:22-bookworm-slim AS lint-worker

WORKDIR /app/lint-worker
COPY lint-worker/package*.json ./
RUN npm ci
COPY lint-worker/ ./

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=lint-worker /usr/local/bin/node /usr/local/bin/node

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY --from=lint-worker /app/lint-worker/ ./lint-worker/
COPY . .

EXPOSE 8000
