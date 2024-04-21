from datetime import datetime
import os
from typing import NamedTuple


class LABELS:
    LON = r'Longitude ($^{\circ}E$)'
    LAT = r'Latitude ($^{\circ}N$)'
    DEPTH = r'Depth ($m$)'
    TIME = r'Datetime ($UTC$)'
    CHL = r'Chlorophyll-a ($\frac{{\mu}g}{L}$)'
    CUTI = r'CUTI ($\frac{m^2}{s})$'
    BEUTI = r'BEUTI ($\frac{mmol}{ms}$)'
    DEN = r'\rho\ ($\frac{kg}{m^3}$)'
    SAL= r'ASU ($\frac{g}{kg}$)'
    TEMP = r'Conservative Temperature ($^{\circ}C$)'
    
    
class UNITS:
    LON = r'$^{\circ}E$'
    LAT = r'$^{\circ}N$'
    DEPTH = r'$m$'
    TIME = r'$UTC$'
    CHL = r'$\frac{{\mu}g}{L}$'
    CUTI = r'$\frac{m^2}{s}$'
    BEUTI = r'$\frac{mmol}{ms}$'
    DEN= r'$\frac{kg}{m^3}$'
    SAL= r'$\frac{g}{kg}$'
    TEMP = r'$^{\circ}C$'
    
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
DATA_DIR = os.path.join(USER_DIR, 'data')
CURATED_DIR = os.path.join(DATA_DIR, 'curated')
PROJECT_DIR = os.path.join(USER_DIR, 'oregon-shelf-mhw')
FIGURE_DIR = os.path.join(PROJECT_DIR, 'figures')


OISSTV2_DIR = os.path.join(DATA_DIR, 'oisstv2')
CUTI_DIR = os.path.join(DATA_DIR, 'cuti')

NASA_DIR = os.path.join(DATA_DIR, 'nasa')
L2_DIR = os.path.join(NASA_DIR,'L2')
L2_GRID_DIR = os.path.join(NASA_DIR, 'L2_GRIDDED')



MAX_THREADS = os.cpu_count()-1

GEBCO_FILEPATH = os.path.join(os.path.join(DATA_DIR,'gebco'),'GEBCO_2023.nc')

CUTI_FP = os.path.join(os.path.join(DATA_DIR,'cuti_beuti'), 'CUTI_daily.nc')
BEUTI_FP = os.path.join(os.path.join(DATA_DIR,'cuti_beuti'), 'BEUTI_daily.nc')

def build_project_directories() -> None:
    """A quick function for building blank directories."""
    _dirs = [PROJECT_DIR, DATA_DIR, FIG_DIR, OISSTV2_DATA_DIR, GEBCO_DATA_DIR, NASA_DATA_DIR]
    for _dir in _dirs:
        os.makedirs(_dir, exist_ok = True)
        
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
    

