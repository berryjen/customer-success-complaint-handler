from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from enum import Enum as PyEnum

class Severity(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplaintStatus(PyEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True)
    source = Column(String)           
    raw_content = Column(String)      
    customer_email = Column(String)
    
   
    severity = Column(Enum(Severity))
    category = Column(String)         
    summary = Column(String)
    sentiment_score = Column(Integer) 
    
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.RECEIVED)
    ai_metadata = Column(JSON)       
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)