# alteryx-diff

A CLI tool to diff Alteryx `.yxmd` workflow files.

## Overview

`alteryx-diff` compares two Alteryx workflow files and generates a structured HTML diff report showing what changed at the tool, configuration, and connection level.

## Installation

```bash
uv sync
```

## Usage

```bash
acd workflow_v1.yxmd workflow_v2.yxmd
```

## Development

```bash
# Install all dependencies (including dev)
uv sync --all-groups

# Run tests
uv run pytest

# Run type checker
uv run mypy src/

# Install pre-commit hooks
uv run pre-commit install
```
