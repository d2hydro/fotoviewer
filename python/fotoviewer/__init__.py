#%%
import os
from pathlib import Path

__version__ = "2024.9.1"

TOKEN_FILE = os.getenv("FOTOVIEWER_TOKEN_FILE")
CLIENT_ID = os.getenv("FOTOVIEWER_CLIENT_ID")
CLIENT_SECRET = os.getenv("FOTOVIEWER_CLIENT_SECRET")
FOTOVIEWER_DATA_DIR = os.getenv("FOTOVIEWER_DATA_DIR")

AUTHORITY = "https://login.microsoftonline.com/common"

def create_sub_dirs(data_dir):
    for sub_dir in ["inbox", "datastore", "archive"]:
        dir_path = data_dir / sub_dir
        dir_path.mkdir(parents=True, exist_ok=True)

def date_time_file_prefix(date_time):
    """String we use as prefix"""
    return date_time.strftime("%Y%m%dT%H%M%S") 

if FOTOVIEWER_DATA_DIR is not None:
    FOTOVIEWER_DATA_DIR = Path(FOTOVIEWER_DATA_DIR)
    INBOX = FOTOVIEWER_DATA_DIR / "inbox"
    DATASTORE = FOTOVIEWER_DATA_DIR / "datastore"
    ARCHIVE = FOTOVIEWER_DATA_DIR / "archive"

    create_sub_dirs(FOTOVIEWER_DATA_DIR)
else:
    INBOX = None
    DATASTORE = None
