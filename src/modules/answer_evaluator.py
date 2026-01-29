"""
Answer Evaluator module for grading quiz responses.
Uses keyword matching and optional LLM for semantic evaluation.
"""
import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from src.modules.quiz_generator import Question, QuizResult


@dataclass
class EvaluationResult:
    """Result of evaluating a single answer."""
    question_id: str
    is_correct: bool
    score: float  # 0.0 to 1.0
    feedback: str
    matched_keywords: List[str]
    missing_keywords: List[str]


class AnswerEvaluator:
    """
    Evaluates quiz answers using keyword matching and optional LLM.
    
    Features:
    - Smart keyword matching (case-insensitive, stemming)
    - Partial credit for partial answers
    - Detailed feedback for incorrect answers
    - 70% pass threshold
    """
    
    def __init__(self, pass_threshold: float = None):
        """Initialize the answer evaluator."""
        self.pass_threshold = pass_threshold or float(os.getenv("UNDERSTANDING_THRESHOLD", "0.70"))
    
    def evaluate_answer(
        self,
        question: Question,
        user_answer: str
    ) -> EvaluationResult:
        """
        Evaluate a single answer.
        
        Args:
            question: The question object
            user_answer: User's answer string
            
        Returns:
            EvaluationResult with score and feedback
        """
        if not user_answer or not user_answer.strip():
            return EvaluationResult(
                question_id=question.id,
                is_correct=False,
                score=0.0,
                feedback="No answer provided.",
                matched_keywords=[],
                missing_keywords=question.keywords
            )
        
        user_answer_lower = user_answer.lower().strip()
        
        # Handle different question types
        if question.question_type == "multiple_choice":
            return self._evaluate_multiple_choice(question, user_answer_lower)
        elif question.question_type == "true_false":
            return self._evaluate_true_false(question, user_answer_lower)
        else:
            return self._evaluate_short_answer(question, user_answer_lower)
    
    def _evaluate_multiple_choice(
        self,
        question: Question,
        user_answer: str
    ) -> EvaluationResult:
        """Evaluate multiple choice answer."""
        correct = question.correct_answer.lower().strip()
        
        # Extract just the letter if user included option text
        user_letter = user_answer[0] if user_answer else ""
        correct_letter = correct[0] if correct else ""
        
        is_correct = user_letter == correct_letter
        
        return EvaluationResult(
            question_id=question.id,
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0,
            feedback="" if is_correct else f"Correct answer: {question.correct_answer}",
            matched_keywords=[user_letter] if is_correct else [],
            missing_keywords=[correct_letter] if not is_correct else []
        )
    
    def _evaluate_true_false(
        self,
        question: Question,
        user_answer: str
    ) -> EvaluationResult:
        """Evaluate true/false answer."""
        correct = question.correct_answer.lower().strip()
        
        # Normalize answers
        true_variants = ["true", "t", "yes", "y", "1", "correct"]
        false_variants = ["false", "f", "no", "n", "0", "incorrect", "wrong"]
        
        user_is_true = any(v in user_answer for v in true_variants)
        user_is_false = any(v in user_answer for v in false_variants)
        correct_is_true = any(v in correct for v in true_variants)
        
        is_correct = (user_is_true and correct_is_true) or (user_is_false and not correct_is_true)
        
        return EvaluationResult(
            question_id=question.id,
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0,
            feedback="" if is_correct else f"Correct answer: {question.correct_answer}",
            matched_keywords=["true"] if is_correct else [],
            missing_keywords=["false"] if not is_correct else []
        )
    
    def _evaluate_short_answer(
        self,
        question: Question,
        user_answer: str
    ) -> EvaluationResult:
        """Evaluate short answer using keyword matching."""
        keywords = question.keywords or []
        
        if not keywords:
            # If no keywords, give partial credit for any substantial answer
            if len(user_answer) > 20:
                return EvaluationResult(
                    question_id=question.id,
                    is_correct=True,
                    score=0.7,
                    feedback="Answer recorded. Unable to verify without reference keywords.",
                    matched_keywords=[],
                    missing_keywords=[]
                )
            return EvaluationResult(
                question_id=question.id,
                is_correct=False,
                score=0.3,
                feedback="Please provide a more detailed answer.",
                matched_keywords=[],
                missing_keywords=[]
            )
        
        # Check for keyword matches
        matched_keywords = []
        missing_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check for exact match or partial match
            if self._keyword_matches(keyword_lower, user_answer):
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate score based on keyword matches
        if keywords:
            match_ratio = len(matched_keywords) / len(keywords)
        else:
            match_ratio = 0.5
        
        # Apply scoring curve (reward partial knowledge)
        if match_ratio >= 0.8:
            score = 1.0
        elif match_ratio >= 0.5:
            score = 0.7 + (match_ratio - 0.5) * 0.6
        else:
            score = match_ratio * 1.4  # Boost for partial knowledge
        
        score = min(1.0, max(0.0, score))
        is_correct = score >= 0.7
        
        # Generate feedback
        if is_correct:
            feedback = "Good answer! You covered the key concepts."
        elif matched_keywords:
            feedback = f"Partial credit. You mentioned: {', '.join(matched_keywords)}. Consider also: {', '.join(missing_keywords[:2])}"
        else:
            feedback = f"Review these concepts: {', '.join(keywords[:3])}"
        
        return EvaluationResult(
            question_id=question.id,
            is_correct=is_correct,
            score=score,
            feedback=feedback,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords
        )
    
    def _keyword_matches(self, keyword: str, text: str) -> bool:
        """Check if a keyword matches in the text (with variations)."""
        # Direct match
        if keyword in text:
            return True
        
        # Word boundary match
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
        
        # Stemming variations (simple)
        if keyword.endswith('ing'):
            base = keyword[:-3]
            if base in text or base + 'e' in text:
                return True
        elif keyword.endswith('ed'):
            base = keyword[:-2]
            if base in text or base + 'e' in text:
                return True
        elif keyword.endswith('s'):
            if keyword[:-1] in text:
                return True
        
        return False
    
    def evaluate_quiz(
        self,
        questions: List[Question],
        user_answers: Dict[str, str]
    ) -> QuizResult:
        """
        Evaluate a complete quiz.
        
        Args:
            questions: List of questions
            user_answers: Dict mapping question_id to user's answer
            
        Returns:
            QuizResult with scores and feedback
        """
        scores = {}
        total_score = 0.0
        weak_concepts = []
        
        for question in questions:
            answer = user_answers.get(question.id, "")
            result = self.evaluate_answer(question, answer)
            
            scores[question.id] = result.score
            total_score += result.score
            
            # Track weak concepts (score < 0.5)
            if result.score < 0.5 and question.objective:
                weak_concepts.append(question.objective)
        
        # Calculate average score
        avg_score = total_score / len(questions) if questions else 0.0
        passed = avg_score >= self.pass_threshold
        
        return QuizResult(
            checkpoint_id="",  # Set by caller
            questions=questions,
            user_answers=user_answers,
            scores=scores,
            total_score=avg_score,
            passed=passed,
            attempt_number=1,  # Set by caller
            weak_concepts=list(set(weak_concepts))
        )
    
    def get_feedback_summary(self, quiz_result: QuizResult) -> str:
        """Generate a summary feedback for the quiz result."""
        score_pct = quiz_result.total_score * 100
        
        if quiz_result.passed:
            summary = f"🎉 Congratulations! You scored {score_pct:.0f}% and passed this checkpoint!"
        else:
            summary = f"📚 You scored {score_pct:.0f}%. You need {self.pass_threshold * 100:.0f}% to pass."
            if quiz_result.weak_concepts:
                summary += f"\n\nFocus on these areas:\n"
                for concept in quiz_result.weak_concepts[:3]:
                    summary += f"• {concept}\n"
        
        return summary


# Global evaluator instance
_answer_evaluator: Optional[AnswerEvaluator] = None


def get_answer_evaluator() -> AnswerEvaluator:
    """Get or create the global answer evaluator instance."""
    global _answer_evaluator
    if _answer_evaluator is None:
        _answer_evaluator = AnswerEvaluator()
    return _answer_evaluator
