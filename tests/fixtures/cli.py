"""Minimal .yxmd XML byte fixtures for CLI end-to-end tests.

ToolIDs 901+ allocated for Phase 9. No collision with Phases 1-8 (max 815).
Write bytes to tmp_path in tests — do NOT commit .yxmd files to disk.
"""

from __future__ import annotations

# ToolID 901 — Filter tool, base expression
MINIMAL_YXMD_A: bytes = b"""<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2020.1">
  <Nodes>
    <Node ToolID="901">
      <GuiSettings Plugin="AlteryxBasePluginsGui.Filter">
        <Position x="60" y="100"/>
      </GuiSettings>
      <Properties>
        <Configuration>
          <Expression>Field1 > 0</Expression>
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections/>
</AlteryxDocument>"""

# ToolID 901 — same tool, changed filter expression → produces exit code 1
MINIMAL_YXMD_B: bytes = b"""<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2020.1">
  <Nodes>
    <Node ToolID="901">
      <GuiSettings Plugin="AlteryxBasePluginsGui.Filter">
        <Position x="60" y="100"/>
      </GuiSettings>
      <Properties>
        <Configuration>
          <Expression>Field1 > 100</Expression>
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections/>
</AlteryxDocument>"""

# Identical content — produces exit code 0
IDENTICAL_YXMD: bytes = MINIMAL_YXMD_A

# ToolID 902 — position differs between A and B, config is identical
# Used to test --include-positions flag
POSITION_YXMD_A: bytes = b"""<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2020.1">
  <Nodes>
    <Node ToolID="902">
      <GuiSettings Plugin="AlteryxBasePluginsGui.Filter">
        <Position x="10" y="20"/>
      </GuiSettings>
      <Properties>
        <Configuration>
          <Expression>Field2 > 5</Expression>
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections/>
</AlteryxDocument>"""

POSITION_YXMD_B: bytes = b"""<?xml version="1.0"?>
<AlteryxDocument yxmdVer="2020.1">
  <Nodes>
    <Node ToolID="902">
      <GuiSettings Plugin="AlteryxBasePluginsGui.Filter">
        <Position x="50" y="80"/>
      </GuiSettings>
      <Properties>
        <Configuration>
          <Expression>Field2 > 5</Expression>
        </Configuration>
      </Properties>
    </Node>
  </Nodes>
  <Connections/>
</AlteryxDocument>"""

# Malformed XML — triggers MalformedXMLError → exit code 2
MALFORMED_XML: bytes = b"<not valid xml><<"
