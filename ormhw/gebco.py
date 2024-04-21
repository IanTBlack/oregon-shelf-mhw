import os
import xarray as xr


def import_gebco(filepath: os.path, bounding_box: object) -> xr.Dataset:
    """
    This function will import a GEBCO file, slice it by latitude and longitude, and then recalculate depth as the inverse of elevation.
    All original data and attributes are retained.
    
    
    :param filepath: The filepath of the GEBCO file. Recommend using the absolute filepath.
    :param bounding_box: A class object (NamedTuple) with the attributes of lat_min, lat_max, lon_min, and lon_max. 
    :return: The GEBCO file data as an xarray dataset.
    """
    
    _ds = xr.open_dataset(filepath)
    _ds = _ds.sel(lat = slice(bounding_box.lat_min,bounding_box.lat_max), 
                  lon = slice(bounding_box.lon_min,bounding_box.lon_max)) # Slice the dataset by latitude and longitude.
    _ds['depth'] = _ds.elevation * -1
    return _ds


