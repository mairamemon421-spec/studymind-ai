"""Coordinator Agent — orchestrates Priority → Planner pipeline and records step logs."""
import time
from datetime import date
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent
from app.agents.priority_agent import PriorityAgent
from app.agents.planner_agent import PlannerAgent


class CoordinatorAgent(BaseAgent):
    name = "CoordinatorAgent"

    def __init__(self):
        super().__init__()
        self.priority_agent = PriorityAgent()
        self.planner_agent = PlannerAgent()

    async def generate_plan(
        self,
        subjects: List[Dict],
        exams: List[Dict],
        study_hours_per_day: int = 4,
        weeks_ahead: int = 2,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline: rank subjects → create schedule.

        Returns:
          {
            "ranked_subjects": [...],
            "sessions": [...],
            "start_date": "...",
            "end_date": "...",
            "coordinator_notes": "...",
            "logs": [ ...agent_log dicts... ]
          }
        """
        start = time.time()
        logs: List[Dict] = []

        # ── Step 1: Rank subjects ────────────────────────────────────────
        logs.append(self._log_entry(
            action="pipeline_start",
            status="running",
            input_summary=f"{len(subjects)} subjects, {len(exams)} exams",
            output_summary="Starting Priority → Planner pipeline",
            duration_ms=0,
            user_id=user_id,
        ))

        priority_result = await self.priority_agent.rank_subjects(
            subjects=subjects,
            exams=exams,
            user_id=user_id,
        )
        ranked = priority_result["ranked"]
        logs.append(priority_result["log"])

        # ── Step 2: Create schedule ──────────────────────────────────────
        planner_result = await self.planner_agent.create_schedule(
            ranked_subjects=ranked,
            study_hours_per_day=study_hours_per_day,
            weeks_ahead=weeks_ahead,
            user_id=user_id,
        )
        sessions = planner_result["sessions"]
        logs.append(planner_result["log"])

        # ── Finalise ─────────────────────────────────────────────────────
        duration_ms = int((time.time() - start) * 1000)
        notes = (
            f"Generated plan with {len(sessions)} sessions across "
            f"{weeks_ahead} weeks. Top priority: "
            f"{ranked[0]['subject_name'] if ranked else 'N/A'}"
        )

        logs.append(self._log_entry(
            action="pipeline_complete",
            status="success",
            input_summary=f"{len(subjects)} subjects → {len(sessions)} sessions",
            output_summary=notes,
            duration_ms=duration_ms,
            user_id=user_id,
        ))

        return {
            "ranked_subjects": ranked,
            "sessions": sessions,
            "start_date": planner_result["start_date"],
            "end_date": planner_result["end_date"],
            "coordinator_notes": notes,
            "logs": logs,
        }
