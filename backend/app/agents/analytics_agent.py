"""Analytics Agent — analyzes quiz results, identifies weak areas, suggests focus topics."""
import time
import json
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class AnalyticsAgent(BaseAgent):
    name = "AnalyticsAgent"

    async def analyze_quiz(
        self,
        quiz_data: Dict,
        questions_with_answers: List[Dict],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze quiz submission results.

        Args:
            quiz_data: {"subject_name": ..., "topic": ..., "difficulty": ...}
            questions_with_answers: List of question dicts with user_answer and is_correct

        Returns:
          {
            "score": float,
            "correct": int,
            "total": int,
            "percentage": float,
            "weak_areas": ["..."],
            "feedback": "...",
            "log": { agent_log dict }
          }
        """
        start = time.time()
        total = len(questions_with_answers)
        correct = sum(1 for q in questions_with_answers if q.get("is_correct"))
        percentage = (correct / total * 100) if total > 0 else 0
        score = correct / total if total > 0 else 0

        # Identify weak areas (questions answered incorrectly)
        weak_areas = []
        for q in questions_with_answers:
            if not q.get("is_correct"):
                q_text = q.get("question_text", "")
                if len(q_text) > 60:
                    q_text = q_text[:60] + "..."
                weak_areas.append(q_text)

        input_summary = f"{quiz_data.get('subject_name', 'Unknown')} — {correct}/{total}"

        if self.has_gemini:
            try:
                feedback = await self._analyze_gemini(quiz_data, questions_with_answers, score, weak_areas)
            except Exception as e:
                print(f"[AnalyticsAgent] Gemini error: {e}. Falling back to mock.")
                feedback = self._analyze_mock(quiz_data, score, percentage, weak_areas)
        else:
            feedback = self._analyze_mock(quiz_data, score, percentage, weak_areas)

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="analyze_quiz",
            status="success",
            input_summary=input_summary,
            output_summary=f"Score: {percentage:.0f}%, {len(weak_areas)} weak areas",
            duration_ms=duration_ms,
            user_id=user_id,
        )

        return {
            "score": round(score, 3),
            "correct": correct,
            "total": total,
            "percentage": round(percentage, 1),
            "weak_areas": weak_areas,
            "feedback": feedback,
            "log": log,
        }

    async def _analyze_gemini(
        self, quiz_data: Dict, questions: List[Dict], score: float, weak_areas: List[str]
    ) -> str:
        prompt = f"""You are an educational analytics AI. A student just completed a quiz.

Subject: {quiz_data.get('subject_name', 'Unknown')}
Topic: {quiz_data.get('topic', 'General')}
Score: {score * 100:.0f}%

Questions they got wrong:
{json.dumps(weak_areas, indent=2)}

Provide:
1. A brief performance summary (2 sentences)
2. Specific areas to focus on based on wrong answers
3. Study recommendations (2-3 actionable tips)

Keep response under 200 words. Use markdown formatting."""

        return await self._call_gemini(prompt)

    def _analyze_mock(
        self, quiz_data: Dict, score: float, percentage: float, weak_areas: List[str]
    ) -> str:
        subject = quiz_data.get("subject_name", "this subject")
        if percentage >= 90:
            level = "excellent"
            emoji = "🌟"
            advice = (
                f"You have a strong grasp of {subject}. "
                f"Consider challenging yourself with harder problems or "
                f"helping others study — teaching reinforces mastery."
            )
        elif percentage >= 70:
            level = "good"
            emoji = "👍"
            advice = (
                f"Solid foundation in {subject}! Focus on the areas "
                f"where you lost points. Review those specific topics "
                f"and try practice problems before your next quiz."
            )
        elif percentage >= 50:
            level = "moderate"
            emoji = "📖"
            advice = (
                f"You're on the right track with {subject}, but there's "
                f"room for improvement. Dedicate extra study time to the "
                f"weak areas listed below and consider using the tutor "
                f"chat for explanations."
            )
        else:
            level = "needs improvement"
            emoji = "💪"
            advice = (
                f"Don't be discouraged! {subject} takes time to master. "
                f"Start by reviewing the fundamentals, use the tutor "
                f"feature for concept explanations, and retake quizzes "
                f"after studying each topic."
            )

        weak_text = ""
        if weak_areas:
            weak_text = "\n\n**Areas to review:**\n" + "\n".join(f"- {a}" for a in weak_areas[:5])

        return (
            f"{emoji} **Performance: {level.title()}** ({percentage:.0f}%)\n\n"
            f"{advice}{weak_text}"
        )
