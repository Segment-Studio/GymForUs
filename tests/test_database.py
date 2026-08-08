from __future__ import annotations

import os
import tempfile
from pathlib import Path

from backend import database


def test_resolve_db_path_uses_tmp_on_vercel(monkeypatch) -> None:
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.setenv("VERCEL", "1")

    path = database.resolve_db_path(base_dir=Path("/tmp/app"))

    assert path == Path(tempfile.gettempdir()) / "gymforus.db"
    assert path.parent == Path(tempfile.gettempdir())
