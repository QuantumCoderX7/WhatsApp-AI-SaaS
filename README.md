# Enterprise Multi-Tenant WhatsApp AI Automation Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791.svg)](https://www.postgresql.org/)
[![Gemini API](https://img.shields.io/badge/Google%20Gemini-1.5%20%2F%202.0-8E75B2.svg)](https://ai.google.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-14%2B%20App%20Router-000000.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, production-ready multi-tenant B2B SaaS platform enabling businesses to connect their WhatsApp Business Cloud API with an autonomous Gemini-powered AI Agent capable of answering knowledge base questions, managing catalog inventory, placing orders, and handling human agent escalations.

---

## 📚 Master Engineering Specification
For full architectural blueprints, database DDLs, UML sequence diagrams, state machines, and engineering sprint roadmaps, refer to the master architecture document:
📄 **[Master Architecture Specification](docs/architecture_specification.md)**

---

## ✨ Key Platform Features

- 🏢 **Strict Multi-Tenancy**: Isolated products, inventory, vector chunks, orders, conversations, and usage limits per tenant using PostgreSQL Row-Level Security (RLS) and dynamic context binding.
- 🤖 **Gemini Function Calling**: Schema-validated tool execution for stock checking, inventory reservation, order creation, knowledge search, and human handoff.
- 📚 **Multi-Tenant RAG Pipeline**: File upload parsing (PDF/Docx/TXT), semantic recursive chunking, and 768-dimensional vector cosine distance search via `pgvector` (`text-embedding-004`).
- ⚡ **High-Volume Concurrency Protection**: Redis Distributed Locks (Redlock pattern) + PostgreSQL Optimistic Locking (`version` column) guarantee zero stock overselling during flash sales.
- 💬 **WhatsApp Webhook Engine**: Asynchronous Meta signature verification (HMAC-SHA256), `wamid` deduplication via Redis, and ARQ async worker processing.
- 🎛️ **Live Agent Dashboard**: Next.js 14 inbox UI allowing support teams to monitor AI conversations and toggle human agent takeover in real-time.

---

## 🛠️ Tech Stack

### Backend Infrastructure
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 16 + `pgvector` extension (Async SQLAlchemy 2.0 + Alembic)
- **Cache & Queue**: Upstash Redis + ARQ (Async Redis Queue)
- **AI / LLM Provider**: Google AI Studio (Gemini 1.5 / 2.0 Flash & Pro)
- **API Integration**: WhatsApp Cloud API (v18.0)

### Frontend Infrastructure
- **Framework**: Next.js 14+ (App Router, TypeScript)
- **Styling**: Tailwind CSS + `shadcn/ui`
- **State & Data Fetching**: TanStack Query v5, Zustand, React Hook Form + Zod

### Deployment & Infrastructure
- **Backend API & Workers**: Railway (Dockerized containers)
- **Frontend Dashboard**: Vercel Edge Serverless
- **Database & Storage**: Supabase Managed Postgres + Supabase Storage

---

## 📁 Repository Structure

```
.
├── docs/                             # Authoritative System Architecture Specification
│   └── architecture_specification.md
├── backend/                          # FastAPI Python Backend Service
│   ├── alembic/                      # Database Migration Scripts
│   ├── app/
│   │   ├── api/                      # REST API Endpoints & Dependencies
│   │   ├── core/                     # Configuration, Database Engine & Security
│   │   ├── domain/                   # DDD Bounded Contexts (Tenant, Conversation, AI, RAG, Inventory, Order)
│   │   └── workers/                  # ARQ Background Task Workers
│   ├── Dockerfile                    # Production Docker Container
│   └── requirements.txt              # Python Dependencies
├── docker-compose.yml                # Local Stack (API + Postgres/pgvector + Redis)
├── .env.example                      # Environment Variables Template
├── .gitignore                        # Git Version Control Ignore Definitions
└── README.md                         # Project Overview & Quickstart Guide
```

---

## 🚀 Quickstart Guide (Local Development)

### 1. Prerequisites
Ensure you have the following installed locally:
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)

### 2. Environment Setup
Clone the repository and copy the environment template:
```bash
git clone https://github.com/QuantumCoderX7/WhatsApp-AI-SaaS.git
cd WhatsApp-AI-SaaS
cp .env.example .env
```

### 3. Launch Local Stack with Docker Compose
Start PostgreSQL (with `pgvector`), Redis, and the FastAPI backend service:
```bash
docker-compose up -d --build
```
The services will be available at:
- **FastAPI Application**: `http://localhost:8000`
- **Swagger OpenAPI Documentation**: `http://localhost:8000/docs`
- **Health Check Endpoint**: `http://localhost:8000/api/v1/health`

### 4. Run Backend Manually (Optional)
If running without Docker for Python development:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run Database Migrations
alembic upgrade head

# Start Development Server
uvicorn app.main:app --reload --port 8000
```

---

## 🔐 API Routes Summary

| Method | Endpoint | Access | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Public | System Health & DB Connectivity Ping |
| `POST` | `/api/v1/auth/register` | Public | Register new Tenant Business & Admin Account |
| `POST` | `/api/v1/auth/login` | Public | Authenticate User and receive JWT Token |
| `GET` | `/api/v1/auth/me` | Bearer JWT | Retrieve active User Profile & Tenant Details |
| `GET` | `/api/v1/webhooks/whatsapp` | Meta Signature | Verification challenge for WhatsApp Cloud API |
| `POST` | `/api/v1/webhooks/whatsapp` | Meta Signature | Incoming WhatsApp Message & Event Stream Ingestion |

---

## 🗺️ Engineering Implementation Roadmap

- [x] **Sprint 1**: Base Architecture, Multi-Tenant DB Schemas, JWT Auth & Docker Scaffolding.
- [x] **Sprint 2**: WhatsApp Webhook Verification, Deduplication & Queue Ingestion.
- [x] **Sprint 3**: Gemini Function Calling Agent & Pydantic Tool Registry.
- [x] **Sprint 4**: Multi-Tenant Document Upload & RAG Retrieval Engine.
- [x] **Sprint 5**: Concurrency-Locked Inventory Control & Transactional Checkout.
- [x] **Sprint 6**: Next.js Dashboard Live Agent Inbox & Real-Time Controls.
- [ ] **Sprint 7**: Locust Load Testing, Security Audit & Production Deployment.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
