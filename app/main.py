from fastapi import FastAPI
from app.services.ingestion import create_complaint
from app.tasks import process_complaint_async

app = FastAPI(title="Complaint Agent API")

@app.post("/complaints")
async def receive_complaint(complaint: ComplaintCreate):
    db_complaint = create_complaint(complaint)
    process_complaint_async.delay(db_complaint.id)
    return {"id": db_complaint.id, "status": "received"}