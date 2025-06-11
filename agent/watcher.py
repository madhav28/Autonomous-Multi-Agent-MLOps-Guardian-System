"""
Watcher — polls `data/logs/` for unseen CSVs and queues {ref,cur}.
"""
from multiprocessing import Process, Queue
from pathlib import Path
from .config import settings
import time, json

class Watcher(Process):
    def __init__(self, out_q: Queue):
        super().__init__(daemon=True)
        self.out_q = out_q
        self.ref = max(Path("data/ref").glob("*.csv"))

    def run(self):
        seen = set()
        while True:
            for cur in sorted(settings.data_dir.glob("*.csv")):
                if cur not in seen:
                    self.out_q.put(json.dumps({"ref": str(self.ref), "cur": str(cur)}))
                    seen.add(cur)
            time.sleep(5)

