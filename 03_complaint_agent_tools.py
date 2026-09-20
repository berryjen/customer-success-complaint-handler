import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

def create_ticket(complaint: str, category: str, urgency: int) -> str:
    """Log the complaint in the support system."""
    ticket_id = f"TICKET-{hash(complaint) % 100000:05d}"
    print(f"  [tool] create_ticket -> {ticket_id} (cat={category}, urgency={urgency})")
    return json.dumps({"ticket_id": ticket_id, "status": "open"})

def issue_refund(order_id: str, reason: str) -> str:
    """Issue a refund for an order."""
    print(f"  [tool] issue_refund -> order={order_id}")
    return json.dumps({"refunded": True, "order_id": order_id})

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Log a customer complaint as a support ticket. Call this for EVERY complaint.",
            "parameters": {
                "type": "object",
                "properties": {
                    "complaint": {"type": "string"},
                    "category": {"type": "string", "enum": ["refund", "shipping", "product_defect", "other"]},
                    "urgency": {"type": "integer"},
                },
                "required": ["complaint", "category", "urgency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue a refund. Only call when the customer explicitly asks for money back.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["order_id", "reason"],
            },
        },
    },
]

TOOL_FUNCTIONS = {"create_ticket": create_ticket, "issue_refund": issue_refund}

# ---------- 2. The agent loop ----------

SYSTEM_PROMPT = """You are a complaint-handling agent for a small online shop.
Workflow for every complaint:
1. Classify it (category + urgency 1-5) and call create_ticket.
2. If the customer explicitly demands money back, also call issue_refund
   (invent an order_id like "ORD-1234" if none is given).
3. Finally write a short, empathetic reply to the customer (max 3 sentences)
   telling them exactly what you did."""

def run_agent(complaint: str, max_steps: int = 5) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": complaint},
    ]
    for step in range(max_steps):  # safety cap so we can never loop forever
        resp = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
        )
        msg = resp.choices[0].message

        # No tool call => the model is done, this is the final reply.
        if not msg.tool_calls:
            return msg.content or "(no reply)"

        # Otherwise: record the model's tool request, execute it, feed result back.
        messages.append(msg)  # keep full assistant msg (tool_calls included)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"  [step {step}] Kimi wants: {call.function.name}({args})")
            result = TOOL_FUNCTIONS[call.function.name](**args)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
    return "(agent hit max steps)"

if __name__ == "__main__":
    demo = ("My order ORD-9876 arrived broken and I want a full refund "
            "immediately. Terrible experience!")
    print("Final reply to customer:\n")
    print(run_agent(demo))