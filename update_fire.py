import requests
import fiona
import geopandas as gpd
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
import bs4
import re
import pandas as pd
from datetime import date, datetime
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_df(region, date_span, sensor):

    # Set up session to avoid max_retries
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    logger.info(f'Getting fires for region ({region}) and sensor ({sensor})')

    url = 'https://firms.modaps.eosdis.nasa.gov/api/kml_fire_footprints/'

    params = {
        'region': region,
        'sensor': sensor,
        'date_span': date_span
    }

    headers = {
      'Content-Type': '.kmz'
    }

    response = session.request("GET", url, params=params, headers=headers)

    if response.status_code != 200:
        logger.error(str(response.status_code) + ' ' + response.text)
    else:
        logger.info('Successfully requested fires')

    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

    logger.info('Getting contents from request')

    f = fiona.BytesCollection(bytes(response.content))


    df = gpd.GeoDataFrame()
    for layer in fiona.listlayers(f.path):
        if 'Footprints' not in layer:
            logging.info(f'Proccessing {layer}')
            s = gpd.read_file(f.path, driver='KML', layer=layer)
            df = df.append(s, ignore_index=True)

    logger.info('Done!')
    return df


def clean_attributes(value):
    today = datetime.today()
    attributes = {}
    soup = BeautifulSoup(value, 'html.parser')
    for item in soup.contents:
        if isinstance(item, bs4.element.Tag):
            if len(item.next.strip()) > 0:
                attr_key = item.next.strip().translate({ord(c): None for c in '!@#$:'})
                if attr_key == 'Detection Time':
                    attr_val = item.nextSibling.strip()[0:10] + 'T' + item.nextSibling.strip()[11:]
                    attr_val = attr_val[0:16]
                    date_val = datetime.strptime(attr_val, '%Y-%m-%dT%H:%M')
                    attributes['today'] = today
                    date_dif = round((today - date_val).total_seconds()/3600,1)
                    attributes['hours_since'] = date_dif

                elif attr_key == 'Day/Night' or attr_key == 'Sensor':
                    attr_val = item.nextSibling.strip()
                else:
                    attr_val = re.sub("[^0-9.:\-]", "", item.nextSibling.strip())
                    try:
                        attr_val = float(attr_val)
                    except:
                        attr_val = attr_val
                attributes[attr_key] = attr_val

    return attributes


def write_clean_df(df, filename):

    logger.info('Cleaning attributes')

    df['attributes'] = df.apply(lambda row: clean_attributes(row['Description']), axis=1)
    new_df = df.join(pd.DataFrame(df.pop('attributes').values.tolist()))

    logger.info('Writing to geojson...')
    with fiona.drivers():
        new_df.to_file(filename, driver='GeoJSON')



# Get FIRMS data



regions = ['northern_and_central_africa', 'southern_africa']
date_span= ['24h', '48h', '72h', '7d']
sensors = ['c6.1', 'suomi-npp-viirs-c2', 'noaa-20-viirs-c2']

c6_df = get_df(regions[0], date_span[2], sensors[0])
su_df = get_df(regions[0], date_span[2], sensors[1])
no_df = get_df(regions[0], date_span[2], sensors[2])

c6_df_south = get_df(regions[1], date_span[2], sensors[0])
su_df_south = get_df(regions[1], date_span[2], sensors[1])
no_df_south = get_df(regions[1], date_span[2], sensors[2])


df = c6_df.append(su_df).append(no_df).append(c6_df_south).append(su_df_south).append(no_df_south)

write_clean_df(df, 'data/fires.ldgeojson.ld')