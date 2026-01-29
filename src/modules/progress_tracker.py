"""
Progress Tracker module for managing learning journey state.
Tracks checkpoint completion, retry counts, and overall progress.
"""
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    STUDYING = "studying"
    QUIZ_IN_PROGRESS = "quiz_in_progress"
    NEEDS_TEACHING = "needs_teaching"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class CheckpointProgress:
    """Progress for a single checkpoint."""
    checkpoint_id: str
    topic: str
    status: CheckpointStatus = CheckpointStatus.NOT_STARTED
    attempt_count: int = 0
    max_attempts: int = 3
    best_score: float = 0.0
    last_score: float = 0.0
    weak_concepts: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    study_material_loaded: bool = False
    quiz_results: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def attempts_remaining(self) -> int:
        """Get remaining attempts."""
        return max(0, self.max_attempts - self.attempt_count)
    
    @property
    def can_retry(self) -> bool:
        """Check if retry is allowed."""
        return self.attempts_remaining > 0 and self.status != CheckpointStatus.PASSED


@dataclass
class LearningSession:
    """Represents a complete learning session."""
    session_id: str
    started_at: datetime
    checkpoints: Dict[str, CheckpointProgress] = field(default_factory=dict)
    current_checkpoint_id: Optional[str] = None
    completed_checkpoints: List[str] = field(default_factory=list)
    
    @property
    def total_checkpoints(self) -> int:
        """Get total number of checkpoints."""
        return len(self.checkpoints)
    
    @property
    def completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if not self.checkpoints:
            return 0.0
        passed = len(self.completed_checkpoints)
        return (passed / len(self.checkpoints)) * 100


