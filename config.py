from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_FILENAME = "db_BarokahCopy.db"
DATABASE_PATH = PROJECT_ROOT / DATABASE_FILENAME
APP_VERSION = "1.0.0"


def asset_path(filename: str) -> str:
    return str(DATA_DIR / filename)


def asset_uri(filename: str) -> str:
    return (DATA_DIR / filename).as_posix()
