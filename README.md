# Email Triage OpenEnv

An **OpenEnv-compatible** evaluation environment for benchmarking LLM-based email-triage agents.

Agents classify **30 realistic fake emails** across two axes:

| Axis | Values |
|------|--------|
| **Priority** | `urgent` · `normal` · `low` |
| **Category** | `billing` · `support` · `spam` · `inquiry` |

---

## Project Structure

```
email-triage-env/
├── env/
│   ├── __init__.py          # package exports
│   ├── models.py            # Pydantic types: Email, Label, TriageResult
│   ├── tasks.py             # 30 annotated fake emails + EmailTriageTask
│   ├── graders.py           # scoring functions (exact-match, partial credit)
│   └── environment.py       # OpenEnv-style EmailTriageEnvironment
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI REST service
├── inference.py             # stand-alone agent runner (rule-based or LLM)
├── openenv.yaml             # OpenEnv configuration manifest
├── Dockerfile               # container definition
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Quick Start

### 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### 2 — Run the rule-based baseline (no API key needed)

```bash
python inference.py --mode rule_based
```

### 3 — Run with GPT-4o

```bash
export OPENAI_API_KEY=sk-...
python inference.py --mode llm --model gpt-4o
```

### 4 — Start the REST API server

```bash
uvicorn api.main:app --reload --port 8000
```

Interactive docs: **http://localhost:8000/docs**

### 5 — Docker (optional)

```bash
docker build -t email-triage-env .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... email-triage-env
```

---

## REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/emails` | List all 30 task emails |
| GET | `/emails/{email_id}` | Get one email by ID |
| POST | `/triage` | Submit a triage prediction |
| GET | `/metrics` | Episode aggregate metrics |
| POST | `/reset` | Reset environment |

### Example: submit a prediction

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"email_id":"email_01","priority":"urgent","category":"billing"}'
```

---

## Scoring

| Outcome | Score |
|---------|-------|
| Both priority **and** category correct | **1.0** |
| Only one axis correct | **0.5** |
| Neither correct | **0.0** |

Maximum episode score: **30.0**

---

## Dataset Distribution

| Priority | Count | Category | Count |
|----------|-------|----------|-------|
| urgent | 9 | billing | 7 |
| normal | 13 | support | 7 |
| low | 8 | spam | 6 |
| | | inquiry | 10 |

---

## License

MIT
