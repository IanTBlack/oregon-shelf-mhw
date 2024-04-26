import os
import xarray as xr

from ormhw.core import CUTI_FP,BEUTI_FP
from ormhw.core import NH_LINE

    
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