"""
Diagnoser — LLM agent; outputs {"status": ..., "details": {...}}.
"""
from multiprocessing import Process, Queue
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI       # swap for ChatOllama etc.
from .tools import check_metrics
from .config import settings

SYSTEM_PROMPT = """
You are the Diagnoser in an MLOps pipeline.
1️⃣ Call check_metrics(ref,cur) first.
2️⃣ If dataset_drift == true → status = DRIFT
   Else if accuracy < 0.92   → status = REGRESSION
   Else → status = OK
Return ONLY JSON:
{"status":"OK|DRIFT|REGRESSION","details":{...}}
"""

llm = ChatOpenAI(model_name=settings.model_path, temperature=0.0)

diagnoser_agent = initialize_agent(
    tools=[check_metrics],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    system_message=SYSTEM_PROMPT,
    verbose=False,
)

class Diagnoser(Process):
    def __init__(self, in_q: Queue, out_q: Queue):
        super().__init__(daemon=True)
        self.in_q, self.out_q = in_q, out_q

    def run(self):
        while True:
            event = self.in_q.get()      # blocking
            diagnosis = diagnoser_agent.run(event)
            self.out_q.put(diagnosis)

