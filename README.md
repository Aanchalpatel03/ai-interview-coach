# AI Interview Preparation Platform

Production-oriented monorepo for an AI-powered interview preparation SaaS with:

- `frontend`: Next.js 15 + Tailwind + Framer Motion + Recharts
- `backend`: FastAPI + PostgreSQL + JWT + WebSocket orchestration
- `ai-services/nlp`: question generation and answer scoring microservice
- `ai-services/vision`: posture and movement analysis microservice
- `ai-services/emotion`: confidence and nervousness estimation microservice
- `ml-services/*`: modular ML microservices for NLP, vision, emotion, and speech analysis
- `database`: PostgreSQL schema bootstrap
- `docker`: container build files

## Architecture

1. Users authenticate via JWT.
2. Resume upload stores a file reference and extracts skills.
3. Interview sessions are created in PostgreSQL.
4. Frontend streams answers and video analysis requests.
5. Backend brokers requests to NLP, vision, and emotion services.
6. Real-time feedback is pushed back through WebSocket.
7. Final aggregated feedback is stored and shown in the dashboard.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### AI services

```bash
cd ml-services/nlp-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8101
```

To train the NLP answer scorer with your own labeled dataset:

```bash
cd ml-services/nlp-service
..\..\.venv312\Scripts\python.exe train.py path\to\your-dataset.jsonl
```

Accepted dataset formats are `csv`, `json`, and `jsonl`. Required text fields are `question` and `answer`. Supported label columns are `score`, `communication_score`, `structure_score`, `relevance_score`, and `specificity_score`. A sample format is available at [`ai-services/nlp/dataset.template.jsonl`](/C:/Users/svedi/OneDrive/Desktop/Ai interview coach/ai-services/nlp/dataset.template.jsonl).

```bash
cd ml-services/vision-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8102
```

```bash
cd ml-services/emotion-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8103
```

```bash
cd ml-services/speech-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8104
```

### Docker

```bash
docker compose up --build
```

## Environment variables

Copy and adapt:

- [`backend/.env.example`](/C:/Users/svedi/IdeaProjects/Ai interview coach/backend/.env.example)
- [`frontend/.env.example`](/C:/Users/svedi/IdeaProjects/Ai interview coach/frontend/.env.example)

## Notes

- The CV and emotion services include deterministic starter heuristics and isolated service boundaries so you can replace them with trained models later.
- The NLP service now auto-loads a trained artifact from `ai-services/nlp/artifacts/answer_scoring_model.json` when present; otherwise it falls back to the original heuristic scorer.
- The backend uses `create_all` for bootstrap. Add Alembic for production migrations before launch.
- The backend now exposes `/api/ml/*` orchestration endpoints and `/api/ml/ws/ml-feedback?interview_id=<id>` for aggregated real-time ML feedback.
