import os
from PySide6.QtCore import QStandardPaths, QCoreApplication
from pathlib import Path

QCoreApplication.setApplicationName("BarokahCopyPOS")
app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)

if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)

PROJECT_ROOT = Path(__file__).resolve().parent
APP_DATA_DIR = Path(app_data_dir)
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_FILENAME = "db_BarokahCopy.db"
DATABASE_PATH = PROJECT_ROOT / DATABASE_FILENAME      #testing
# DATABASE_PATH = APP_DATA_DIR / DATABASE_FILENAME    #production
APP_VERSION = "1.1.0"


def asset_path(filename: str) -> str:
    return str(DATA_DIR / filename)


def asset_uri(filename: str) -> str:
    return (DATA_DIR / filename).as_posix()
