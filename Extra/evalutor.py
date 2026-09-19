"""Backward-compatible launcher for the evaluation dashboard.

Use ``python Extra/evaluator.py`` for the canonical entry point.
"""

from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Extra.evaluator import app


if __name__ == "__main__":
    app.launch(
        inbrowser=True,
        server_name="127.0.0.1",
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
    )
