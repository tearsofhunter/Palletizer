"""Assemble the standalone viewer (index.html) from src/ and data/.

Usage: python3 tools/build.py
"""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
head = (root / "src/head.html").read_text()
app = (root / "src/app.html").read_text()
out = head + app
(root / "index.html").write_text(out)
print(f"wrote index.html ({len(out):,} bytes)")
