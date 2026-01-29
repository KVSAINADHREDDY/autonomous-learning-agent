"""
LangGraph workflow for the autonomous learning agent.
Implements the complete learning journey with study, quiz, and Feynman teaching.
"""
import os
from typing import Literal, Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from src.data.checkpoints import CheckpointDefinition, get_checkpoint_by_id
from src.modules.vector_store import get_vector_store, VectorStore
from src.modules.quiz_generator import get_quiz_generator, Question
from src.modules.answer_evaluator import get_answer_evaluator, QuizResult
from src.modules.feynman_teacher import get_feynman_teacher
from src.modules.progress_tracker import (
    get_progress_tracker, 
    CheckpointProgress, 
    CheckpointStatus
)
from src.utils.search_tools import search_for_learning_content


@dataclass
class LearningState:
    """State for the learning workflow."""
    # Current checkpoint
    checkpoint_id: str = ""
    checkpoint: Optional[CheckpointDefinition] = None
    
    # Study materials
    study_content: str = ""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quiz state
    questions: List[Question] = field(default_factory=list)
    current_question_idx: int = 0
    user_answers: Dict[str, str] = field(default_factory=dict)
    quiz_result: Optional[QuizResult] = None
    
    # Teaching state
    weak_concepts: List[str] = field(default_factory=list)
    feynman_explanation: str = ""
    
    # Progress
    attempt_number: int = 0
    passed: bool = False
    score: float = 0.0
    
    # Workflow state
    current_stage: str = "init"
    messages: List[str] = field(default_factory=list)
    error: Optional[str] = None


