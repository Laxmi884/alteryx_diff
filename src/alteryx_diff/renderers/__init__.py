"""Renderer stage for alteryx_diff.

Public surface: JSONRenderer, HTMLRenderer

  from alteryx_diff.renderers import JSONRenderer, HTMLRenderer
  renderer = HTMLRenderer()
  html = renderer.render(diff_result)
"""

from __future__ import annotations

from alteryx_diff.renderers.html_renderer import HTMLRenderer
from alteryx_diff.renderers.json_renderer import JSONRenderer

__all__ = ["JSONRenderer", "HTMLRenderer"]
