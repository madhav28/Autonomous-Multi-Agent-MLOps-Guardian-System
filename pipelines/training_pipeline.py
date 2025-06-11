"""
Toy retraining script — swap with your real pipeline.
Generates a new accuracy log CSV in data/logs/.
"""
from pathlib import Path
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd, joblib, datetime as dt, random

def main():
    X, y = load_iris(return_X_y=True, as_frame=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier().fit(Xtr, ytr)
    acc = clf.score(Xte, yte)

    Path("models").mkdir(exist_ok=True, parents=True)
    joblib.dump(clf, "models/latest.pkl")

    Path("data/logs").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "timestamp": [dt.datetime.utcnow()],
            "accuracy": [acc + random.uniform(-0.05, 0.05)],  # jitter for demo
        }
    ).to_csv(f"data/logs/{int(dt.datetime.utcnow().timestamp())}.csv", index=False)

    print(f"Retraining finished. Accuracy={acc:.3f}")

if __name__ == "__main__":
    main()

