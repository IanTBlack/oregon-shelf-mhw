import requests
import sys
import shutil
from datetime import datetime
import fsspec
import multiprocessing
import numpy as np
import os
import pandas as pd
from scipy.interpolate import griddata
import xarray as xr



from ormhw.core import DATA_DIR, BBox

year = int(sys.argv[1])


def main():
    save_directory = os.path.join(os.path.join(DATA_DIR,'nasa'),'L2_GRIDDED')
    os.makedirs(save_directory, exist_ok = True)

    L2_DIR = os.path.join(os.path.join(DATA_DIR,'nasa'),'L2')
    AM_FILES = fsspec.filesystem('file').glob(L2_DIR + '/AQUA*.nc')
    dtr = pd.date_range(datetime(year,7,7), datetime(year,10,10))
    for dt in dtr:
        dt_str = dt.strftime('.%Y%m%dT')
        dt_files = [v for v in AM_FILES if dt_str in v]

        if len(dt_files) == 0:
            continue
    
        f = combine_files(dt, overwrite = True)

        if f is None: 
            continue
        #print(f"Created: {f}")

        
def make_template_grid(lat_min, lat_max, lon_min, lon_max, bin_size = 0.01):
    x = np.arange(lon_min, lon_max, bin_size)
    y = np.arange(lat_min, lat_max, bin_size)
    grid_lons, grid_lats = np.meshgrid(x,y)
    return grid_lons, grid_lats


    
def import_file(filepath):
    lat_min = BBox.lat_min
    lon_min = BBox.lon_min
    lat_max = BBox.lat_max
    lon_max = BBox.lon_max
    grid_lons, grid_lats = make_template_grid(lat_min, lat_max, lon_min, lon_max, bin_size = 0.01)
    try:
        nav = xr.open_dataset(filepath, group = 'navigation_data')
        product = xr.open_dataset(filepath, group = 'geophysical_data')
    except:
        return None
    lats = np.array(nav.latitude)
    lons = np.array(nav.longitude)     
    
    product['chlor_a'] = product['chlor_a'].where(product['chlor_a'] <= 35 ,np.nan)
    product['chlor_a'] = product['chlor_a'].where(product['chlor_a'] >= 0 , np.nan) 
    chl = np.array(product['chlor_a'])
    new_chl = griddata((lons.flatten(),lats.flatten()),chl.flatten(),(grid_lons,grid_lats),method = 'linear')

    return (grid_lats, grid_lons, new_chl)


def export_to_nc(dt, filepaths):
    
    with multiprocessing.Pool(len(filepaths)) as pool:
        data_list = pool.map(import_file, filepaths)
        
    lat = data_list[0][0]  # The grid lat and lons are passed with each import_file output.
    lon = data_list[0][1]
    chl_swaths = [v[-1] for v in data_list]
    grid_chl = np.nanmean(np.array(chl_swaths), axis = 0)
    
    ds = xr.Dataset()
    ds = ds.assign_coords({'latitude':np.unique(lat),'longitude': np.unique(lon)})
    ds['chl'] = (['latitude','longitude'], grid_chl)

    
    filename = f"oc_{dt.strftime('%Y-%m-%d')}.nc"
    filepath = os.path.join(os.path.join(DATA_DIR,'nasa/L2_GRIDDED'), filename)
    ds.to_netcdf(filepath, engine = 'netcdf4')
    return filepath


def combine_files(dt, overwrite = True):
    filename = f"oc_{dt.strftime('%Y-%m-%d')}.nc"
    save_dir = os.path.join(DATA_DIR,'nasa/L2_GRIDDED')
    filepath = os.path.join(save_dir, filename)
    if overwrite is False:
        if os.path.isfile(filepath):
            return filepath
    dt_str = dt.strftime('.%Y%m%dT')
    local = fsspec.filesystem('file')
    files = local.glob(os.path.join(DATA_DIR,'nasa/L2') + '/AQUA*.nc')
    if len(files) == 0:
        return None
    day_files = [f for f in files if dt_str in f]
    new_filepath = export_to_nc(dt, day_files)
    return new_filepath

    

if __name__ == "__main__":
    main()