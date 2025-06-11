"""
Entry-point: spawns Watcher → Diagnoser → Remediator.
Run:  python -m agent.orchestrator
"""
from multiprocessing import Queue
from .watcher import Watcher
from .diagnoser import Diagnoser
from .remediator import Remediator

def main():
    q12, q23 = Queue(), Queue()
    Watcher(out_q=q12).start()
    Diagnoser(in_q=q12, out_q=q23).start()
    Remediator(in_q=q23).start()

if __name__ == "__main__":
    main()

