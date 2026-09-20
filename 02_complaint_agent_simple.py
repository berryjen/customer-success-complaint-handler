import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

SYSTEM_PROMPT = """You are a customer-complaint triage agent for a small online shop.
Given a customer complaint, output STRICT JSON with exactly these keys:
- "category": one of "refund" | "shipping" | "product_defect" | "other"
- "urgency": 1-5 (5 = furious customer, refund demanded)
- "sentiment": one word
- "summary": one sentence summary
- "reply": a short, empathetic customer-facing reply (max 3 sentences)
Output JSON only. No markdown fences, no commentary."""

def handle_complaint(complaint: str) -> dict:
    resp = client.chat.completions.create(
        model="kimi-k3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": complaint},
        ],
        response_format={"type": "json_object"},  # JSON mode
        temperature=0.3,
    )
    return json.loads(resp.choices[0].message.content)

if __name__ == "__main__":
    demo = ("I ordered a coffee maker two weeks ago and it arrived completely "
            "cracked. This is unacceptable — I want my money back TODAY.")
    result = handle_complaint(demo)
    print(json.dumps(result, indent=2, ensure_ascii=False))