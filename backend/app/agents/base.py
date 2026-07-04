"""Base agent class with Gemini client, mock fallback, and structured logging."""
import time
import json
from datetime import datetime
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()


class BaseAgent:
    name: str = "BaseAgent"

    def __init__(self):
        self._client = None
        if settings.has_gemini:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self._client = client
            except Exception as e:
                print(f"[{self.name}] Gemini init failed: {e}. Using mock mode.")

    @property
    def has_gemini(self) -> bool:
        return self._client is not None

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API and return text response."""
        if not self._client:
            raise RuntimeError("Gemini client not initialized")
        from google import genai
        response = self._client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return response.text

    def _parse_json_response(self, text: str) -> Any:
        """Extract JSON from Gemini response (may be wrapped in markdown code blocks)."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last line (```json ... ```)
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return json.loads(text)

    def _log_entry(
        self,
        action: str,
        status: str,
        input_summary: str = "",
        output_summary: str = "",
        duration_ms: int = 0,
        user_id: Optional[str] = None,
    ) -> dict:
        """Build a log entry dict for the agent_logs table."""
        return {
            "agent_name": self.name,
            "action": action,
            "status": status,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        }
