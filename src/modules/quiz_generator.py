"""
Quiz Generator module for creating assessment questions.
Uses LLM to generate questions based on study material from vector store.
"""
import os
import re
import json
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.utils.llm_provider import get_quiz_llm
from src.modules.vector_store import get_vector_store


@dataclass
class Question:
    """Represents a quiz question."""
    id: str
    question_text: str
    question_type: str  # "multiple_choice", "short_answer", "true_false"
    options: List[str] = field(default_factory=list)  # For multiple choice
    correct_answer: str = ""
    keywords: List[str] = field(default_factory=list)  # For answer evaluation
    hint: str = ""
    explanation: str = ""
    objective: str = ""  # Which learning objective this covers
    difficulty: str = "medium"  # easy, medium, hard
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "keywords": self.keywords,
            "hint": self.hint,
            "explanation": self.explanation,
            "objective": self.objective,
            "difficulty": self.difficulty
        }


@dataclass
class QuizResult:
    """Represents the result of a quiz attempt."""
    checkpoint_id: str
    questions: List[Question]
    user_answers: Dict[str, str]
    scores: Dict[str, float]
    total_score: float
    passed: bool
    attempt_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    weak_concepts: List[str] = field(default_factory=list)


class QuizGenerator:
    """
    Generates quiz questions based on study material.
    
    Features:
    - Auto-generates questions from context using LLM
    - Supports multiple question types
    - Creates hints for each question
    - Links questions to learning objectives
    """
    
    def __init__(self, questions_per_quiz: int = None):
        """Initialize the quiz generator."""
        # Reload dotenv to get latest settings
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        self.questions_per_quiz = questions_per_quiz or int(os.getenv("QUESTIONS_PER_QUIZ", "10"))
        print(f"📝 Quiz generator initialized with {self.questions_per_quiz} questions per quiz")
        self.llm = None  # Lazy initialization
        self.vector_store = get_vector_store()
    
    def _get_llm(self):
        """Get LLM instance (lazy initialization)."""
        if self.llm is None:
            try:
                self.llm = get_quiz_llm()
            except Exception as e:
                print(f"⚠️ Could not initialize LLM: {e}")
        return self.llm
    
    def generate_questions(
        self,
        topic: str,
        objectives: List[str],
        context: str = "",
        num_questions: int = None
    ) -> List[Question]:
        """
        Generate quiz questions for a topic.
        
        Args:
            topic: The learning topic
            objectives: Learning objectives to cover
            context: Study material context
            num_questions: Number of questions to generate
            
        Returns:
            List of Question objects
        """
        num_questions = num_questions or self.questions_per_quiz
        
        # Get additional context from vector store
        if not context:
            context = self.vector_store.get_context_for_topic(topic, objectives)
        
        if not context:
            # Generate using only topic and objectives
            context = f"Topic: {topic}\nObjectives: " + ", ".join(objectives)
        
        # Prepare prompt for question generation
        prompt = self._create_question_prompt(topic, objectives, context, num_questions)
        
        llm = self._get_llm()
        if not llm:
            # Return fallback questions
            return self._generate_fallback_questions(topic, objectives, num_questions)
        
        try:
            # Generate questions using LLM
            if hasattr(llm, 'chat'):
                response = llm.chat([
                    {"role": "system", "content": "You are an expert educator creating quiz questions."},
                    {"role": "user", "content": prompt}
                ])
            else:
                response = llm.invoke(prompt)
                if hasattr(response, 'content'):
                    response = response.content
            
            # Parse the response
            questions = self._parse_questions(response, topic, objectives)
            
            if questions:
                print(f"✅ Generated {len(questions)} questions")
                return questions
            else:
                return self._generate_fallback_questions(topic, objectives, num_questions)
                
        except Exception as e:
            print(f"⚠️ Error generating questions: {e}")
            return self._generate_fallback_questions(topic, objectives, num_questions)
    
    def _create_question_prompt(
        self,
        topic: str,
        objectives: List[str],
        context: str,
        num_questions: int
    ) -> str:
        """Create the prompt for question generation with randomness for unique questions."""
        objectives_text = "\n".join(f"- {obj}" for obj in objectives)
        
        # Add randomness to generate different questions each time
        random_seed = random.randint(1000, 9999)
        random_focus = random.choice([
            "Focus on practical applications and real-world examples.",
            "Focus on theoretical concepts and definitions.",
            "Focus on comparisons and contrasts between concepts.",
            "Focus on problem-solving and critical thinking.",
            "Focus on historical context and evolution of ideas.",
            "Focus on common misconceptions and how to avoid them.",
            "Focus on step-by-step processes and methodologies.",
            "Focus on advantages, disadvantages, and trade-offs."
        ])
        
        random_style = random.choice([
            "Use scenario-based questions where possible.",
            "Include questions that test understanding of relationships between concepts.",
            "Ask questions that require applying knowledge to new situations.",
            "Include some questions about edge cases and exceptions.",
            "Mix abstract questions with concrete examples."
        ])
        
        return f"""You MUST generate exactly {num_questions} UNIQUE quiz questions about "{topic}".

RANDOMIZATION SEED: {random_seed} - Use this to ensure questions are different from previous generations.

FOCUS: {random_focus}
STYLE: {random_style}

Learning Objectives:
{objectives_text}

Study Material:
{context[:3000]}

Generate questions in this exact JSON format:
```json
[
  {{
    "question_text": "What is...",
    "question_type": "multiple_choice",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "keywords": ["keyword1", "keyword2"],
    "hint": "Think about...",
    "explanation": "The correct answer is A because...",
    "objective": "Understanding basic concepts",
    "difficulty": "easy"
  }}
]
```

Requirements:
1. Generate EXACTLY {num_questions} UNIQUE questions - different from any previous quiz
2. Question types: 7 multiple_choice, 2 short_answer, 1 true_false
3. Cover all learning objectives across the questions
4. Include helpful hints for each question
5. Provide clear explanations for correct answers
6. Keywords for grading short answers
7. Difficulty distribution: 3 easy, 4 medium, 3 hard

OUTPUT: Return ONLY the JSON array with all {num_questions} unique questions:"""
    
    def _parse_questions(
        self,
        response: str,
        topic: str,
        objectives: List[str]
    ) -> List[Question]:
        """Parse LLM response into Question objects."""
        questions = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                questions_data = json.loads(json_str)
            else:
                # Try to parse as plain JSON
                questions_data = json.loads(response)
            
            for i, q_data in enumerate(questions_data):
                question = Question(
                    id=f"q_{topic.lower().replace(' ', '_')}_{i+1}",
                    question_text=q_data.get("question_text", ""),
                    question_type=q_data.get("question_type", "short_answer"),
                    options=q_data.get("options", []),
                    correct_answer=q_data.get("correct_answer", ""),
                    keywords=q_data.get("keywords", []),
                    hint=q_data.get("hint", ""),
                    explanation=q_data.get("explanation", ""),
                    objective=q_data.get("objective", objectives[0] if objectives else ""),
                    difficulty=q_data.get("difficulty", "medium")
                )
                questions.append(question)
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error parsing questions: {e}")
        
        return questions
    
    def _generate_fallback_questions(
        self,
        topic: str,
        objectives: List[str],
        num_questions: int
    ) -> List[Question]:
        """Generate fallback questions when LLM is unavailable."""
        print("📝 Using fallback question templates")
        
        questions = []
        templates = [
            {
                "question_text": f"What is {topic}?",
                "question_type": "short_answer",
                "keywords": [topic.lower(), "definition", "concept"],
                "hint": f"Think about the fundamental definition of {topic}",
                "explanation": f"{topic} is a key concept that forms the foundation of this subject.",
                "difficulty": "easy"
            },
            {
                "question_text": f"{topic} is an important concept in modern technology.",
                "question_type": "true_false",
                "correct_answer": "True",
                "keywords": ["true", "yes"],
                "hint": "Consider the relevance of this topic in today's world",
                "explanation": f"True - {topic} is indeed important in modern technology.",
                "difficulty": "easy"
            },
            {
                "question_text": f"Name two key characteristics or components of {topic}.",
                "question_type": "short_answer",
                "keywords": ["characteristic", "component", "feature", "element"],
                "hint": "Think about what makes this topic unique",
                "explanation": f"Key aspects of {topic} include its core features and applications.",
                "difficulty": "medium"
            },
            {
                "question_text": f"How does {topic} differ from traditional approaches?",
                "question_type": "short_answer",
                "keywords": ["different", "unlike", "compared", "versus", "new"],
                "hint": "Compare with older or conventional methods",
                "explanation": f"{topic} introduces new paradigms that differ from traditional methods.",
                "difficulty": "medium"
            },
            {
                "question_text": f"Give a real-world example of {topic} in use.",
                "question_type": "short_answer",
                "keywords": ["example", "use", "application", "used", "applied"],
                "hint": "Think about everyday applications you might encounter",
                "explanation": f"There are many real-world applications of {topic} in various industries.",
                "difficulty": "medium"
            },
            {
                "question_text": f"What are the main benefits of using {topic}?",
                "question_type": "short_answer",
                "keywords": ["benefit", "advantage", "helpful", "improve", "better"],
                "hint": "Consider the positive outcomes of using this approach",
                "explanation": f"{topic} provides several key benefits in practical applications.",
                "difficulty": "medium"
            },
            {
                "question_text": f"{topic} can only be used by technical experts.",
                "question_type": "true_false",
                "correct_answer": "False",
                "keywords": ["false", "no"],
                "hint": "Think about how accessible this technology has become",
                "explanation": f"False - {topic} is becoming increasingly accessible to non-experts.",
                "difficulty": "easy"
            },
            {
                "question_text": f"Explain a potential challenge or limitation of {topic}.",
                "question_type": "short_answer",
                "keywords": ["challenge", "limitation", "problem", "issue", "concern", "difficulty"],
                "hint": "No technology is perfect - what are some downsides?",
                "explanation": f"Like any technology, {topic} has certain limitations that should be considered.",
                "difficulty": "hard"
            },
            {
                "question_text": f"How might {topic} evolve in the next few years?",
                "question_type": "short_answer",
                "keywords": ["future", "evolve", "develop", "advance", "improve", "change"],
                "hint": "Consider current trends and potential developments",
                "explanation": f"{topic} is expected to continue evolving with new advancements.",
                "difficulty": "hard"
            },
            {
                "question_text": f"What skills are important for working with {topic}?",
                "question_type": "short_answer",
                "keywords": ["skill", "knowledge", "understand", "learn", "ability"],
                "hint": "Think about what someone would need to know",
                "explanation": f"Working with {topic} requires a combination of technical and analytical skills.",
                "difficulty": "medium"
            },
            {
                "question_text": f"{topic} requires no understanding of underlying principles to use effectively.",
                "question_type": "true_false",
                "correct_answer": "False",
                "keywords": ["false", "no"],
                "hint": "Basic understanding usually helps with effective usage",
                "explanation": f"False - Understanding the principles of {topic} leads to more effective use.",
                "difficulty": "medium"
            },
            {
                "question_text": f"Describe how {topic} can be applied in education.",
                "question_type": "short_answer",
                "keywords": ["education", "learning", "teaching", "student", "school", "train"],
                "hint": "Think about classroom or learning applications",
                "explanation": f"{topic} has significant applications in educational settings.",
                "difficulty": "medium"
            },
            {
                "question_text": f"What ethical considerations are associated with {topic}?",
                "question_type": "short_answer",
                "keywords": ["ethical", "moral", "responsible", "fair", "bias", "privacy"],
                "hint": "Consider the broader societal implications",
                "explanation": f"Ethical considerations are important when implementing {topic}.",
                "difficulty": "hard"
            },
            {
                "question_text": f"{topic} has applications across multiple industries.",
                "question_type": "true_false",
                "correct_answer": "True",
                "keywords": ["true", "yes"],
                "hint": "Think about the versatility of this technology",
                "explanation": f"True - {topic} is used in healthcare, finance, education, and many other fields.",
                "difficulty": "easy"
            },
            {
                "question_text": f"What is the relationship between {topic} and data?",
                "question_type": "short_answer",
                "keywords": ["data", "information", "input", "process", "analyze"],
                "hint": "Consider how data is involved in this concept",
                "explanation": f"Data plays a fundamental role in how {topic} operates and improves.",
                "difficulty": "medium"
            }
        ]
        
        for i in range(min(num_questions, len(templates))):
            template = templates[i]
            objective = objectives[i % len(objectives)] if objectives else f"Understanding {topic}"
            
            question = Question(
                id=f"q_{topic.lower().replace(' ', '_')}_{i+1}",
                question_text=template["question_text"],
                question_type=template["question_type"],
                options=template.get("options", []),
                correct_answer=template.get("correct_answer", ""),
                keywords=template["keywords"],
                hint=template["hint"],
                explanation=template["explanation"],
                objective=objective,
                difficulty=template["difficulty"]
            )
            questions.append(question)
        
        return questions
    
    def get_hint(self, question: Question) -> str:
        """Get hint for a question."""
        if question.hint:
            return question.hint
        return f"💡 Hint: Think carefully about the key concepts of this topic."


# Global quiz generator instance
_quiz_generator: Optional[QuizGenerator] = None


def get_quiz_generator() -> QuizGenerator:
    """Get or create the global quiz generator instance."""
    global _quiz_generator
    if _quiz_generator is None:
        _quiz_generator = QuizGenerator()
    return _quiz_generator


def reset_quiz_generator():
    """Reset the quiz generator to pick up new settings."""
    global _quiz_generator
    _quiz_generator = None
