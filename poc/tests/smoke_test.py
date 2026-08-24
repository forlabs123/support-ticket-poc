from pathlib import Path

from poc.audit_logger import AuditLogger
from poc.models import Risk
from poc.orchestrator import TicketOrchestrator


class OfflineLLM:
    configured = False

    def improve(self, ticket_text, kb_answer):
        raise RuntimeError("offline")


def build_orchestrator(tmp_path: Path):
    return TicketOrchestrator(AuditLogger(tmp_path / "audit.jsonl"), OfflineLLM())


def test_happy_path_uses_safe_kb_fallback(tmp_path):
    result = build_orchestrator(tmp_path).process("Как отменить подписку?", "web")
    assert result.status == "answered"
    assert result.classification.risk == Risk.low
    assert result.answer_source == "knowledge_base"
    assert result.knowledge_article == "KB-101"
    assert result.routing_ms < 500


class WorkingAliceAI:
    configured = True

    def improve(self, ticket_text, kb_answer):
        return "Ответ, переформулированный Alice AI LLM"


def test_happy_path_marks_alice_ai_as_source(tmp_path):
    orchestrator = TicketOrchestrator(AuditLogger(tmp_path / "audit.jsonl"), WorkingAliceAI())
    result = orchestrator.process("Как отменить подписку?", "web")
    assert result.status == "answered"
    assert result.answer_source == "aliceai_grounded"


def test_risky_path_escalates_without_answer(tmp_path):
    result = build_orchestrator(tmp_path).process("Мой аккаунт взломали и украли деньги", "chat")
    assert result.status == "escalated"
    assert result.classification.risk == Risk.high
    assert result.answer is None
    assert result.operator_queue == "risk-review"


def test_unknown_topic_is_not_auto_answered(tmp_path):
    result = build_orchestrator(tmp_path).process("У меня необычная ситуация", "email")
    assert result.status == "escalated"
    assert result.classification.risk == Risk.medium
