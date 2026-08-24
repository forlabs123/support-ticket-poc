import re

from poc.models import Classification, Risk


TOPICS = {
    "refund": ("возврат", "вернуть деньги", "списали", "платеж", "оплат"),
    "security": ("взлом", "украли", "мошен", "чужой вход", "парол"),
    "account": ("аккаунт", "профиль", "войти", "логин", "регистрац"),
    "delivery": ("достав", "заказ", "курьер", "посыл"),
    "subscription": ("подписк", "отменить", "тариф", "пробный период"),
}

HIGH_RISK = {
    "possible_fraud": ("мошен", "украли", "взлом", "чужой вход"),
    "legal_threat": ("суд", "прокуратур", "роскомнадзор", "адвокат"),
    "health_or_safety": ("угрож", "опасност", "суицид", "покончить"),
    "sensitive_data": ("номер карты", "cvv", "паспорт", "пароль:"),
}

MEDIUM_RISK = {
    "money_dispute": ("списали", "деньги не вернулись", "двойное списание"),
    "angry_customer": ("жалоба", "обманули", "ужасный сервис"),
}


def _matches(text: str, vocabulary: tuple[str, ...]) -> bool:
    return any(token in text for token in vocabulary)


def classify(text: str) -> Classification:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    topic_scores = {
        topic: sum(token in normalized for token in tokens)
        for topic, tokens in TOPICS.items()
    }
    topic = max(topic_scores, key=topic_scores.get)
    score = topic_scores[topic]
    if score == 0:
        topic = "other"

    high_reasons = [name for name, words in HIGH_RISK.items() if _matches(normalized, words)]
    medium_reasons = [name for name, words in MEDIUM_RISK.items() if _matches(normalized, words)]
    if high_reasons:
        risk, reasons = Risk.high, high_reasons
    elif medium_reasons or topic == "other":
        risk = Risk.medium
        reasons = medium_reasons or ["unknown_topic"]
    else:
        risk, reasons = Risk.low, ["known_low_risk_intent"]

    confidence = 0.95 if high_reasons else (0.88 if score else 0.45)
    return Classification(topic=topic, risk=risk, reasons=reasons, confidence=confidence)

