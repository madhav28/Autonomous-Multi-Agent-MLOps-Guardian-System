# MLOps Guardian Agent  
_Watcher → Diagnoser → Remediator_

A fully‑local, multi‑agent watchdog that keeps your ML model healthy:

| Stage        | Purpose                                                                                   |
|--------------|-------------------------------------------------------------------------------------------|
| **Watcher**  | Detect new evaluation logs in `data/logs/` and enqueue them                               |
| **Diagnoser**| Run **Evidently** + LLM reasoning to label each run **OK / DRIFT / REGRESSION**            |
| **Remediator**| Decide **retrain**, **rollback**, or **noop** and execute the action                     |

All three agents run as independent Python processes and talk through `multiprocessing.Queue`.
Swap the LLM backend (OpenAI, Ollama, llama‑cpp, etc.) without touching the control flow.

---

## Project layout

```
mlops-guardian-agent/
├── agent/              # all three agents + shared tools
│   ├── config.py
│   ├── monitors.py
│   ├── tools.py
│   ├── watcher.py
│   ├── diagnoser.py
│   ├── remediator.py
│   └── orchestrator.py   ← entry‑point
├── pipelines/
│   └── training_pipeline.py
├── app/                # FastAPI service
│   └── main.py
├── data/
│   ├── ref/            # ONE reference CSV goes here
│   └── logs/           # new eval logs appear here
├── models/             # latest.pkl etc.
├── tests/
│   └── test_guardian.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

---

## Quick‑start (local, with OpenAI API)

```bash
git clone https://github.com/yourname/mlops-guardian-agent.git
cd mlops-guardian-agent

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# --- configure ---
cp .env.example .env
# edit .env  → add your OPENAI_API_KEY

# --- seed reference data ---
mkdir -p data/ref
python - <<'PY'
import pandas as pd, pathlib
df = pd.DataFrame({"f1":[0,1], "label":[0,1]})
df.to_csv("data/ref/ref.csv", index=False)
PY

# --- launch agents (three processes) ---
python -m agent.orchestrator
```

Open a second terminal and create a new evaluation log:

```bash
source .venv/bin/activate
python pipelines/training_pipeline.py
```

You’ll see log lines from **Watcher → Diagnoser → Remediator** along with the chosen action.

---

## Offline / self‑hosted LLM

1. Install [Ollama](https://ollama.com/) and pull a model:

   ```bash
   ollama pull llama3
   ```

2. In `.env` set  
   `MODEL_PATH=ollama/llama3`

3. Replace the import in `agent/diagnoser.py`, `agent/remediator.py`, and `app/main.py`:

   ```python
   # from langchain.chat_models import ChatOpenAI
   # llm = ChatOpenAI(...)
   from langchain.chat_models import ChatOllama
   llm = ChatOllama(model="llama3")
   ```

Everything else stays the same—no internet required.

---

## REST API (optional)

```bash
uvicorn app.main:app --reload
```

| Method & path   | Body (JSON)                                  | Description                       |
|-----------------|----------------------------------------------|-----------------------------------|
| `POST /inspect/`| `{"ref":"path.csv","cur":"path.csv"}`         | Ad‑hoc drift check (Evidently)    |
| `POST /action/` | `{"kind":"retrain" \| "rollback"}`            | Manual override of Remediator     |

---

## Running tests

```bash
pytest
```

The smoke‑test simply imports the orchestrator and pipeline to verify dependencies.

---

## Docker

```bash
docker build -t guardian .
docker run -it -v $(pwd)/data:/app/data guardian
```

---

## Customizing

* **Drift / accuracy thresholds** — change `DRIFT_THRESHOLD` in `.env` and the `0.92` cutoff inside `agent/diagnoser.py`.
* **Retraining command** — set `RETRAIN_COMMAND` in `.env`.
* **Log format** — adapt `agent/monitors.py` for regression, NLP, etc.
* **Message bus** — swap `multiprocessing.Queue` for Redis, Kafka, or Prefect Orion to distribute across machines.

---