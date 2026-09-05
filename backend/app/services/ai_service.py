"""
AI Service — Gemini API integration with complete rule-based fallback.

The application is fully functional without an API key.
AI mode enhances the experience when a key is available.
"""
import os
import random
from typing import List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_ENABLED = GEMINI_AVAILABLE and bool(GEMINI_API_KEY)

if AI_ENABLED:
    genai.configure(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────
# Fallback question banks
# ─────────────────────────────────────────────

FALLBACK_INTERVIEW_QUESTIONS = {
    "opening": [
        "Tell me about yourself and your technical background.",
        "Walk me through your resume briefly.",
        "Why are you interested in this role?",
    ],
    "technical": [
        "Explain Object-Oriented Programming and its four pillars.",
        "What is the difference between a stack and a queue?",
        "Explain normalization in databases with examples.",
        "What is the time complexity of binary search?",
        "Explain the concept of polymorphism with a real-world example.",
        "What is a deadlock in OS and how is it prevented?",
        "Explain the difference between TCP and UDP.",
        "What are ACID properties in databases?",
        "How does garbage collection work in Java?",
        "What is REST API and what are its principles?",
    ],
    "dsa": [
        "How would you find the middle element of a linked list in one pass?",
        "Explain the difference between BFS and DFS.",
        "What is dynamic programming? Give an example.",
        "How does quicksort work and what is its average time complexity?",
        "Explain the two-pointer technique with an example.",
    ],
    "project": [
        "Tell me about a project you've built.",
        "What was the most challenging technical problem you solved in a project?",
        "How did you design the database for your project?",
        "What technologies did you use and why?",
        "If you could redo this project, what would you do differently?",
    ],
    "hr": [
        "Where do you see yourself in 5 years?",
        "Tell me about a time you worked in a team and faced a conflict.",
        "What are your strengths and weaknesses?",
        "Why should we hire you over other candidates?",
        "Are you comfortable relocating?",
    ],
    "closing": [
        "Do you have any questions for us?",
        "Is there anything else you'd like us to know about you?",
        "Thank you for your time. We'll get back to you shortly.",
    ]
}

INTERVIEW_FLOW = ["opening", "technical", "dsa", "project", "hr", "closing"]


class AIService:
    """Unified AI service with Gemini integration and rule-based fallback."""

    def __init__(self):
        self.model = None
        if AI_ENABLED:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception:
                self.model = None

    def is_ai_mode(self) -> bool:
        return self.model is not None

    def generate_interview_question(
        self,
        phase: str,
        company: Optional[str],
        role: Optional[str],
        weak_topics: List[str],
        conversation_history: List[dict],
        interview_type: str = "technical",
    ) -> str:
        """Generate the next interview question."""
        if self.model:
            return self._ai_interview_question(
                phase, company, role, weak_topics, conversation_history, interview_type
            )
        return self._fallback_interview_question(phase, conversation_history)

    def _ai_interview_question(
        self,
        phase: str,
        company: Optional[str],
        role: Optional[str],
        weak_topics: List[str],
        history: List[dict],
        interview_type: str,
    ) -> str:
        try:
            history_text = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in history[-6:]
            )
            weak_str = ", ".join(weak_topics[:3]) if weak_topics else "general topics"
            prompt = f"""You are an interviewer at {company or 'a top tech company'} interviewing for the role of {role or 'Software Developer'}.

Interview type: {interview_type}
Current phase: {phase}
Student's weak areas: {weak_str}

Conversation so far:
{history_text}

Generate ONE concise interview question appropriate for this phase and the student's profile. 
If it's the closing phase, wrap up the interview professionally.
Just output the question, nothing else."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return self._fallback_interview_question(phase, history)

    def _fallback_interview_question(self, phase: str, history: List[dict]) -> str:
        phase_key = phase if phase in FALLBACK_INTERVIEW_QUESTIONS else "technical"
        asked = {m["content"] for m in history if m["role"] == "ai"}
        available = [q for q in FALLBACK_INTERVIEW_QUESTIONS[phase_key] if q not in asked]
        if not available:
            available = FALLBACK_INTERVIEW_QUESTIONS[phase_key]
        return random.choice(available)

    def evaluate_interview(
        self,
        company: Optional[str],
        role: Optional[str],
        messages: List[dict],
    ) -> dict:
        """Evaluate the mock interview and return scores + feedback."""
        if self.model:
            return self._ai_evaluate_interview(company, role, messages)
        return self._fallback_evaluate_interview(messages)

    def _ai_evaluate_interview(
        self, company: Optional[str], role: Optional[str], messages: List[dict]
    ) -> dict:
        try:
            conversation = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in messages
            )
            prompt = f"""You are evaluating a mock interview for a {role or 'Software Developer'} role at {company or 'a tech company'}.

