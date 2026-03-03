# Clínica Go - Monorepo Infrastructure

This repository contains the full stack application for Clínica Go, structured as a monorepo with Dockerized environments for easy development and deployment.

## Project Structure

```
clinica_go/
├── back/               # Backend (FastAPI, Python)
│   ├── Dockerfile      # Multi-stage optimized Dockerfile
│   └── src/            # Application source code
├── frontend/           # Frontend (Next.js, React)
│   ├── Dockerfile      # Production-ready Dockerfile
│   └── src/            # Application components and pages
├── docker-compose.yml  # Root orchestration file
└── .env                # centralized configuration (optional, or use back/.env)
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (v4.32+)
- [Git](https://git-scm.com/)

## Quick Start (Docker)

To start the entire stack (Backend + Frontend + Databases + Tools):

```bash
docker compose up -d --build
```

### Services & Ports

| Service            | Host Name | Host Port | Internal Port | Description                     |
|--------------------|-----------|-----------|---------------|---------------------------------|
| **Frontend**       | `web`     | `3000`    | `3000`        | Next.js Web Interface           |
| **Backend API**    | `go`      | `3333`    | `3333`        | FastAPI REST API                |
| **WAHA Dashboard** | `waha`    | `3001`    | `3000`        | WhatsApp API Dashboard          |
| **PostgreSQL**     | `db`      | `15432`   | `5432`        | Database Access                 |
| **Redis**          | `rd`      | `6379`    | `6379`        | Cache & Queue                   |
| **Adminer**        | `adm`     | `8080`    | `8080`        | Database UI Management          |
| **MailDev**        | `md`      | `1080`    | `1080`        | Email Preview Tool              |
| **Worker**         | `wk`      | -         | -             | RQ Background Worker            |
| **Poller**         | `pwk`     | -         | -             | polling-worker                  |
| **Ops**            | `ops`     | -         | -             | Autoscaler                      |

**Note:** The WAHA service is mapped to host port `3001` to reserve `3000` for the Frontend.
**Naming Convention:** Short codes (`go`, `wk`, `rd`) are used for all container names as per project standards.

## Development Workflow

### Backend (`back/`)
- Code changes in `back/src` are NOT automatically hot-reloaded in the main compose setup unless you mount volumes (configured by default for `api`).
- To view logs: `docker compose logs -f api`

### Frontend (`frontend/`)
- The Docker setup currently runs a **production build** (`npm run build` -> `npm start`). 
- For active frontend development, it is recommended to run the frontend locally outside Docker while keeping backend in Docker:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
  (Ensure your `.env.local` points to `NEXT_PUBLIC_API_URL=http://localhost:3333/api/v1`)

## Troubleshooting

### Build Issues
If `npm ci` fails in the frontend build, ensure `frontend/package-lock.json` is consistent.
If backend build fails on PyTorch, ensure you have allocated enough memory to Docker (4GB+ recommended).

### Database Persistence
Data is persisted in named volumes: `db_data`, `redis_data`, `waha_data`, `chroma_data`.
To reset data: `docker compose down -v`.

