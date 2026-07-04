"""Planner Agent — creates a weekly study schedule from priority rankings."""
import time
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    async def create_schedule(
        self,
        ranked_subjects: List[Dict],
        study_hours_per_day: int = 4,
        weeks_ahead: int = 2,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a study timetable from ranked subjects.

        Returns:
          {
            "sessions": [ { session dicts } ],
            "start_date": ...,
            "end_date": ...,
            "log": { agent_log dict }
          }
        """
        start = time.time()
        start_date = date.today()
        end_date = start_date + timedelta(weeks=weeks_ahead)
        input_summary = f"{len(ranked_subjects)} subjects, {study_hours_per_day}h/day, {weeks_ahead} weeks"

        if self.has_gemini:
            try:
                sessions = await self._plan_with_gemini(ranked_subjects, study_hours_per_day, start_date, end_date)
            except Exception as e:
                print(f"[PlannerAgent] Gemini error: {e}. Falling back to mock.")
                sessions = self._plan_mock(ranked_subjects, study_hours_per_day, start_date, end_date)
        else:
            sessions = self._plan_mock(ranked_subjects, study_hours_per_day, start_date, end_date)

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="create_schedule",
            status="success",
            input_summary=input_summary,
            output_summary=f"Created {len(sessions)} study sessions",
            duration_ms=duration_ms,
            user_id=user_id,
        )
        return {
            "sessions": sessions,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "log": log,
        }

    async def _plan_with_gemini(
        self, ranked_subjects: List[Dict], hours_per_day: int, start_date: date, end_date: date
    ) -> List[Dict]:
        prompt = f"""You are a study scheduling AI. Create a detailed study timetable.

Start: {start_date.isoformat()}
End: {end_date.isoformat()}
Study hours per day: {hours_per_day}
Available hours per session: 1-2 hours each

Subjects ranked by priority (highest first):
{json.dumps(ranked_subjects, indent=2)}

Rules:
- Allocate more time to higher priority subjects
- Spread sessions across all weekdays (Mon-Fri)
- Weekends are lighter (max 2h)
- Each session = 1 specific topic/chapter
- Session times from 08:00 to 22:00

Return ONLY a JSON array:
[
  {{
    "subject_id": "...",
    "subject_name": "...",
    "topic": "Chapter 3: Linear Algebra",
    "session_date": "2025-01-15",
    "start_time": "09:00",
    "end_time": "10:30",
    "duration_minutes": 90,
    "priority_score": 0.85
  }}
]"""
        text = await self._call_gemini(prompt)
        return self._parse_json_response(text)

    def _plan_mock(
        self, ranked_subjects: List[Dict], hours_per_day: int, start_date: date, end_date: date
    ) -> List[Dict]:
        """Generate a deterministic mock schedule."""
        sessions = []
        current = start_date
        topics = [
            "Introduction & Overview", "Core Concepts", "Problem Solving", "Practice Problems",
            "Review & Assessment", "Advanced Topics", "Case Studies", "Mock Exam Prep",
        ]
        slot_starts = ["08:00", "09:30", "11:00", "13:00", "14:30", "16:00", "17:30", "19:00", "20:30"]

        day_count = 0
        while current <= end_date:
            is_weekend = current.weekday() >= 5
            day_hours = max(1, hours_per_day // 2) if is_weekend else hours_per_day
            sessions_today = max(1, day_hours // 2)

            for slot_idx in range(sessions_today):
                if not ranked_subjects:
                    break
                # Cycle subjects weighted by priority
                subj_idx = slot_idx % len(ranked_subjects)
                subj = ranked_subjects[subj_idx]
                topic = topics[(day_count + slot_idx) % len(topics)]
                start_t = slot_starts[slot_idx % len(slot_starts)]
                sh, sm = map(int, start_t.split(":"))
                duration = 90
                eh = sh + (sm + duration) // 60
                em = (sm + duration) % 60
                end_t = f"{eh:02d}:{em:02d}"

                sessions.append({
                    "subject_id": subj.get("subject_id", ""),
                    "subject_name": subj.get("subject_name", ""),
                    "topic": f"{topic} — {subj.get('subject_name', '')}",
                    "session_date": current.isoformat(),
                    "start_time": start_t,
                    "end_time": end_t,
                    "duration_minutes": duration,
                    "priority_score": subj.get("priority_score", 0.5),
                })

            current += timedelta(days=1)
            day_count += 1

        return sessions
