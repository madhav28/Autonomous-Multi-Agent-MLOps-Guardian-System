from fastapi import FastAPI, BackgroundTasks
from agent.monitors import run_drift_check
from agent.config import settings
from pathlib import Path
import subprocess

app = FastAPI(title="MLOps Guardian API")

@app.post("/inspect/")
def inspect(ref: str, cur: str):
    """Manual drift check."""
    return run_drift_check(Path(ref), Path(cur))

@app.post("/action/")
def action(kind: str, bg: BackgroundTasks):
    """Manually trigger retrain or rollback."""
    if kind == "retrain":
        bg.add_task(subprocess.run, settings.retrain_command.split())
        return {"msg": "retraining kicked off"}
    if kind == "rollback":
        bg.add_task(subprocess.run, ["echo", "rollback placeholder"])
        return {"msg": "rollback kicked off"}
    return {"error": "unknown action"}

