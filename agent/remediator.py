"""
Remediator — decides retrain / rollback / noop.
"""
from multiprocessing import Process, Queue
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from .tools import trigger_retrain, rollback_model
from .config import settings

SYSTEM_PROMPT = """
You are the Remediator. Input is Diagnoser JSON.
• If status=="DRIFT"       → call rollback_model
• If status=="REGRESSION"  → call trigger_retrain
• If status=="OK"          → reply "noop"
Answer in plain English stating what you did.
"""

llm = ChatOpenAI(model_name=settings.model_path, temperature=0.0)

remediator_agent = initialize_agent(
    tools=[trigger_retrain, rollback_model],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    system_message=SYSTEM_PROMPT,
    verbose=True,
)

class Remediator(Process):
    def __init__(self, in_q: Queue):
        super().__init__(daemon=True)
        self.in_q = in_q

    def run(self):
        while True:
            diagnosis = self.in_q.get()
            print(remediator_agent.run(diagnosis))

