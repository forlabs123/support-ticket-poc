from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from poc.audit_logger import AuditLogger
from poc.models import TicketRequest, TicketResult
from poc.orchestrator import TicketOrchestrator

app = FastAPI(title="TicketFlow PoC API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

audit = AuditLogger(Path(__file__).parent / "data" / "audit.jsonl")
orchestrator = TicketOrchestrator(audit)


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_configured": orchestrator.llm.configured}


@app.post("/api/tickets/process", response_model=TicketResult)
def process_ticket(ticket: TicketRequest):
    return orchestrator.process(ticket.text, ticket.channel)


@app.get("/api/audit")
def audit_log(limit: int = Query(20, ge=1, le=100)):
    return {"items": audit.recent(limit)}

