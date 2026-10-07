import os
from llm import Budget
from extraction import extract

sample_transcript = """
Priya: Welcome everyone. Let's discuss the product roadmap for Q4.
Rahul: I will prepare the financial forecast slides by next Friday.
Priya: Great. Also, Alex, can you review the security audit document by Wednesday?
Alex: Sure, I'll review the security audit document by Wednesday.
Priya: Perfect. Let's make sure we launch the beta by end of month.
"""

if __name__ == "__main__":
    if os.path.exists("t.txt"):
        with open("t.txt", "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sample_transcript

    b = Budget(60000)
    res = extract(text, b)
    print("Extracted Results:")
    print(res.model_dump_json(indent=2))
    print(f"Tokens used: {b.used}")
