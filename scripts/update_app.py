#%%
from fotoviewer.update_app import update_app
from pathlib import Path

app_dir = Path(__file__).parents[1] / "app"
""""
Updaten van de fotoviewer app/static/data en app/static/js/fotos.js op basis van de data_dir/datastore directory

De structuur van data_dir

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

De structuur van app

app
├── static
│   ├── data
│   │   ├── image1.jpg
│   │   ├── image2.png
│   │   ├── imagex.jpg
│   │   └── ....
│   └── js
│       ├── fotos.js
│       └── ...
└── index.html


Argumenten die meegegeven kunnen worden zijn:
app_dir: directory met de app (root van index.html)
datastore: de directory met fotos.gpkg en foto-bestanden. Kan worden gelezen uit OS variabele FOTOVIEWER_DATA_DIR 
"""

update_app(app_dir=app_dir)
