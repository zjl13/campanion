# AI Buddy Backend

FastAPI MVP backend for the "AI 搭子兼规划 App".

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

The API boots with a SQLite database by default and stores proof uploads under `storage/proofs/`.

## Main Capabilities

- `POST /api/v1/auth/dev-login`
- buddy profile creation
- calendar block CRUD
- goal creation with rules-based plan generation
- today task query
- task reschedule with supportive assistant reply
- proof upload and mock review
- chat messages and quick actions
- risk snapshot and overview stats

## Tests

```bash
pytest
```

