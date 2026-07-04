"""Quiz Agent — generates multiple-choice and short-answer questions."""
import time
import json
import random
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class QuizAgent(BaseAgent):
    name = "QuizAgent"

    async def generate_quiz(
        self,
        subject_name: str,
        topic: Optional[str] = None,
        difficulty: int = 3,
        num_questions: int = 5,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate quiz questions for a subject/topic.

        Returns:
          {
            "questions": [ { question dicts } ],
            "log": { agent_log dict }
          }
        """
        start = time.time()
        topic_str = f" — {topic}" if topic else ""
        input_summary = f"{subject_name}{topic_str}, difficulty={difficulty}, n={num_questions}"

        if self.has_gemini:
            try:
                questions = await self._generate_gemini(subject_name, topic, difficulty, num_questions)
            except Exception as e:
                print(f"[QuizAgent] Gemini error: {e}. Falling back to mock.")
                questions = self._generate_mock(subject_name, topic, difficulty, num_questions)
        else:
            questions = self._generate_mock(subject_name, topic, difficulty, num_questions)

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="generate_quiz",
            status="success",
            input_summary=input_summary,
            output_summary=f"Generated {len(questions)} questions",
            duration_ms=duration_ms,
            user_id=user_id,
        )
        return {"questions": questions, "log": log}

    async def _generate_gemini(
        self, subject: str, topic: Optional[str], difficulty: int, n: int
    ) -> List[Dict]:
        topic_ctx = f" specifically about {topic}" if topic else ""
        prompt = f"""You are a quiz generator. Create {n} questions for {subject}{topic_ctx}.
Difficulty level: {difficulty}/5.

Mix of multiple_choice (4 options, one correct) and short_answer questions.

Return ONLY a JSON array:
[
  {{
    "question_text": "What is...?",
    "question_type": "multiple_choice",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "A) ...",
    "explanation": "Because...",
    "order_index": 0
  }},
  {{
    "question_text": "Explain...",
    "question_type": "short_answer",
    "options": null,
    "correct_answer": "The answer is...",
    "explanation": "This is important because...",
    "order_index": 1
  }}
]"""
        text = await self._call_gemini(prompt)
        return self._parse_json_response(text)

    def _generate_mock(
        self, subject: str, topic: Optional[str], difficulty: int, n: int
    ) -> List[Dict]:
        """Generate deterministic mock questions."""
        topic_str = topic or "General Concepts"
        questions = []
        mc_templates = [
            {
                "q": f"Which of the following best describes a key concept in {subject}?",
                "opts": [
                    f"A) It is the fundamental principle of {subject}",
                    f"B) It is unrelated to {subject}",
                    f"C) It only applies in advanced scenarios",
                    f"D) It was deprecated in modern {subject}",
                ],
                "ans": f"A) It is the fundamental principle of {subject}",
                "exp": f"This is a core concept that forms the foundation of {subject}.",
            },
            {
                "q": f"In {subject}, what is the primary purpose of {topic_str}?",
                "opts": [
                    f"A) To provide structure and organization",
                    f"B) To add unnecessary complexity",
                    f"C) To replace older methodologies entirely",
                    f"D) It serves no practical purpose",
                ],
                "ans": "A) To provide structure and organization",
                "exp": f"{topic_str} helps organize and structure knowledge in {subject}.",
            },
            {
                "q": f"What distinguishes {subject} from related fields?",
                "opts": [
                    f"A) Its focus on practical application",
                    f"B) Its unique theoretical framework",
                    f"C) Both A and B",
                    f"D) Neither A nor B",
                ],
                "ans": "C) Both A and B",
                "exp": f"{subject} combines both practical application and theoretical depth.",
            },
            {
                "q": f"When studying {topic_str} in {subject}, which approach is most effective?",
                "opts": [
                    f"A) Start with fundamentals, then build up",
                    f"B) Jump straight to advanced topics",
                    f"C) Only memorize definitions",
                    f"D) Skip practice entirely",
                ],
                "ans": f"A) Start with fundamentals, then build up",
                "exp": "Building a strong foundation makes advanced topics much more accessible.",
            },
        ]

        sa_templates = [
            {
                "q": f"Explain the significance of {topic_str} in the context of {subject}.",
                "ans": f"{topic_str} is significant in {subject} because it provides the foundational framework for understanding more complex concepts. It establishes key principles that are built upon throughout the field.",
                "exp": "A good answer covers both the definition and its practical importance.",
            },
            {
                "q": f"Describe two real-world applications of concepts from {subject}.",
                "ans": f"Two real-world applications include: 1) Problem-solving in professional settings where {subject} principles are applied directly, and 2) Research and development that advances the field of {subject}.",
                "exp": "Real-world applications demonstrate understanding beyond textbook definitions.",
            },
        ]

        random.seed(hash(f"{subject}{topic_str}{difficulty}"))  # Deterministic
        for i in range(n):
            if i % 3 == 2:  # Every 3rd question is short answer
                tmpl = sa_templates[i % len(sa_templates)]
                questions.append({
                    "question_text": tmpl["q"],
                    "question_type": "short_answer",
                    "options": None,
                    "correct_answer": tmpl["ans"],
                    "explanation": tmpl["exp"],
                    "order_index": i,
                })
            else:
                tmpl = mc_templates[i % len(mc_templates)]
                questions.append({
                    "question_text": tmpl["q"],
                    "question_type": "multiple_choice",
                    "options": tmpl["opts"],
                    "correct_answer": tmpl["ans"],
                    "explanation": tmpl["exp"],
                    "order_index": i,
                })

        return questions
