# app/services/classifier.py
import openai
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    severity: str
    category: str
    summary: str
    sentiment_score: int
    suggested_action: str  # "auto_reply", "escalate", "review"

async def classify_complaint(text: str) -> ClassificationResult:
    prompt = f"""
    You are a customer support triage assistant. Analyze this complaint:
    
    COMPLAINT: {text}
    
    Respond in JSON with these keys:
    - severity: one of [low, medium, high, critical]
    - category: one of [billing, technical, account, feature_request, other]
    - summary: max 20 words
    - sentiment_score: 1-10 (10=very angry)
    - suggested_action: one of [auto_reply, escalate, review]
    """
    
    response = await openai.chat.completions.create(
        model="kimi-k2.6",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return ClassificationResult.model_validate_json(
        response.choices[0].message.content
    )