class LearningWorkflow:
    """
    Complete learning workflow with 5 milestones:
    1. Smart Study Material Collection
    2. Flashcard Generation
    3. Intelligent Quiz System
    4. Feynman Teaching Method
    5. Complete Learning Journey
    """
    
    def __init__(self):
        """Initialize the learning workflow."""
        self.vector_store = get_vector_store()
        # Create a fresh quiz generator to pick up current .env settings
        from src.modules.quiz_generator import QuizGenerator
        from src.modules.flashcard_generator import FlashcardGenerator
        self.quiz_generator = QuizGenerator()  # Fresh instance with current settings
        self.flashcard_generator = FlashcardGenerator()  # Add flashcard generator
        self.answer_evaluator = get_answer_evaluator()
        self.feynman_teacher = get_feynman_teacher()
        self.progress_tracker = get_progress_tracker()
        
        self.pass_threshold = float(os.getenv("UNDERSTANDING_THRESHOLD", "0.70"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
    
    # =========================================================
    # MILESTONE 1: SMART STUDY MATERIAL COLLECTION
    # =========================================================
    
    def collect_study_material(
        self,
        checkpoint: CheckpointDefinition,
        user_notes: str = ""
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Collect study material, prioritizing saved notes then web search.
        
        Args:
            checkpoint: The checkpoint to study
            user_notes: Optional user-provided notes
            
        Returns:
            Tuple of (study_content, sources)
        """
        print(f"\n📚 Collecting study material for: {checkpoint.topic}")
        sources = []
        content_parts = []
        
        # Step 1: Use predefined notes first (fastest)
        if checkpoint.notes:
            print("  ✅ Using predefined study notes")
            content_parts.append(checkpoint.notes.strip())
            sources.append({
                "type": "predefined_notes",
                "title": f"{checkpoint.topic} - Study Guide",
                "content": checkpoint.notes[:500]
            })
        
        # Step 2: Add user notes if provided
        if user_notes and user_notes.strip():
            print("  ✅ Adding user-provided notes")
            content_parts.append(f"\n\n## Your Notes\n{user_notes.strip()}")
            sources.append({
                "type": "user_notes",
                "title": "Your Personal Notes",
                "content": user_notes[:500]
            })
        
        # Step 3: Web search if no notes or for supplementary content
        if not content_parts or len(content_parts[0]) < 500:
            print("  🔍 Searching web for additional content...")
            try:
                search_results = search_for_learning_content(
                    topic=checkpoint.topic,
                    objectives=checkpoint.objectives,
                    max_results=3
                )
                
                for result in search_results:
                    content = result.get('content', result.get('snippet', ''))
                    if content:
                        content_parts.append(f"\n\n## {result.get('title', 'Web Source')}\n{content}")
                        sources.append({
                            "type": "web_search",
                            "title": result.get('title', 'Web Source'),
                            "url": result.get('url', ''),
                            "content": content[:300]
                        })
                
                print(f"  ✅ Found {len(search_results)} web sources")
            except Exception as e:
                print(f"  ⚠️ Web search error: {e}")
        
        # Combine all content
        study_content = "\n".join(content_parts)
        
        # Store in vector database for quiz generation
        if study_content:
            self._store_in_vector_db(checkpoint, study_content)
        
        print(f"  📖 Total study content: {len(study_content)} characters from {len(sources)} sources")
        return study_content, sources
    
    def _store_in_vector_db(self, checkpoint: CheckpointDefinition, content: str):
        """Store study content in vector database."""
        # Clear previous content for this checkpoint
        self.vector_store.clear()
        
        # Split content into chunks
        chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        chunks = []
        
        paragraphs = content.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Add to vector store
        documents = [
            {
                "id": f"{checkpoint.id}_chunk_{i}",
                "content": chunk,
                "metadata": {
                    "checkpoint_id": checkpoint.id,
                    "topic": checkpoint.topic,
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        
        self.vector_store.add_documents(documents)
        print(f"  💾 Stored {len(chunks)} chunks in vector database")
    
    # =========================================================
    # MILESTONE 2: FLASHCARD GENERATION
    # =========================================================
    
    def generate_flashcards(
        self,
        checkpoint: CheckpointDefinition,
        num_cards: int = None
    ) -> List:
        """
        Generate flashcards for a checkpoint.
        
        Args:
            checkpoint: The checkpoint to generate flashcards for
            num_cards: Number of cards to generate
            
        Returns:
            List of Flashcard objects
        """
        print(f"\n🃏 Generating flashcards for: {checkpoint.topic}")
        
        # Get context from vector store
        context = self.vector_store.get_context_for_topic(
            checkpoint.topic,
            checkpoint.objectives
        )
        
        # If no vector store content, use checkpoint notes
        if not context:
            context = checkpoint.notes or ""
        
        # Generate flashcards
        flashcards = self.flashcard_generator.generate_flashcards(
            topic=checkpoint.topic,
            objectives=checkpoint.objectives,
            context=context,
            num_cards=num_cards
        )
        
        print(f"  🃏 Generated {len(flashcards)} flashcards")
        return flashcards
    
    # =========================================================
    # MILESTONE 3: INTELLIGENT QUIZ SYSTEM
    # =========================================================
    
    def generate_quiz(
        self,
        checkpoint: CheckpointDefinition,
        num_questions: int = None
    ) -> List[Question]:
        """
        Generate quiz questions based on study material.
        
        Args:
            checkpoint: The checkpoint to quiz on
            num_questions: Number of questions (default from env)
            
        Returns:
            List of Question objects
        """
        print(f"\n📝 Generating quiz for: {checkpoint.topic}")
        
        # Get context from vector store
        context = self.vector_store.get_context_for_topic(
            checkpoint.topic,
            checkpoint.objectives
        )
        
        # If no vector store content, use checkpoint notes
        if not context and checkpoint.notes:
            context = checkpoint.notes
        
        questions = self.quiz_generator.generate_questions(
            topic=checkpoint.topic,
            objectives=checkpoint.objectives,
            context=context,
            num_questions=num_questions
        )
        
        print(f"  ✅ Generated {len(questions)} questions")
        return questions
    
    def get_hint(self, question: Question) -> str:
        """Get hint for a question."""
        return self.quiz_generator.get_hint(question)
    
    def evaluate_quiz(
        self,
        questions: List[Question],
        user_answers: Dict[str, str],
        checkpoint_id: str,
        attempt_number: int
    ) -> QuizResult:
        """
        Evaluate quiz answers.
        
        Args:
            questions: List of questions
            user_answers: Dict of question_id -> answer
            checkpoint_id: ID of the checkpoint
            attempt_number: Which attempt this is
            
        Returns:
            QuizResult with scores and feedback
        """
        print(f"\n📊 Evaluating quiz (Attempt {attempt_number})...")
        
        result = self.answer_evaluator.evaluate_quiz(questions, user_answers)
        result.checkpoint_id = checkpoint_id
        result.attempt_number = attempt_number
        
        print(f"  Score: {result.total_score * 100:.0f}%")
        print(f"  Passed: {'✅ Yes' if result.passed else '❌ No'}")
        
        # Update progress tracker
        self.progress_tracker.record_quiz_result(
            checkpoint_id=checkpoint_id,
            score=result.total_score,
            passed=result.passed,
            weak_concepts=result.weak_concepts
        )
        
        return result
    
    # =========================================================
    # MILESTONE 3: FEYNMAN TEACHING METHOD
    # =========================================================
    
    def teach_weak_concepts(
        self,
        weak_concepts: List[str],
        checkpoint: CheckpointDefinition
    ) -> str:
        """
        Generate Feynman-style explanations for concepts the user struggled with.
        
        Args:
            weak_concepts: List of concepts to explain
            checkpoint: The checkpoint context
            
        Returns:
            Formatted teaching content
        """
        print(f"\n🎓 Generating Feynman explanations for {len(weak_concepts)} concepts...")
        
        if not weak_concepts:
            return "Great job! No concepts need additional explanation."
        
        # Get context for teaching
        context = checkpoint.notes if checkpoint.notes else ""
        
        # Generate explanations
        explanations = self.feynman_teacher.teach_weak_concepts(
            weak_concepts=weak_concepts,
            topic=checkpoint.topic,
            context=context
        )
        
        # Format as teaching session
        teaching_content = self.feynman_teacher.format_teaching_session(explanations)
        
        # Mark teaching complete in progress tracker
        self.progress_tracker.complete_teaching(checkpoint.id)
        
        print(f"  ✅ Generated explanations for: {', '.join(weak_concepts)}")
        return teaching_content
    
    # =========================================================
    # MILESTONE 4: COMPLETE LEARNING JOURNEY
    # =========================================================
    
    def start_learning_session(self, checkpoints: List[CheckpointDefinition]):
        """
        Initialize a new learning session with checkpoints.
        
        Args:
            checkpoints: List of checkpoints to study
        """
        checkpoint_topics = [
            {"id": cp.id, "topic": cp.topic}
            for cp in checkpoints
        ]
        self.progress_tracker.start_session(checkpoint_topics)
    
    def start_checkpoint(self, checkpoint_id: str) -> CheckpointProgress:
        """Start working on a checkpoint."""
        return self.progress_tracker.start_checkpoint(checkpoint_id)
    
    def can_retry(self, checkpoint_id: str) -> bool:
        """Check if user can retry the quiz."""
        progress = self.progress_tracker._get_progress(checkpoint_id)
        return progress.can_retry
    
    def get_attempts_remaining(self, checkpoint_id: str) -> int:
        """Get remaining attempts for a checkpoint."""
        progress = self.progress_tracker._get_progress(checkpoint_id)
        return progress.attempts_remaining
    
    def move_to_next_checkpoint(self) -> Optional[CheckpointProgress]:
        """Move to the next checkpoint in the learning journey."""
        return self.progress_tracker.move_to_next_checkpoint()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall learning progress."""
        return self.progress_tracker.get_progress_summary()
    
    def run_complete_workflow(
        self,
        checkpoint: CheckpointDefinition,
        user_notes: str = ""
    ) -> LearningState:
        """
        Run the complete learning workflow for a checkpoint.
        
        This is the main entry point that orchestrates all milestones.
        
        Args:
            checkpoint: The checkpoint to learn
            user_notes: Optional user-provided notes
            
        Returns:
            Final LearningState
        """
        state = LearningState(
            checkpoint_id=checkpoint.id,
            checkpoint=checkpoint,
            current_stage="collecting_material"
        )
        
        try:
            # Start checkpoint tracking
            self.start_checkpoint(checkpoint.id)
            
            # Milestone 1: Collect study material
            state.study_content, state.sources = self.collect_study_material(
                checkpoint, user_notes
            )
            state.current_stage = "material_collected"
            state.messages.append(f"Collected {len(state.sources)} study sources")
            
            # Milestone 2: Generate quiz
            state.questions = self.generate_quiz(checkpoint)
            state.current_stage = "quiz_ready"
            state.messages.append(f"Generated {len(state.questions)} quiz questions")
            
            # Note: Quiz taking and evaluation happens interactively in the UI
            # The workflow pauses here and continues when user submits answers
            
        except Exception as e:
            state.error = str(e)
            state.current_stage = "error"
            state.messages.append(f"Error: {str(e)}")
        
        return state


# Global workflow instance
_learning_workflow: Optional[LearningWorkflow] = None


def get_learning_workflow() -> LearningWorkflow:
    """Get or create the global learning workflow instance."""
    global _learning_workflow
    if _learning_workflow is None:
        _learning_workflow = LearningWorkflow()
    return _learning_workflow


def reset_learning_workflow():
    """Reset the global learning workflow."""
    global _learning_workflow
    _learning_workflow = None
