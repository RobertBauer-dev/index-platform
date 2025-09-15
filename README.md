# Index Platform - Solactive-like Indexing Solution

Eine modulare Indexing-Plattform für Finanzmarktdaten mit Backend (Python/FastAPI) und Frontend (React).

## Architektur

```
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── api/            # API Endpoints (REST + GraphQL)
│   │   ├── core/           # Core Configuration
│   │   ├── db/             # Database Models & Connection
│   │   ├── ingestion/      # Data Ingestion Modules
│   │   ├── processing/     # ETL/ELT Pipeline
│   │   ├── calculation/    # Index Calculation Engine
│   │   └── auth/           # Authentication
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React Components
│   │   ├── pages/          # Page Components
│   │   ├── services/       # API Services
│   │   └── utils/          # Utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Local Development
├── k8s/                    # Kubernetes Manifests
└── docs/                   # Documentation
```

## Features

- **Datenaufnahme**: CSV/JSON/API Datenquellen
- **Datenverarbeitung**: ETL/ELT Pipeline mit Bereinigung und Transformation
- **Index-Berechnung**: Equal Weight, Market Cap Weight, Custom Rules
- **API**: REST + GraphQL Endpoints
- **Frontend**: Dashboard, Index Builder, Performance Charts
- **Authentifizierung**: OAuth2/JWT
- **Deployment**: Docker + Kubernetes

## Quick Start

### Development Setup

1. **Backend**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend**:
```bash
cd frontend
npm install
npm start
```

### Docker Setup

```bash
docker-compose up -d
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- GraphQL Playground: http://localhost:8000/graphql

## Frontend

- Dashboard: http://localhost:3000
- Index Builder: http://localhost:3000/builder
