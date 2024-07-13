# %%
from pathlib import Path
import geopandas as gpd
from shapely.geometry import box
from datetime import timedelta

datastore = Path(r"d:\projecten\D2408.RWS.fototool\02.emails\datastore")

app_dir = Path(__file__).parents[1].joinpath("app")
foto_js = app_dir.joinpath("static", "js", "fotos.js")
data_dir = app_dir.joinpath("static", "data")
foto_gpkg = datastore.joinpath("fotos.gpkg")


gdf = gpd.read_file(foto_gpkg, engine="pyogrio")

# copy foto's to app data_dir
for row in gdf.itertuples():
    file_path = datastore.joinpath(row.file_name)
    app_file_path = data_dir.joinpath(row.file_name)
    app_file_path.write_bytes(file_path.read_bytes())

# write foto.js
min_date = gdf.date_time.min().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
max_date = (gdf.date_time.max() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

# convert datetime objects to string
date_time = gdf.date_time.copy()
gdf.drop(columns="date_time", inplace=True)
gdf.loc[:, "date_time"] = date_time.dt.strftime("%Y-%m-%dT%H:%M:%S")

# get bounds from gdf with a buffer of 100m
bounds = list(box(*gdf.total_bounds).buffer(100).bounds)

foto_js.write_text(
f"""
var geoJsonObj = {gdf.to_json(drop_id=True)};

var maxDate = new Date('{max_date}');
var minDate = new Date('{min_date}');
"""
)