Interview transcript:
{conversation}

Evaluate the candidate on a scale of 0-100 for:
1. Technical Knowledge
2. Communication Clarity
3. Answer Relevance

Also provide:
- 2-3 sentence overall feedback
- 3 specific improvement suggestions

Respond ONLY in this exact JSON format:
{{
  "tech_score": 75,
  "comm_score": 70,
  "relevance_score": 80,
  "overall_score": 75,
  "feedback": "...",
  "suggestions": "1. ... 2. ... 3. ..."
}}"""

            response = self.model.generate_content(prompt)
            import json
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception:
            return self._fallback_evaluate_interview(messages)

    def _fallback_evaluate_interview(self, messages: List[dict]) -> dict:
        student_msgs = [m for m in messages if m["role"] == "student"]
        num_responses = len(student_msgs)
        avg_length = sum(len(m["content"]) for m in student_msgs) / max(num_responses, 1)

        # Heuristic scoring based on response engagement
        base = 55
        length_bonus = min(avg_length / 50, 20)  # up to 20 bonus for longer answers
        count_bonus = min(num_responses * 3, 15)  # up to 15 for more responses

        tech_score = round(min(base + length_bonus + count_bonus + random.uniform(-5, 5), 95), 1)
        comm_score = round(min(base + length_bonus * 0.8 + random.uniform(-5, 5), 95), 1)
        relevance_score = round(min(base + count_bonus + random.uniform(-5, 5), 95), 1)
        overall = round((tech_score + comm_score + relevance_score) / 3, 1)

        return {
            "tech_score": tech_score,
            "comm_score": comm_score,
            "relevance_score": relevance_score,
            "overall_score": overall,
            "feedback": (
                f"You completed {num_responses} responses in this interview. "
                "Focus on giving structured answers with specific examples. "
                "Demonstrate your technical depth by explaining concepts clearly."
            ),
            "suggestions": (
                "1. Use the STAR method for behavioral questions. "
                "2. Back up technical claims with concrete examples from your projects. "
                "3. Ask clarifying questions when a question seems ambiguous."
            ),
        }

    def generate_practice_question(
        self,
        topic: str,
        difficulty: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Optional[dict]:
        """Generate an AI practice question. Returns None if AI unavailable."""
        if not self.model:
            return None
        try:
            company_ctx = f"for someone preparing for {company}" if company else ""
            prompt = f"""Generate ONE {difficulty} multiple-choice question about {topic} {company_ctx}.

Respond ONLY in this exact JSON format:
{{
  "question_text": "...",
  "options": [
    {{"option_text": "...", "is_correct": false}},
    {{"option_text": "...", "is_correct": true}},
    {{"option_text": "...", "is_correct": false}},
    {{"option_text": "...", "is_correct": false}}
  ],
  "explanation": "Brief explanation of why the answer is correct."
}}"""

            response = self.model.generate_content(prompt)
            import json
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception:
            return None

    def explain_answer(self, question_text: str, correct_answer: str, topic: str) -> str:
        """Generate an explanation for a question answer."""
        if self.model:
            try:
                prompt = f"Question: {question_text}\nCorrect Answer: {correct_answer}\n\nProvide a clear, concise explanation (2-3 sentences) of why this answer is correct. Focus on the concept of {topic}."
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass
        return f"The correct answer demonstrates a key concept in {topic}. Review the fundamentals to understand this better."


# Singleton instance
ai_service = AIService()
