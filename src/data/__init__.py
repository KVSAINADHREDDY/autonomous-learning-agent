"""
Autonomous Learning Agent - Data module.
Contains predefined checkpoints and learning content.
"""
from src.data.checkpoints import (
    CheckpointDefinition,
    get_all_checkpoints,
    get_checkpoint_by_id,
    get_checkpoints_summary,
    CHECKPOINTS
)

__all__ = [
    "CheckpointDefinition",
    "get_all_checkpoints",
    "get_checkpoint_by_id",
    "get_checkpoints_summary",
    "CHECKPOINTS"
]
