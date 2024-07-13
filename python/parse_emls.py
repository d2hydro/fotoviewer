#%%
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr
from exif import Image
from shapely.geometry import Point
from datetime import datetime
import io
from pathlib import Path
import shutil
import geopandas as gpd
import pandas as pd


inbox = Path(r"d:\projecten\D2408.RWS.fototool\02.emails\inbox")
datastore = Path(r"d:\projecten\D2408.RWS.fototool\02.emails\datastore")
archive = Path(r"d:\projecten\D2408.RWS.fototool\02.emails\archive")

def read_exif(image_file):
    """Read exif metadata from image if lat/lon and datetime are available."""
    img = Image(image_file)

    if "APP1" in img._segments.keys():
        if all(hasattr(img, i) for i in ["has_exif", "gps_latitude", "gps_longitude", "datetime_original"]):
            return img
        

def convert_to_degrees(value, ref):
    """Convert exif lat/lon to degrees"""
    d, m, s = value
    degrees = d + (m / 60.0) + (s / 3600.0)
    if ref in ['S', 'W']:
        degrees = -degrees
    return degrees

def get_point(img):
    """Get a point from exif metadata"""
    # Get lat/lon metadata
    lat = img.gps_latitude
    lon = img.gps_longitude
    lat_ref = img.gps_latitude_ref
    lon_ref = img.gps_longitude_ref

    # Convert to decimal degrees
    lat = convert_to_degrees(lat, lat_ref)
    lon = convert_to_degrees(lon, lon_ref)

    # Convert to Point
    return Point(lon, lat)

def get_date_time(img):
    """Get datetime from exif metadata"""
    return datetime.strptime(img.datetime_original, '%Y:%m:%d %H:%M:%S')

def get_unique_id(img):
    """Get unique id from exif metadata"""

    unique_id = get_date_time(img).strftime("%Y%m%dT%H%M%S")

    if hasattr(img, "image_unique_id"):
        unique_id = f"{unique_id}_{img.image_unique_id}"

    return unique_id

def new_file_name(date_time, sender, file_name):
    """Construct new file name from date_time, sender and file_name"""

    # if we don't have date-time info we use now as datetime
    if date_time is None:
        date_time = datetime.now()

    # make sure we parse datetime to string
    if isinstance(date_time, datetime):
        date_time = date_time.strftime("%Y%m%dT%H%M%S")

    if sender is None:    
        sender = "unknown"

    new_file_name = f"{date_time}_{sender}_{file_name.name}".replace(" ","_")

    return new_file_name

def get_sender(from_header, senders):
    if from_header:
        parsed_from_header = parseaddr(from_header)
        if senders:
            if parsed_from_header[1] in senders:
                return parsed_from_header[0]
        else:
            return parsed_from_header[0]


def parse_eml(eml_file, to_archive=True, re_import=False, senders=[]):
    data = []
    # Open the EML file
    with open(eml_file, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Get the email subject
    subject = msg['subject']

    # Get the email sender
    sender = get_sender(msg['From'], senders)
    if sender is None:
        pass

    # Get the email body
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in disposition:
                body = part.get_payload(decode=True).decode(part.get_content_charset())
                break
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset())

    # Parse all attachements as images
    for part in msg.iter_attachments():
        filename = part.get_filename()
        content = part.get_payload(decode=True)

        with io.BytesIO(content) as image_file:
            # read exif from file_objec
            img = read_exif(image_file)

            # only returns img if file is image and exif is complete
            if img is not None:
                # read all data from exif
                geometry = get_point(img)
                date_time = get_date_time(img)

                # store file with a unique uuid
                new_filename = datastore.joinpath(
                    Path(filename).with_stem(get_unique_id(img))
                    )
                image_file.seek(0)
                new_filename.write_bytes(image_file.read())
                data += [{"file_name":new_filename.name, "sender": sender, "date_time":date_time, "subject":subject, "body": body, "geometry":geometry}]
    if to_archive:
        # Move eml-file to archive
        msg_date_time = msg["Date"]
        msg_date_time = parsedate_to_datetime(msg_date_time) if msg_date_time  else None
        if re_import:
            new_eml_file = archive.joinpath(eml_file.name)
        else:
            new_eml_file = archive.joinpath(new_file_name(
                date_time=msg_date_time,
                sender=sender,
                file_name=eml_file
                )
            )

        shutil.move(eml_file, new_eml_file)

    return data

# parse all emls
data = []
for eml_file in inbox.glob("*.eml"):
    data += parse_eml(eml_file, to_archive=False, re_import=False)

# converteer data naar een geopackage
foto_gpkg = datastore.joinpath("fotos.gpkg")

gdf = gpd.GeoDataFrame(data, crs=4326)
gdf.to_crs(28992, inplace=True)

# als de GeoPackage al bestond, dan vullen we hem aan
if foto_gpkg.exists():
    gdf = pd.concat([gdf, gpd.read_file(foto_gpkg, engine="pyogrio")])
    gdf.drop_duplicates(inplace=True)

# en sowieso schrijven we hem weg
gdf.to_file(foto_gpkg, engine="pyogrio")
