from dataclasses import dataclass
from pathlib import Path


@dataclass
class HighScore:
    best: int = 0


def load_highscore(path):
    p = Path(path)
    if not p.exists():
        return HighScore(0)
    try:
        return HighScore(int(p.read_text(encoding="utf-8").strip()))
    except Exception:
        return HighScore(0)


def save_highscore(path, value):
    try:
        Path(path).write_text(str(int(value)), encoding="utf-8")
    except Exception:
        pass
