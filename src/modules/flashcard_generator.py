"""
Flashcard Generator module for creating study flashcards.
Uses LLM to generate flashcards based on study material.
"""
import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from src.utils.llm_provider import get_quiz_llm
from src.modules.vector_store import get_vector_store


@dataclass
class Flashcard:
    """Represents a study flashcard."""
    id: str
    front: str  # Question/Term
    back: str   # Answer/Definition
    category: str = ""  # Topic category
    difficulty: str = "medium"
    hint: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "category": self.category,
            "difficulty": self.difficulty,
            "hint": self.hint
        }


class FlashcardGenerator:
    """
    Generates study flashcards from learning material.
    
    Features:
    - Creates term/definition flashcards
    - Generates concept explanation cards
    - Supports multiple difficulty levels
    """
    
    def __init__(self, cards_per_topic: int = None):
        """Initialize the flashcard generator."""
        self.cards_per_topic = cards_per_topic or int(os.getenv("FLASHCARDS_PER_TOPIC", "10"))
        self.llm = None
        self.vector_store = get_vector_store()
    
    def _get_llm(self):
        """Get LLM instance (lazy initialization)."""
        if self.llm is None:
            try:
                self.llm = get_quiz_llm()
            except Exception as e:
                print(f"⚠️ Could not initialize LLM: {e}")
        return self.llm
    
    def generate_flashcards(
        self,
        topic: str,
        objectives: List[str],
        context: str = "",
        num_cards: int = None
    ) -> List[Flashcard]:
        """
        Generate flashcards for a topic.
        
        Args:
            topic: The learning topic
            objectives: Learning objectives to cover
            context: Study material context
            num_cards: Number of cards to generate
            
        Returns:
            List of Flashcard objects
        """
        num_cards = num_cards or self.cards_per_topic
        
        # Get context from vector store if not provided
        if not context:
            context = self.vector_store.get_context_for_topic(topic, objectives)
        
        if not context:
            context = f"Topic: {topic}\nObjectives: " + ", ".join(objectives)
        
        prompt = self._create_flashcard_prompt(topic, objectives, context, num_cards)
        
        llm = self._get_llm()
        if not llm:
            return self._generate_fallback_flashcards(topic, objectives, num_cards)
        
        try:
            if hasattr(llm, 'chat'):
                response = llm.chat([
                    {"role": "system", "content": "You are an expert educator creating study flashcards."},
                    {"role": "user", "content": prompt}
                ])
            else:
                response = llm.invoke(prompt)
                if hasattr(response, 'content'):
                    response = response.content
            
            flashcards = self._parse_flashcards(response, topic)
            
            if flashcards:
                print(f"✅ Generated {len(flashcards)} flashcards")
                return flashcards
            else:
                return self._generate_fallback_flashcards(topic, objectives, num_cards)
                
        except Exception as e:
            print(f"⚠️ Error generating flashcards: {e}")
            return self._generate_fallback_flashcards(topic, objectives, num_cards)
    
    def _create_flashcard_prompt(
        self,
        topic: str,
        objectives: List[str],
        context: str,
        num_cards: int
    ) -> str:
        """Create the prompt for flashcard generation."""
        objectives_text = "\n".join(f"- {obj}" for obj in objectives)
        
        return f"""Generate {num_cards} study flashcards about "{topic}".

Learning Objectives:
{objectives_text}

Study Material:
{context[:3000]}

Generate flashcards in this exact JSON format:
```json
[
  {{
    "front": "What is machine learning?",
    "back": "Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
    "category": "Definition",
    "difficulty": "easy",
    "hint": "Think about how computers can learn patterns"
  }}
]
```

Requirements:
1. Mix of card types: definitions, concepts, examples, comparisons
2. Cover all learning objectives
3. Front should be a clear question or term
4. Back should be a concise, complete answer
5. Include helpful hints
6. Vary difficulty (easy, medium, hard)

Generate exactly {num_cards} flashcards:"""
    
    def _parse_flashcards(self, response: str, topic: str) -> List[Flashcard]:
        """Parse LLM response into Flashcard objects."""
        flashcards = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                cards_data = json.loads(json_str)
            else:
                cards_data = json.loads(response)
            
            for i, card_data in enumerate(cards_data):
                flashcard = Flashcard(
                    id=f"fc_{topic.lower().replace(' ', '_')}_{i+1}",
                    front=card_data.get("front", ""),
                    back=card_data.get("back", ""),
                    category=card_data.get("category", "General"),
                    difficulty=card_data.get("difficulty", "medium"),
                    hint=card_data.get("hint", "")
                )
                flashcards.append(flashcard)
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Error parsing flashcards: {e}")
        
        return flashcards
    
    def _generate_fallback_flashcards(
        self,
        topic: str,
        objectives: List[str],
        num_cards: int
    ) -> List[Flashcard]:
        """Generate fallback flashcards when LLM is unavailable."""
        print("📝 Using fallback flashcard templates")
        
        flashcards = []
        templates = [
            {
                "front": f"What is {topic}?",
                "back": f"{topic} is a fundamental concept in this field that helps us understand and apply key principles.",
                "category": "Definition",
                "difficulty": "easy",
                "hint": "Think about the basic definition"
            },
            {
                "front": f"Why is {topic} important?",
                "back": f"{topic} is important because it provides the foundation for understanding more advanced concepts and has practical applications.",
                "category": "Concept",
                "difficulty": "easy",
                "hint": "Consider the practical benefits"
            },
            {
                "front": f"What are the key components of {topic}?",
                "back": f"The key components include core principles, practical applications, and theoretical foundations that work together.",
                "category": "Components",
                "difficulty": "medium",
                "hint": "Break it down into parts"
            },
            {
                "front": f"How does {topic} differ from traditional approaches?",
                "back": f"{topic} introduces new paradigms and methodologies that offer advantages over conventional methods.",
                "category": "Comparison",
                "difficulty": "medium",
                "hint": "Compare with older methods"
            },
            {
                "front": f"Give an example of {topic} in practice.",
                "back": f"Real-world applications of {topic} can be seen in various industries including technology, healthcare, and finance.",
                "category": "Example",
                "difficulty": "medium",
                "hint": "Think of everyday applications"
            },
            {
                "front": f"What are the limitations of {topic}?",
                "back": f"Like any approach, {topic} has limitations including complexity, resource requirements, and specific use case constraints.",
                "category": "Limitations",
                "difficulty": "hard",
                "hint": "No technology is perfect"
            },
            {
                "front": f"How can you get started with {topic}?",
                "back": f"Start by understanding the fundamentals, practicing with examples, and gradually building on your knowledge.",
                "category": "Getting Started",
                "difficulty": "easy",
                "hint": "Think step by step"
            },
            {
                "front": f"What skills are needed for {topic}?",
                "back": f"Key skills include analytical thinking, problem-solving, and understanding of foundational concepts.",
                "category": "Skills",
                "difficulty": "medium",
                "hint": "What would help you learn this?"
            },
            {
                "front": f"How is {topic} evolving?",
                "back": f"The field is rapidly evolving with new techniques, tools, and applications emerging regularly.",
                "category": "Trends",
                "difficulty": "hard",
                "hint": "Think about recent developments"
            },
            {
                "front": f"What are best practices for {topic}?",
                "back": f"Best practices include starting simple, continuous learning, applying concepts practically, and staying updated.",
                "category": "Best Practices",
                "difficulty": "medium",
                "hint": "What would experts recommend?"
            }
        ]
        
        for i in range(min(num_cards, len(templates))):
            template = templates[i]
            flashcard = Flashcard(
                id=f"fc_{topic.lower().replace(' ', '_')}_{i+1}",
                front=template["front"],
                back=template["back"],
                category=template["category"],
                difficulty=template["difficulty"],
                hint=template["hint"]
            )
            flashcards.append(flashcard)
        
        return flashcards


# Global flashcard generator instance
_flashcard_generator: Optional[FlashcardGenerator] = None


def get_flashcard_generator() -> FlashcardGenerator:
    """Get or create the global flashcard generator instance."""
    global _flashcard_generator
    if _flashcard_generator is None:
        _flashcard_generator = FlashcardGenerator()
    return _flashcard_generator
