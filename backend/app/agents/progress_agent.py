"""Progress Agent — calculates study streak, completion rate, and readiness scores."""
import time
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class ProgressAgent(BaseAgent):
    name = "ProgressAgent"

    async def calculate_progress(
        self,
        sessions: List[Dict],
        subjects: List[Dict],
        exams: List[Dict],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate study progress metrics.

        Args:
            sessions: List of PlanSession dicts with completed, completed_at, etc.
            subjects: List of Subject dicts
            exams: List of Exam dicts

        Returns:
          {
            "streak_days": int,
            "total_sessions_completed": int,
            "sessions_today": int,
            "hours_studied_week": float,
            "readiness_scores": { subject_name: float },
            "upcoming_exams": [...],
            "overall_readiness": float,
            "log": { agent_log dict }
          }
        """
        start = time.time()
        today = date.today()

        # ── Streak calculation ───────────────────────────────────────────
        completed_dates = set()
        for s in sessions:
            if s.get("completed"):
                ca = s.get("completed_at")
                if ca:
                    if isinstance(ca, str):
                        ca = datetime.fromisoformat(ca).date()
                    elif isinstance(ca, datetime):
                        ca = ca.date()
                    completed_dates.add(ca)

        streak = 0
        check_date = today
        while check_date in completed_dates:
            streak += 1
            check_date -= timedelta(days=1)

        # ── Sessions today ───────────────────────────────────────────────
        sessions_today = sum(
            1 for s in sessions
            if s.get("completed") and self._session_date(s) == today
        )

        # ── Total completed ──────────────────────────────────────────────
        total_completed = sum(1 for s in sessions if s.get("completed"))

        # ── Hours studied this week ──────────────────────────────────────
        week_start = today - timedelta(days=today.weekday())
        minutes_this_week = 0
        for s in sessions:
            if s.get("completed"):
                sd = self._session_date(s)
                if sd and sd >= week_start:
                    minutes_this_week += s.get("duration_minutes", 90)
        hours_week = round(minutes_this_week / 60.0, 1)

        # ── Readiness scores per subject ─────────────────────────────────
        readiness_scores = {}
        subject_sessions = {}
        for s in sessions:
            sname = s.get("subject_name", "Unknown")
            if sname not in subject_sessions:
                subject_sessions[sname] = {"total": 0, "completed": 0}
            subject_sessions[sname]["total"] += 1
            if s.get("completed"):
                subject_sessions[sname]["completed"] += 1

        for subj in subjects:
            sname = subj.get("name", "Unknown")
            mastery = subj.get("mastery_score", 0.0)
            sess = subject_sessions.get(sname, {"total": 1, "completed": 0})
            completion_rate = sess["completed"] / max(1, sess["total"])
            readiness = round(mastery * 0.4 + completion_rate * 0.6, 3)
            readiness_scores[sname] = min(1.0, readiness)

        # ── Overall readiness ────────────────────────────────────────────
        if readiness_scores:
            overall = round(sum(readiness_scores.values()) / len(readiness_scores), 3)
        else:
            overall = 0.0

        # ── Upcoming exams ───────────────────────────────────────────────
        upcoming_exams = []
        for e in exams:
            edate = e.get("exam_date")
            if isinstance(edate, str):
                edate = date.fromisoformat(edate)
            if edate and edate >= today:
                upcoming_exams.append(e)
        upcoming_exams.sort(key=lambda x: str(x.get("exam_date", "")))

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="calculate_progress",
            status="success",
            input_summary=f"{len(sessions)} sessions, {len(subjects)} subjects",
            output_summary=f"Streak: {streak}d, Readiness: {overall:.0%}",
            duration_ms=duration_ms,
            user_id=user_id,
        )

        return {
            "streak_days": streak,
            "total_sessions_completed": total_completed,
            "sessions_today": sessions_today,
            "hours_studied_week": hours_week,
            "readiness_scores": readiness_scores,
            "upcoming_exams": upcoming_exams,
            "overall_readiness": overall,
            "log": log,
        }

    @staticmethod
    def _session_date(session: Dict) -> Optional[date]:
        sd = session.get("session_date")
        if not sd:
            return None
        if isinstance(sd, str):
            return date.fromisoformat(sd)
        if isinstance(sd, date):
            return sd
        return None
