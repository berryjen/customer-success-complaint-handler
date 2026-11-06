# complaint-agent — MVP

A beginner-friendly AI agent that handles customer complaints, built on the
Kimi API via the official OpenAI Python SDK (Kimi is OpenAI-compatible, so
only `base_url` + `model` change).

## Setup

```bash

python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade 'openai&gt;=1.0'
export GLM_API_KEY="sk-your-key-here"   # platform.kimi.ai -&gt; API keys
```

## Files (run in order)


## Architecture

complaint in -> LLM (classify) -> [optional: tools: ticket, refund] -> reply out
state: one `messages` list per complaint | storage: none yet (add SQLite when needed)
