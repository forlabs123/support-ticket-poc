import json
from pathlib import Path

from poc.audit_logger import AuditLogger
from poc.orchestrator import TicketOrchestrator


def main():
    orchestrator = TicketOrchestrator(AuditLogger(Path("poc/data/audit.jsonl")))
    examples = [
        ("Happy path", "Как отменить подписку? Больше не хочу ей пользоваться."),
        ("Risky path", "Мой аккаунт взломали и с карты украли деньги."),
    ]
    for title, text in examples:
        result = orchestrator.process(text, "demo")
        print(f"\n--- {title} ---")
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

