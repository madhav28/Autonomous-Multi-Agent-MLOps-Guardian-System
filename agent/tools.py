from langchain.tools import tool
from .monitors import run_drift_check
from .config import settings
from rich.console import Console
import subprocess, json, shutil

console = Console()

@tool("check_metrics", return_direct=True)
def check_metrics(payload: str) -> str:
    """Args (JSON): {"ref":"path.csv","cur":"path.csv"} → returns metrics JSON"""
    paths = json.loads(payload)
    res = run_drift_check(paths["ref"], paths["cur"])
    console.log(res)
    return json.dumps(res)

@tool("trigger_retrain", return_direct=True)
def trigger_retrain(_: str) -> str:
    """Launch local retraining. Blocking until finished."""
    console.log("[bold yellow]Retraining pipeline launched…[/]")
    proc = subprocess.run(
        settings.retrain_command.split(), capture_output=True, text=True
    )
    return proc.stdout + proc.stderr

@tool("rollback_model", return_direct=True)
def rollback_model(_: str) -> str:
    """Example rollback via MLflow (skips if MLflow missing)."""
    if shutil.which("mlflow"):
        subprocess.run(
            ["mlflow", "models", "deploy", "--model-uri", "models:/last-known-good"]
        )
        return "Rollback executed via MLflow."
    return "MLflow not installed — rollback skipped."

