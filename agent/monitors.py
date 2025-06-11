from evidently.report import Report
from evidently.metrics import DataDriftPreset, ClassificationPerformancePreset
import pandas as pd
from pathlib import Path
from .config import settings

def run_drift_check(ref_csv: Path, cur_csv: Path) -> dict:
    ref = pd.read_csv(ref_csv)
    cur = pd.read_csv(cur_csv)

    report = Report(metrics=[DataDriftPreset(), ClassificationPerformancePreset()])
    report.run(reference_data=ref, current_data=cur)
    res = report.as_dict()

    drift_flag = res["metrics"][0]["result"]["dataset_drift"]
    accuracy = res["metrics"][1]["result"]["accuracy"]

    return {
        "dataset_drift": drift_flag,
        "accuracy": accuracy,
        "passed": (not drift_flag) and (accuracy >= 0.92),
    }

