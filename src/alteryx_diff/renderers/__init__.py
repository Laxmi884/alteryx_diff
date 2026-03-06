"""Renderer stage for alteryx_diff.

Public surface: JSONRenderer

  from alteryx_diff.renderers import JSONRenderer
  renderer = JSONRenderer()
  json_text = renderer.render(diff_result)
"""

from __future__ import annotations

from alteryx_diff.renderers.json_renderer import JSONRenderer

__all__ = ["JSONRenderer"]
