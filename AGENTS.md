# AGENTS.md — complaint-agent

MVP AI agent that handles customer complaints via the Kimi API,
using the official OpenAI Python SDK (Kimi is OpenAI-compatible).

## Stack & constraints
- Python 3.10+, only dependency: `openai&gt;=1.0`. Keep it that way for the MVP.
- Kimi base_url: `https://api.moonshot.ai/v1` (China: `https://api.moonshot.cn/v1`)
- Model: `kimi-k3`. Secrets come from `MOONSHOT_API_KEY` env var only.

## Architecture (do not over-engineer)
1. `01_hello_kimi.py` — minimal API call.
2. `02_complaint_agent_simple.py` — one LLM call, strict JSON out (JSON mode).
3. `03_complaint_agent_tools.py` — tool-calling loop (create_ticket, issue_refund),
   tools are MOCKED functions; loop capped at 5 steps.

All per-complaint state lives in one `messages` list. No databases, no vector
stores, no frameworks. Escalation rules are prompt instructions, not code.

## Working agreement for Pi
- Run the scripts before and after every change (venv activated):
  `python3 01_hello_kimi.py`, `02_...`, `03_...` (MOONSHOT_API_KEY must be set).
- Make the smallest change that works; no refactors unless asked.
- Tools in demo 03 stay mocked until real integrations (Stripe/Zendesk) are specced.