class ProgressTracker:
    """
    Tracks learning progress across checkpoints.
    
    Features:
    - Sequential progression through checkpoints
    - Retry count management (max 3 attempts)
    - Progress persistence within session
    - Weak concept tracking for Feynman teaching
    """
    
    def __init__(self, max_attempts: int = None):
        """Initialize the progress tracker."""
        self.max_attempts = max_attempts or int(os.getenv("MAX_RETRIES", "3"))
        self.session: Optional[LearningSession] = None
        self._checkpoints_order: List[str] = []
    
    def start_session(self, checkpoint_topics: List[Dict[str, str]]) -> LearningSession:
        """
        Start a new learning session.
        
        Args:
            checkpoint_topics: List of {"id": "...", "topic": "..."} dicts
            
        Returns:
            LearningSession object
        """
        import uuid
        
        session = LearningSession(
            session_id=str(uuid.uuid4()),
            started_at=datetime.now()
        )
        
        # Initialize checkpoints
        for cp in checkpoint_topics:
            cp_id = cp.get("id", cp.get("topic", "").lower().replace(" ", "_"))
            progress = CheckpointProgress(
                checkpoint_id=cp_id,
                topic=cp.get("topic", ""),
                max_attempts=self.max_attempts
            )
            session.checkpoints[cp_id] = progress
            self._checkpoints_order.append(cp_id)
        
        # Set first checkpoint as current
        if self._checkpoints_order:
            session.current_checkpoint_id = self._checkpoints_order[0]
        
        self.session = session
        print(f"📚 Started learning session with {len(checkpoint_topics)} checkpoints")
        return session
    
    def get_current_checkpoint(self) -> Optional[CheckpointProgress]:
        """Get the current checkpoint progress."""
        if not self.session or not self.session.current_checkpoint_id:
            return None
        return self.session.checkpoints.get(self.session.current_checkpoint_id)
    
    def start_checkpoint(self, checkpoint_id: str) -> CheckpointProgress:
        """
        Mark a checkpoint as started.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Updated CheckpointProgress
        """
        if not self.session:
            raise ValueError("No active session")
        
        progress = self.session.checkpoints.get(checkpoint_id)
        if not progress:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        if progress.status == CheckpointStatus.NOT_STARTED:
            progress.status = CheckpointStatus.STUDYING
            progress.started_at = datetime.now()
        
        self.session.current_checkpoint_id = checkpoint_id
        print(f"📖 Started checkpoint: {progress.topic}")
        return progress
    
    def mark_study_complete(self, checkpoint_id: str) -> CheckpointProgress:
        """Mark study material as loaded/read."""
        progress = self._get_progress(checkpoint_id)
        progress.study_material_loaded = True
        progress.status = CheckpointStatus.IN_PROGRESS
        return progress
    
    def start_quiz(self, checkpoint_id: str) -> CheckpointProgress:
        """Mark quiz as started."""
        progress = self._get_progress(checkpoint_id)
        progress.status = CheckpointStatus.QUIZ_IN_PROGRESS
        progress.attempt_count += 1
        print(f"📝 Starting quiz attempt {progress.attempt_count}/{progress.max_attempts}")
        return progress
    
    def record_quiz_result(
        self,
        checkpoint_id: str,
        score: float,
        passed: bool,
        weak_concepts: List[str] = None
    ) -> CheckpointProgress:
        """
        Record a quiz result.
        
        Args:
            checkpoint_id: ID of the checkpoint
            score: Quiz score (0.0 to 1.0)
            passed: Whether the quiz was passed
            weak_concepts: List of concepts the learner struggled with
            
        Returns:
            Updated CheckpointProgress
        """
        progress = self._get_progress(checkpoint_id)
        
        # Update scores
        progress.last_score = score
        if score > progress.best_score:
            progress.best_score = score
        
        # Track weak concepts
        if weak_concepts:
            for concept in weak_concepts:
                if concept not in progress.weak_concepts:
                    progress.weak_concepts.append(concept)
        
        # Store result
        progress.quiz_results.append({
            "attempt": progress.attempt_count,
            "score": score,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "weak_concepts": weak_concepts or []
        })
        
        if passed:
            progress.status = CheckpointStatus.PASSED
            progress.completed_at = datetime.now()
            if checkpoint_id not in self.session.completed_checkpoints:
                self.session.completed_checkpoints.append(checkpoint_id)
            print(f"🎉 Checkpoint passed with {score*100:.0f}%!")
        else:
            if progress.can_retry:
                progress.status = CheckpointStatus.NEEDS_TEACHING
                print(f"📚 Score: {score*100:.0f}%. {progress.attempts_remaining} attempts remaining.")
            else:
                progress.status = CheckpointStatus.FAILED
                print(f"❌ Checkpoint failed after {progress.max_attempts} attempts.")
        
        return progress
    
    def complete_teaching(self, checkpoint_id: str) -> CheckpointProgress:
        """Mark teaching session as complete, ready for retry."""
        progress = self._get_progress(checkpoint_id)
        if progress.status == CheckpointStatus.NEEDS_TEACHING:
            progress.status = CheckpointStatus.IN_PROGRESS
        return progress
    
    def move_to_next_checkpoint(self) -> Optional[CheckpointProgress]:
        """
        Move to the next checkpoint in sequence.
        
        Returns:
            Next CheckpointProgress or None if all complete
        """
        if not self.session:
            return None
        
        current_idx = -1
        if self.session.current_checkpoint_id:
            try:
                current_idx = self._checkpoints_order.index(self.session.current_checkpoint_id)
            except ValueError:
                pass
        
        # Find next incomplete checkpoint
        for i in range(current_idx + 1, len(self._checkpoints_order)):
            cp_id = self._checkpoints_order[i]
            progress = self.session.checkpoints.get(cp_id)
            if progress and progress.status != CheckpointStatus.PASSED:
                self.session.current_checkpoint_id = cp_id
                return progress
        
        print("🎓 All checkpoints completed!")
        return None
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of learning progress."""
        if not self.session:
            return {"status": "No active session"}
        
        checkpoints_summary = []
        for cp_id in self._checkpoints_order:
            progress = self.session.checkpoints.get(cp_id)
            if progress:
                checkpoints_summary.append({
                    "id": cp_id,
                    "topic": progress.topic,
                    "status": progress.status.value,
                    "best_score": progress.best_score,
                    "attempts": progress.attempt_count,
                    "passed": progress.status == CheckpointStatus.PASSED
                })
        
        return {
            "session_id": self.session.session_id,
            "total_checkpoints": self.session.total_checkpoints,
            "completed": len(self.session.completed_checkpoints),
            "completion_percentage": self.session.completion_percentage,
            "current_checkpoint": self.session.current_checkpoint_id,
            "checkpoints": checkpoints_summary
        }
    
    def _get_progress(self, checkpoint_id: str) -> CheckpointProgress:
        """Get checkpoint progress, raising error if not found."""
        if not self.session:
            raise ValueError("No active session")
        
        progress = self.session.checkpoints.get(checkpoint_id)
        if not progress:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        return progress
    
    def can_proceed_to_next(self, checkpoint_id: str) -> bool:
        """Check if user can proceed to next checkpoint."""
        progress = self._get_progress(checkpoint_id)
        return progress.status == CheckpointStatus.PASSED


# Global progress tracker instance
_progress_tracker: Optional[ProgressTracker] = None


def get_progress_tracker() -> ProgressTracker:
    """Get or create the global progress tracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker


def reset_progress_tracker():
    """Reset the global progress tracker."""
    global _progress_tracker
    _progress_tracker = None
