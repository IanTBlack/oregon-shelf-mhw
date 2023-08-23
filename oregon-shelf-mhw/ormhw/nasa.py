from datetime import datetime, timedelta
import fsspec
import numpy as np
import pandas as pd
import os
import re
import requests
from scipy.interpolate import griddata
import shutil
import time
import urllib
import xarray as xr

def make_template_grid(lat_min, lat_max, lon_min, lon_max, bin_size = 0.01):
    # Make holder arrays for a common grid.
    x = np.arange(lon_min, lon_max, bin_size)
    y = np.arange(lat_min, lat_max, bin_size)
    grid_lons, grid_lats = np.meshgrid(x,y)
    return grid_lons, grid_lats


def find_oc_files(dt, lat_min = 41, lat_max = 47, lon_min = -126.5, lon_max = -123.5):
    """
    Discover OC L2 files for a given day and area.
    """
    start_date = dt.strftime('%Y-%m-%d')
    end_date = (dt + timedelta(days=1)).strftime('%Y-%m-%d')
    base = 'https://cmr.earthdata.nasa.gov/search/granules.umm_json'
    params = {'page_size': 100,
              'short_name': 'MODISA_L2_OC',
              'temporal': f'{start_date},{end_date}',
              'bounding_box': f"{lon_min},{lat_min},{lon_max},{lat_max}",
              'provider': 'OB_DAAC',
              'sort_key': 'start_date'}
    with requests.get(base, params = params) as response:
        data = response.json()
    hits, took, items = (data['hits'], data['took'], data['items'])
    print(f'Found {hits} files in {took} ms.')
    if hits == 0:
        print(f'No data for {start_date}.')
        return None
    else:
        return items

def download_oc_files(items, save_directory = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/nasa/", overwrite = False, verbose = False):
    """
    Download OC L2 files as discovered with the find_oc_files function.
    """
    os.makedirs(save_directory, exist_ok = True)
    downloaded_files = []
    for _item in items:
        _data_info = {}
        meta = _item['meta']
        umm = _item['umm']
        download_url = umm['RelatedUrls'][0]['URL']
        save_filename = download_url.split('/')[-1]
        save_filepath = os.path.normpath(os.path.join(save_directory, save_filename))
        if os.path.isfile(save_filepath) and overwrite is False:
            downloaded_files.append(save_filepath)
            continue
        with requests.get(download_url, stream = True) as req:
            time.sleep(0.01)
            with open(save_filepath,'wb') as f:
                shutil.copyfileobj(req.raw,f)
        if not os.path.isfile(save_filepath):
            raise FileNotFoundError
        else:
            if verbose is True:
                print(f"Downloaded {download_url} to {save_filepath}.")
        downloaded_files.append(save_filepath)
    return downloaded_files
    

            
def grid_data(downloaded_files, dt, delete_originals_after_gridding = True):
    lat_min = 41
    lon_min = -126.5
    lat_max = 47
    lon_max =  -123.5
    grid_lons, grid_lats = make_template_grid(lat_min, lat_max, lon_min, lon_max, bin_size = 0.01)
    chl_swaths = []
    start_date = dt.strftime('%Y-%m-%d')
    for dfile in downloaded_files:
        try:
            nav = xr.open_dataset(dfile,group = 'navigation_data')
            product = xr.open_dataset(dfile, group = 'geophysical_data')  
        except:
            print('Failure to ingest data.')
            continue
        lats = np.array(nav.latitude)
        lons = np.array(nav.longitude)     
        product['chlor_a'] = product['chlor_a'].where(product['chlor_a'] < 50 ,np.nan)
        product['chlor_a'] = product['chlor_a'].where(product['chlor_a'] > 0 ,np.nan) 
        chl = np.array(product['chlor_a'])
        # try:
        new_chl = griddata((lons.flatten(),lats.flatten()),chl.flatten(),(grid_lons,grid_lats),method = 'linear')
        chl_swaths.append(new_chl)
        # except:
        #     print('Failure to grid data.')
        #     continue
    grid_chl= np.nanmean(np.array(chl_swaths),axis = 0)
    ds = xr.Dataset(data_vars = dict(chl = (['x','y'], grid_chl)), 
                    coords = dict(lon = (['x','y'], grid_lons), 
                                  lat = (['x','y'],grid_lats)))
    new_filepath = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/nasa/oc_{start_date}.nc"
    ds.to_netcdf(new_filepath)
    print(f"Created OC .nc for {start_date}.")
    if delete_originals_after_gridding is True:
        if os.path.exists(new_filepath):
            for dfile in downloaded_files:
                os.remove(dfile)
        else:
            raise OSError
    return new_filepath
        
        
class OC():
    def __init__(self,folder = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/nasa/"):
        self.data_location = folder 
        
    def _find_files(self, bdt, edt):
        local = fsspec.filesystem('file')
        files = local.glob(self.data_location + 'oc*.nc')
        dtr = pd.date_range(bdt,edt)
        keep_files = []
        for file in files:
            fdt = re.findall('(\d{4}-\d{2}-\d{2}).nc',file)[0]
            fdt = datetime.strptime(fdt,'%Y-%m-%d')
            if fdt in dtr:
                keep_files.append(file)
        return keep_files
        
    
    def aggregate_oc(self, bdt, edt):
        files = self._find_files(bdt, edt)
        chls = []
        for file in files:
            ds = xr.open_dataset(file)
            chls.append(ds.chl)
        lat = np.array(ds.lat)
        lon = np.array(ds.lon)
        mean_chl = np.nanmean(chls,axis = 0)
        return (lat, lon, mean_chl)
    
    
    
    