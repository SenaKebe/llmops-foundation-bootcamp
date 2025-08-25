from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from enum import Enum
import time

from src.feedback_collector import FeedbackCollector
from src.monitoring import ChatbotMonitor

# ------------------------------------------------------
# Enums for Swagger Dropdowns
# ------------------------------------------------------
class FeedbackType(str, Enum):
    bug_report = "bug_report"
    feature_request = "feature_request"
    general_feedback = "general_feedback"
    incorrect_response = "incorrect_response"

# ------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------
class FeedbackRequest(BaseModel):
    user_id: str
    feedback_type: FeedbackType   # 👈 Dropdown in Swagger
    description: str
    metadata: Optional[Dict[str, Any]] = None

class LogRequest(BaseModel):
    user_id: str
    query: str
    response: str
    error: Optional[str] = None

# ------------------------------------------------------
# Initialize app and classes
# ------------------------------------------------------
app = FastAPI(title="Chatbot Feedback & Monitoring API")
collector = FeedbackCollector()
monitor = ChatbotMonitor()

# ------------------------------------------------------
# Feedback Endpoints
# ------------------------------------------------------
@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    try:
        feedback = collector.collect_feedback(
            request.user_id,
            request.feedback_type.value,   # 👈 store as string
            request.description,
            request.metadata
        )
        return {"status": "success", "feedback": feedback}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/feedback", response_model=List[Dict[str, Any]])
def list_feedback(feedback_type: Optional[FeedbackType] = None):
    return collector.get_feedback(feedback_type.value if feedback_type else None)

# ------------------------------------------------------
# Monitoring Endpoints
# ------------------------------------------------------
@app.post("/monitor/log")
def log_response(request: LogRequest):
    start_time = time.time()
    log = monitor.log_response(
        request.user_id,
        request.query,
        request.response,
        start_time,
        request.error
    )
    return {"status": "logged", "log": log}
