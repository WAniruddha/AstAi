from __future__ import annotations

import ast
from pathlib import Path


def test_streamlit_entrypoint_parses() -> None:
    """Fail CI if the Streamlit app contains a Python syntax error."""

    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    ast.parse(app_path.read_text(encoding="utf-8"), filename=str(app_path))
