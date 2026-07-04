"""Tutor Agent — conversational chat that explains concepts with simple examples."""
import time
import json
from typing import List, Dict, Any, Optional
from app.agents.base import BaseAgent


class TutorAgent(BaseAgent):
    name = "TutorAgent"

    async def chat(
        self,
        message: str,
        subject_name: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message and get a tutoring response.

        Args:
            message: User's question / input
            subject_name: Optional subject context
            history: List of {"role": "user"|"assistant", "content": "..."}

        Returns:
          {
            "reply": "...",
            "log": { agent_log dict }
          }
        """
        start = time.time()
        history = history or []
        input_summary = f"'{message[:80]}...' ({subject_name or 'general'})"

        if self.has_gemini:
            try:
                reply = await self._chat_gemini(message, subject_name, history)
            except Exception as e:
                print(f"[TutorAgent] Gemini error: {e}. Falling back to mock.")
                reply = self._chat_mock(message, subject_name)
        else:
            reply = self._chat_mock(message, subject_name)

        duration_ms = int((time.time() - start) * 1000)
        log = self._log_entry(
            action="tutor_chat",
            status="success",
            input_summary=input_summary,
            output_summary=f"Reply: {reply[:100]}...",
            duration_ms=duration_ms,
            user_id=user_id,
        )
        return {"reply": reply, "log": log}

    async def _chat_gemini(
        self, message: str, subject_name: Optional[str], history: List[Dict[str, str]]
    ) -> str:
        context = f" about {subject_name}" if subject_name else ""
        history_text = ""
        if history:
            recent = history[-10:]  # Keep last 10 messages for context
            history_text = "\n\nPrevious conversation:\n" + "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in recent
            )

        prompt = f"""You are a friendly, expert study tutor{context}.
Explain concepts clearly using simple examples and analogies.
Break down complex topics into digestible parts.
Use markdown formatting for readability (headers, bullet points, code blocks).
Keep responses concise but thorough (max 500 words).
{history_text}

STUDENT: {message}

TUTOR:"""

        return await self._call_gemini(prompt)

    def _chat_mock(self, message: str, subject_name: Optional[str]) -> str:
        """Generate a helpful mock response."""
        subject_ctx = f" in **{subject_name}**" if subject_name else ""
        lower = message.lower()

        if any(w in lower for w in ["what is", "define", "explain"]):
            return (
                f"Great question{subject_ctx}! 🎓\n\n"
                f"Let me break this down for you:\n\n"
                f"## Key Concept\n"
                f"The topic you're asking about involves several important ideas:\n\n"
                f"1. **Foundation**: Start with the basics — understand the core definition first\n"
                f"2. **Application**: See how it applies in real-world scenarios\n"
                f"3. **Connection**: Notice how it relates to other concepts you've learned\n\n"
                f"### Simple Analogy 💡\n"
                f"Think of it like building blocks — each concept stacks on the previous one. "
                f"Master the foundation, and everything else clicks into place.\n\n"
                f"Would you like me to go deeper into any of these points?"
            )
        elif any(w in lower for w in ["how", "example", "show"]):
            return (
                f"Here's how it works{subject_ctx}: 🔧\n\n"
                f"## Step-by-Step\n\n"
                f"1. **Step 1**: Identify what you're working with\n"
                f"2. **Step 2**: Apply the relevant formula or method\n"
                f"3. **Step 3**: Verify your result\n\n"
                f"### Example\n"
                f"Let's say you have a simple case:\n"
                f"- Start with the given information\n"
                f"- Apply each step systematically\n"
                f"- Check: does the answer make sense?\n\n"
                f"**Pro tip**: Practice with easier examples first, "
                f"then gradually increase difficulty. 📈\n\n"
                f"Want me to work through a specific problem with you?"
            )
        elif any(w in lower for w in ["help", "stuck", "don't understand", "confused"]):
            return (
                f"No worries — let's tackle this together! 💪\n\n"
                f"When you're stuck{subject_ctx}, try this approach:\n\n"
                f"1. **Restate the problem** in your own words\n"
                f"2. **Identify what you know** vs. what you need to find\n"
                f"3. **Look for patterns** in similar problems you've solved\n\n"
                f"Sometimes taking a short break and coming back with fresh eyes "
                f"makes all the difference.\n\n"
                f"Tell me more specifically where you're getting stuck, "
                f"and I'll guide you through it! 🎯"
            )
        else:
            return (
                f"Great topic{subject_ctx}! 📚\n\n"
                f"Here are some key points to consider:\n\n"
                f"- **Start with why**: Understanding the purpose makes learning easier\n"
                f"- **Connect the dots**: Link this to what you already know\n"
                f"- **Practice actively**: Don't just read — try problems yourself\n\n"
                f"I'm here to help you master this topic. "
                f"Feel free to ask me anything specific! 🚀"
            )
