from datetime import datetime
import os
import requests
import shutil
import xarray as xr

from ormhw.core import CUTI_FP,BEUTI_FP
from ormhw.core import NH_LINE

# def download_cuti(save_directory: os.path = CUTI_DATA_DIR):
#     os.makedirs(save_directory, exist_ok = True)
#     url = 'https://www.mjacox.com/wp-content/uploads/2024/02/CUTI_daily.nc'
#     filename = os.path.basename(url)
#     filepath = os.path.join(save_directory, filename)
#     with requests.get(url, stream = True) as req:
#         with open(filepath, 'wb') as fileobj:
#             shutil.copyfileobj(req.raw, fileobj)
    
    
def import_cuti(filepath: os.path.abspath = CUTI_FP, latitude: float = NH_LINE.lat):
    """
    Import CUTI at a given latitude.
    
    :param filepath: An absolute filepath for the CUTI_daily.nc file.
    :param latitude: A number indicating the latitude of interest. The nearest method is used to obtain data.
    :return: A sliced dataset.
    """
    _ds = xr.open_dataset(filepath)
    _ds = _ds.sel(latitude = latitude, method = 'nearest')
    return _ds


    
def import_beuti(filepath: os.path = BEUTI_FP, latitude: float = NH_LINE.lat):
    """
    Import BEUTI at a given latitude.
    
    :param filepath: An absolute filepath for the CUTI_daily.nc file.
    :param latitude: A number indicating the latitude of interest. The nearest method is used to obtain data.
    :return: A sliced dataset.
    """
    _ds = xr.open_dataset(filepath)
    _ds = _ds.sel(latitude = latitude, method = 'nearest')
    return _ds