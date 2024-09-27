#%%
from fotoviewer.read_mailbox import read_mailbox

""""
Het lezen van een mailbox naar mailbestanden (emls). De emls worden opgeslagen in de inbox-folder van ondersaande structuur

data_dir
├── archive
│   └── YYYYMMDDThhmmss_archived_eml_file.eml
├── datastore
│       ├── fotos.gpkg
│       ├── image1.jpg
│       ├── image2.png
│       └── imagex.jpg
└── inbox
        └── eml_file.eml

Argumenten die meegegeven kunnen worden zijn:
inbox: en pad naar de inbox-folder in bovenstaande structuur. Kan worden gelezen uit OS variabele FOTOVIEWER_DATA_DIR
"""

read_mailbox()
