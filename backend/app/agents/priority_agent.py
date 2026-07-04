"""Priority Agent — ranks subjects by urgency based on exams and difficulty."""
import time
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class PriorityAgent(BaseAgent):
    name = "PriorityAgent"

    async def rank_subjects(
        self,
        subjects: List[Dict],
        exams: List[Dict],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ranks subjects by priority score (0.0–1.0) using exam proximity,
        importance, difficulty, and mastery score.

        Returns:
          {
            "ranked": [ { "subject_id", "subject_name", "priority_score", "reasoning" }, ... ],
            "log": { agent_log dict }
          }
        """
        start = time.time()
        input_summary = f"{len(subjects)} subjects, {len(exams)} exams"

        if self.has_gemini:
            try:
                result = await self._rank_with_gemini(subjects, exams)
            except Exception as e:
                print(f"[PriorityAgent] Gemini error: {e}. Falling back to mock.")
                result = self._rank_mock(subjects, exams)
        else:
            result = self._rank_mock(subjects, exams)

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="rank_subjects",
            status="success",
            input_summary=input_summary,
            output_summary=f"Ranked {len(result)} subjects",
            duration_ms=duration_ms,
            user_id=user_id,
        )
        return {"ranked": result, "log": log}

    async def _rank_with_gemini(self, subjects: List[Dict], exams: List[Dict]) -> List[Dict]:
        today = date.today().isoformat()
        prompt = f"""You are a study planning AI. Today is {today}.

Given these subjects:
{json.dumps(subjects, indent=2)}

And these upcoming exams:
{json.dumps(exams, indent=2)}

Rank each subject by study priority. Priority score is 0.0 (lowest) to 1.0 (highest).
Consider: days until exam, exam importance (1-5), subject difficulty (1-5), current mastery (0.0-1.0 where lower mastery = higher priority).

Return ONLY a JSON array like:
[
  {{
    "subject_id": "...",
    "subject_name": "...",
    "priority_score": 0.95,
    "reasoning": "Exam in 3 days, high importance, low mastery"
  }}
]
Ordered by priority_score descending."""

        text = await self._call_gemini(prompt)
        return self._parse_json_response(text)

    def _rank_mock(self, subjects: List[Dict], exams: List[Dict]) -> List[Dict]:
        """Algorithmic mock ranking."""
        today = date.today()
        exam_map: Dict[str, Dict] = {}
        for exam in exams:
            sid = exam.get("subject_id", "")
            edate = datetime.fromisoformat(str(exam.get("exam_date", today))).date() if isinstance(exam.get("exam_date"), str) else exam.get("exam_date", today)
            if isinstance(edate, str):
                edate = date.fromisoformat(edate)
            days_until = max(0, (edate - today).days)
            importance = exam.get("importance", 3)
            if sid not in exam_map or days_until < exam_map[sid]["days_until"]:
                exam_map[sid] = {"days_until": days_until, "importance": importance}

        ranked = []
        for subj in subjects:
            sid = subj.get("id", "")
            difficulty = subj.get("difficulty", 3) / 5.0
            mastery = subj.get("mastery_score", 0.0)
            exam_info = exam_map.get(sid, {})
            days_until = exam_info.get("days_until", 30)
            importance = exam_info.get("importance", 3) / 5.0

            # Urgency: closer exam = higher score
            urgency = max(0.0, 1.0 - days_until / 30.0) if days_until <= 30 else 0.0
            # Need: high difficulty + low mastery
            need = (difficulty * 0.5 + (1.0 - mastery) * 0.5)
            # Combined
            priority = urgency * 0.5 + importance * 0.3 + need * 0.2
            priority = min(1.0, priority)

            reason_parts = []
            if days_until <= 7:
                reason_parts.append(f"Exam in {days_until} days")
            if mastery < 0.4:
                reason_parts.append("low mastery")
            if subj.get("difficulty", 3) >= 4:
                reason_parts.append("high difficulty")
            reasoning = ", ".join(reason_parts) if reason_parts else "Standard priority"

            ranked.append({
                "subject_id": sid,
                "subject_name": subj.get("name", "Unknown"),
                "priority_score": round(priority, 3),
                "reasoning": reasoning,
            })

        ranked.sort(key=lambda x: x["priority_score"], reverse=True)
        return ranked
