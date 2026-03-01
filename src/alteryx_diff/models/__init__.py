"""Public export surface for all model classes and type aliases.

All pipeline stages import from here:
    from alteryx_diff.models import WorkflowDoc, AlteryxNode, ToolID

Never import from sub-modules directly. This allows internal file organization
to change without breaking any callers.
"""

from alteryx_diff.models.diff import DiffResult, EdgeDiff, NodeDiff
from alteryx_diff.models.types import AnchorName, ConfigHash, ToolID
from alteryx_diff.models.workflow import AlteryxConnection, AlteryxNode, WorkflowDoc

__all__ = [
    # NewType aliases
    "ToolID",
    "ConfigHash",
    "AnchorName",
    # Workflow models
    "WorkflowDoc",
    "AlteryxNode",
    "AlteryxConnection",
    # Diff models
    "DiffResult",
    "NodeDiff",
    "EdgeDiff",
]
