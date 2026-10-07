from llm import chat_json, Budget
from models import Extraction

b = Budget(20000)
print(chat_json(Extraction, "Extract meeting outcomes.",
                "Priya: I'll send the Q3 report to Rahul by Friday.", budget=b))
print("tokens:", b.used)
