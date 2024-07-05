# %%
from exif import Image
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point


APP_DIR =  Path(__file__).parents[1].joinpath("app")
FOTOS_DIR = APP_DIR.joinpath("static", "data")
FOTOS_JS = APP_DIR.joinpath("static", "js", "fotos.js")


def get_point(image_path):
    with open(image_path, 'rb') as image_file:
        img = Image(image_file)
        
    if not img.has_exif:
        raise ValueError("Image has no EXIF data")
    
    if hasattr(img, 'gps_latitude') and hasattr(img, 'gps_longitude'):
        lat = img.gps_latitude
        lon = img.gps_longitude
        lat_ref = img.gps_latitude_ref
        lon_ref = img.gps_longitude_ref

        # Convert to decimal degrees
        lat = convert_to_degrees(lat, lat_ref)
        lon = convert_to_degrees(lon, lon_ref)
        
        return Point(lon, lat)
    else:
        raise ValueError("No GPS data found")


def convert_to_degrees(value, ref):
    d, m, s = value
    degrees = d + (m / 60.0) + (s / 3600.0)
    if ref in ['S', 'W']:
        degrees = -degrees
    return degrees

def get_url(image_path):
    return image_path.relative_to(APP_DIR).as_posix()

data = [{"url": get_url(i), "geometry": get_point(i)} for i in FOTOS_DIR.glob("*.jpg")]
gdf = gpd.GeoDataFrame(data, crs=4326)
gdf.to_crs(28992, inplace=True)

FOTOS_JS.write_text(f"""var geoJsonObj = {gdf.to_json(drop_id=True)}""")


