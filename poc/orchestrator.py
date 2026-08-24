import time
from datetime import datetime, timezone
from uuid import uuid4

from poc.audit_logger import AuditLogger
from poc.classifiers import classify
from poc.knowledge_base import find_article
from poc.llm import AliceAIClient
from poc.models import Risk, TicketResult


class TicketOrchestrator:
    def __init__(self, logger: AuditLogger, llm: AliceAIClient | None = None):
        self.logger = logger
        self.llm = llm or AliceAIClient()

    def process(self, text: str, channel: str = "web") -> TicketResult:
        started = time.perf_counter()
        ticket_id = f"TKT-{uuid4().hex[:8].upper()}"
        classification = classify(text)
        article = find_article(classification.topic)
        routing_ms = (time.perf_counter() - started) * 1000

        result = {
            "ticket_id": ticket_id,
            "status": "escalated",
            "classification": classification,
            "answer": None,
            "knowledge_article": article["id"] if article else None,
            "answer_source": None,
            "operator_queue": "risk-review" if classification.risk == Risk.high else "general-support",
            "routing_ms": round(routing_ms, 2),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Автоответ разрешён только для известной темы с явно низким риском.
        if classification.risk == Risk.low and article:
            result.update(status="answered", answer=article["answer"], answer_source="knowledge_base", operator_queue=None)
            try:
                result["answer"] = self.llm.improve(text, article["answer"])
                result["answer_source"] = "aliceai_grounded"
            except Exception as exc:  # Fallback на проверенный KB-ответ — ожидаемая деградация.
                result["llm_fallback_reason"] = type(exc).__name__

        result["total_ms"] = round((time.perf_counter() - started) * 1000, 2)
        audit_event = {
            **result,
            "classification": classification.model_dump(),
            "channel": channel,
            "text_preview": text[:160],
        }
        self.logger.write(audit_event)
        result.pop("llm_fallback_reason", None)
        return TicketResult(**result)
