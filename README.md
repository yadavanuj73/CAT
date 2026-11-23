# CAT Intelligence 2026

Specialised AI-powered CAT 2026 examination intelligence platform with authentic historical pattern analysis, recency-weighted prediction models, independent question verification, and session-first BYOK privacy.

---

## Key Priorities

1. **Analytical Accuracy**: Historical question analysis with provenance (CAT 2000–2025).
2. **Prediction Quality**: Calibrated statistical confidence (bounded at 89%), with limitations disclosed.
3. **Mathematical Correctness**: Independent deterministic verification of equations and arithmetic statements.
4. **Answer Verification**: Multi-stage validation of answer options, MCQ/TITA formats, and detailed solutions.
5. **API Credential Security**: Backend-only Session-First Bring Your Own Key (BYOK). Keys reside in ephemeral RAM, never persisted to disk or exposed to client JavaScript.
6. **Minimal UI**: Clean, light-theme interface with zero clutter, subtle borders, and accessible typography.

---

## Technology Stack

- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS v4, Lucide Icons, Recharts, TanStack Query.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, PyMuPDF, Pytesseract OCR, slowapi.
- **Database**: PostgreSQL (Supabase) with Row Level Security (RLS) & UUID primary keys; SQLite (aiosqlite) for local development/testing.
- **Security & Encryption**: Cryptography AES-256-GCM, PyJWT (HS256), bcrypt, thread-safe memory session key store.
- **Deployment**: Vercel (Frontend), Render (Backend).

---

## System Architecture

```
d:\Cat 2026\
├── backend/
│   ├── alembic/                    # Database migrations
│   │   └── versions/001_initial_schema.py
│   ├── app/
│   │   ├── config.py               # Pydantic BaseSettings
│   │   ├── database.py             # Async SQLAlchemy engine (PG/SQLite)
│   │   ├── main.py                 # FastAPI application & secret-redaction middleware
│   │   ├── models/                 # SQLAlchemy 2.0 ORM models
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── paper.py
│   │   │   ├── question.py
│   │   │   ├── topic.py
│   │   │   ├── analysis.py
│   │   │   ├── prediction.py
│   │   │   ├── mock_exam.py
│   │   │   └── audit.py
│   │   ├── schemas/                # Pydantic v2 request/response models
│   │   ├── security/               # AES-256-GCM, RAM Session Store, CSRF, Redaction
│   │   ├── services/               # Ingestion, OCR, Extraction, Verification, Analysis, Predictions, Mock Gen
│   │   ├── utils/                  # Deterministic math solver, PDF parsing
│   │   └── routers/                # auth, keys, papers, questions, analysis, predictions, mocks
│   ├── tests/                      # 20 Automated test suites covering auth, crypto, verification, security
│   ├── sql/rls_policies.sql        # Supabase Row Level Security definitions
│   ├── Dockerfile                  # Container definition with Tesseract OCR
│   ├── render.yaml                 # Render Infrastructure-as-Code specification
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/layout/      # Navbar, Sidebar, Main Layout
│   │   ├── components/ui/          # Card, Table, Modal, Button, Alert, Badges
│   │   ├── hooks/                  # useAuth, usePapers, useAnalysis, usePredictions, useMockExams
│   │   ├── pages/                  # Dashboard, UploadPapers, PaperAnalysis, Predictions, MockTests, Settings
│   │   ├── services/api.ts         # Axios client with JWT & error interceptors
│   │   ├── types/index.ts          # TypeScript interfaces
│   │   └── App.tsx                 # React Router v7 & Protected Route configuration
│   ├── vercel.json                 # Vercel deployment rewrites
│   └── package.json                # React 19 dependencies
└── docs/                           # Architecture, security & deployment guides
```

---

## Session-First BYOK Security Model

### Default Mode: Session-Only API Key
1. User provides OpenAI API key over HTTPS.
2. Key is received directly by the backend and stored **only in volatile server-side memory (RAM)**.
3. Key is never saved to PostgreSQL, Redis, cookies, localStorage, or error logs.
4. Key is expunged immediately when:
   - User logs out (`POST /api/auth/logout`)
   - User clicks "Purge Credential" (`DELETE /api/keys`)
   - Session expires (default: 120 minutes)
   - Render server instance restarts

### Optional Mode: AES-256-GCM Encrypted Persistence
- User must explicitly opt-in.
- Key is encrypted with authenticated AES-256-GCM using `MASTER_ENCRYPTION_KEY`.
- Stored as ciphertext, 12-byte IV, and 16-byte authentication tag in `encrypted_credentials`.

---

## Verification Pipeline

Before any question enters the trusted historical dataset or is served in a mock exam:
1. **Mathematical Verification**: Equations and arithmetic are checked for deterministic validity.
2. **Option Consistency**: MCQs are verified to have 4 distinct, non-duplicate choices.
3. **Ambiguity Check**: Unclear questions or incomplete text fragments are rejected or flagged as `needs_review`.
4. **Audit Trail**: Every check generates an immutable `verification_records` row.

---

## Automated Test Suite

Run the full pytest suite (20 tests covering authentication, crypto, verification, analysis, and security acceptance):

```bash
cd backend
$env:PYTHONPATH="."
pytest tests -v
```

Build the frontend bundle:

```bash
cd frontend
npm run build
```

---

## Local Development Setup

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API interactive documentation available at: `http://localhost:8000/docs`

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend development server available at: `http://localhost:5173`
