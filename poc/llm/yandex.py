import os

import httpx


class AliceAIClient:
    endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY_GPT", "")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID", "")
        self.model = os.getenv("YANDEX_MODEL", "aliceai-llm")
        self.timeout = float(os.getenv("YANDEX_TIMEOUT_SECONDS", "12"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.folder_id)

    def improve(self, ticket_text: str, kb_answer: str) -> str:
        if not self.configured:
            raise RuntimeError("Alice AI LLM is not configured")

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": "350"},
            "messages": [
                {
                    "role": "system",
                    "text": (
                        "Ты ассистент поддержки. Переформулируй только данный ответ базы знаний "
                        "доброжелательно и кратко. Не придумывай факты, компенсации, сроки или ссылки. "
                        "Не повторяй персональные данные. Ответь только текстом ответа."
                    ),
                },
                {"role": "user", "text": f"Обращение: {ticket_text}\nОтвет базы знаний: {kb_answer}"},
            ],
        }
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        alternatives = data.get("result", {}).get("alternatives", [])
        text = alternatives[0].get("message", {}).get("text", "").strip() if alternatives else ""
        if not text:
            raise RuntimeError("Alice AI LLM returned an empty answer")
        return text
