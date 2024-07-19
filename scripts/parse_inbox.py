#%%
from fotoviewer.parse_emls import parse_emls

""""
The parser van eml-files (email-bestanden). Neemt de volgende data-structuur aan

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

De functie parse_emls leest inbox, slaat alle meta-data en fotos op in datastore en archiveert de email in de archive-folder        

Een argument dat meegegeven kan worden in 'data_dir', die verwijst naar bovenstaande data-structuur
"""

parse_emls()
