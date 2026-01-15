from dataclasses import dataclass
from pathlib import Path

@dataclass
class HighScore:
    best: int = 0

def load_highscore(path: str) -> HighScore:
    p = Path(path)
    if not p.exists():
        return HighScore(0)
    try:
        return HighScore(int(p.read_text().strip()))
    except Exception:
        return HighScore(0)

def save_highscore(path: str, value: int) -> None:
    try:
        Path(path).write_text(str(value))
    except Exception:
        pass
