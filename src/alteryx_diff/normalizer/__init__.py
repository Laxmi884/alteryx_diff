"""Normalization pipeline stage for alteryx_diff.

Public surface: normalize()

  from alteryx_diff.normalizer import normalize
  normalized_doc = normalize(workflow_doc)  # WorkflowDoc -> NormalizedWorkflowDoc
"""

from alteryx_diff.normalizer.normalizer import normalize

__all__ = ["normalize"]
