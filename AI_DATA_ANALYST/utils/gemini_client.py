import json
from google import genai
from prompts import INTENT_SYSTEM_PROMPT, INSIGHT_SYSTEM_PROMPT


class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.intent_model = "gemini-2.5-flash"
        self.insight_model = "gemini-2.5-flash"

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def get_intent(self, question: str, schema: dict) -> dict:
        prompt = f"""
{INTENT_SYSTEM_PROMPT}

Dataset schema:
{json.dumps(schema, indent=2)}

User question:
{question}
"""

        response = self.client.models.generate_content(
            model=self.intent_model,
            contents=prompt
        )

        text = self._clean_json_text(response.text)
        return json.loads(text)

    def generate_insight(self, question: str, computed_summary: dict) -> dict:
        prompt = f"""
{INSIGHT_SYSTEM_PROMPT}

User question:
{question}

Computed summary (already calculated by Python):
{json.dumps(computed_summary, indent=2, default=str)}
"""

        response = self.client.models.generate_content(
            model=self.insight_model,
            contents=prompt
        )

        text = self._clean_json_text(response.text)
        return json.loads(text)