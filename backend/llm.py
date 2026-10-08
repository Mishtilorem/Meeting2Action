import os, json, time
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from pydantic import ValidationError

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

FAST = "openai/gpt-oss-20b"
SMART = "openai/gpt-oss-120b"  

class Budget:
    def __init__(self, limit):
        self.limit, self.used = limit, 0
    def spend(self, n):
        self.used += n
        if self.used > self.limit:
            raise RuntimeError(f"Token budget exceeded ({self.used}/{self.limit})")

def _call(messages, model, budget, retries=5):
    delay = 2
    for _ in range(retries):
        try:
            r = client.chat.completions.create(
                model=model, messages=messages, temperature=0,
                response_format={"type": "json_object"},
            )
            if budget:
                budget.spend(r.usage.total_tokens)
            return r.choices[0].message.content
        except RateLimitError:
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("Rate limited too many times")

def chat_json(schema, system, user, model=FAST, budget=None):
    sys_prompt = f"{system}\nReturn only JSON matching this schema:\n{json.dumps(schema.model_json_schema())}"
    messages = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user}]
    for _ in range(2):  # one validation retry
        raw = _call(messages, model, budget)
        try:
            return schema.model_validate_json(raw)
        except ValidationError as e:
            messages += [{"role": "assistant", "content": raw},
                         {"role": "user", "content": f"Invalid: {e}. Return corrected JSON only."}]
    raise ValueError("Model output failed validation twice")
