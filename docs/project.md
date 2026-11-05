This project is a beginner level AI project that encorporates the use of an LLM to sort incoming customer complaints according to severity.
The following is a proposed architecutural design template for this project. 

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Complaint     │────▶│   API Server     │────▶│   AI Engine     │
│   Sources       │     │   (FastAPI)      │     │   (GLM) │
│   (Email, Form, │     │                  │     │                 │
│    Webhook)     │     │  - Validate      │     │  - Classify     │
└─────────────────┘     │  - Queue Job     │     │  - Extract      │
                        │  - Store Raw     │     │  - Summarize    │
                        └──────────────────┘     └─────────────────┘
                                  │                         │
                                  ▼                         ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │   Task Queue     │◄────│   Action Engine │
                        │   (Celery/Redis) │     │   (Rules)       │
                        └──────────────────┘     │  - Escalate?    │
                                  │               │  - Auto-reply?  │
                                  ▼               │  - Notify?      │
                        ┌──────────────────┐     └─────────────────┘
                        │   Database       │              │
                        │   (SQLite/PSQL)  │              ▼
                        │  - complaints    │     ┌─────────────────┐
                        │  - actions_log   │     │   Notifications   │
                        └──────────────────┘     │   (Slack/Email)   │
                                                 └─────────────────┘
```