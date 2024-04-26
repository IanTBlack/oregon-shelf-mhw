import os
from typing import NamedTuple

MAX_THREADS = os.cpu_count() - 1

class BoundingBox(NamedTuple):
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


BBox = BoundingBox(lat_min = 35.0, 
                   lat_max = 55.0,
                   lon_min = -140, 
                   lon_max = -120)
    

USER_DIR = os.path.expanduser('~')
PROJECT_DIR = os.path.join(USER_DIR, 'oregon-shelf-mhw')
FIGURE_DIR = os.path.join(PROJECT_DIR, 'figures')

DATA_DIR = os.path.join(USER_DIR, 'data')
BLOBTRACKER_DIR = os.path.join(DATA_DIR, 'blobtracker')

CURATED_DIR = os.path.join(DATA_DIR, 'curated')

CUTI_BEUTI_DIR = os.path.join(DATA_DIR, 'cuti_beuti')

GEBCO_DIR = os.path.join(DATA_DIR,'gebco')

NASA_DIR = os.path.join(DATA_DIR, 'nasa')
L2_DIR = os.path.join(NASA_DIR,'L2')
L2_GRID_DIR = os.path.join(NASA_DIR, 'L2_GRIDDED')

OISSTV2_DIR = os.path.join(DATA_DIR, 'oisstv2')

GEBCO_FP = os.path.join(os.path.join(DATA_DIR,'gebco'),'GEBCO_2023.nc')
CUTI_FP = os.path.join(os.path.join(DATA_DIR,'cuti_beuti'), 'CUTI_daily.nc')
BEUTI_FP = os.path.join(os.path.join(DATA_DIR,'cuti_beuti'), 'BEUTI_daily.nc')

BLOBTRACKER_FP = os.path.join(BLOBTRACKER_DIR, 'blobtracker.csv')

        
class CE01:
    lat: float = 44.6598
    lon: float = -124.095

class CE02:
    lat: float = 44.6393
    lon: float = -124.304

class CE04:
    lat: float = 44.3811
    lon: float = -124.96    
    
class NH_LINE:
    lat: float = 44.652
    lon_min: float = -126.0
    lon_max: float = -124.1
    
class CAPE_BLANCO:
    lat: float = 42.8376
    lon: float = -124.5640 + 0.15 # Add buffer for mapping.
    
class COLUMBIA_RIVER:
    lat: float = 46.24692 
    lon: float = -124.09344 + 0.2 # Add buffer for mapping.
    

    