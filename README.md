# complaint-agent — MVP

A beginner-friendly AI agent that handles customer complaints, built on the
Kimi API via the official OpenAI Python SDK (Kimi is OpenAI-compatible, so
only `base_url` + `model` change).

## Setup

```bash
# macOS note: the system command is python3; plain 'python' only exists inside a venv.
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade 'openai&gt;=1.0'
export MOONSHOT_API_KEY="sk-your-key-here"   # platform.kimi.ai -&gt; API keys
```

## Files (run in order)

| File | What it shows |
|---|---|
| `01_hello_kimi.py` | Bare-minimum API call |
| `02_complaint_agent_simple.py` | Agent = 1 prompt + JSON mode (true MVP) |
| `03_complaint_agent_tools.py` | Agent + tools = the classic tool-calling loop |

## Architecture

complaint in -> LLM (classify) -> [optional: tools: ticket, refund] -> reply out
state: one `messages` list per complaint | storage: none yet (add SQLite when needed)
