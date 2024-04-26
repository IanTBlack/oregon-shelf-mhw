from ormhw.core import OISSTV2_DIR, MAX_THREADS
import os
import xarray as xr
import fsspec
import requests
import shutil
from multiprocessing import Pool
import warnings

from datetime import datetime

from itertools import repeat




class OISSTV2():
    def __init__(self):
        pass

    def find_remote_files(self, years: list = range(1981, 2100), ignore_ltm: bool = True):
        url = "https://downloads.psl.noaa.gov/Datasets/noaa.oisst.v2.highres/"
        remote = fsspec.filesystem('https')
        files = remote.glob(url + f"*sst.day.mean*")
        if ignore_ltm is True:
            files = [f for f in files if 'ltm' not in f]
        files_of_interest = []
        for year in years:
            files_of_interest += [f for f in files if str(year) in f]
        return files_of_interest

    def download_files(self, remote_files: list, data_directory: os.path = OISSTV2_DIR, overwrite: bool = False):
        downloaded_files = []
        os.makedirs(data_directory, exist_ok=True)
        for remote_file in remote_files:
            filename = os.path.basename(remote_file)
            filepath = os.path.join(data_directory, filename)
            if overwrite is False:
                if os.path.isfile(filepath):
                    continue
            with requests.get(remote_file, stream = True) as req:
                with open(filepath, 'wb') as fileobj:
                    shutil.copyfileobj(req.raw, fileobj)
                    if os.path.isfile(filepath):
                       downloaded_files.append(filepath)
                       print(f'Downloaded OISSTV2: {filename}')
                    else:
                        raise ConnectionError
        return downloaded_files

    def find_local_files(self, years = range(1983,2024), data_directory = OISSTV2_DIR):
        local = fsspec.filesystem('file')
        local_files = local.glob(data_directory + '/*sst.day.mean*')
        files_of_interest = []
        for year in years:
            files_of_interest += [f for f in local_files if str(year) in f]
        return files_of_interest

    def _format_dataset(self, ds):
        ds = ds.assign_coords({'depth':[0]})
        ds['lon'] = ((ds.lon + 180) % 360) - 180  # Convert longitude from [0 to 360] to [-180 to 180].
        ds = ds.sortby([ds.lon, ds.lat])
        ds = ds.rename({'sst': 'sea_surface_temperature', #Convert to longer CF names.
                        'lon': 'longitude',
                        'lat': 'latitude'})


        return ds

    def import_file(self, filepath, bounding_box):
        ds = xr.open_dataset(filepath)
        ds = self._format_dataset(ds)
        ds = ds.sel(latitude = slice(bounding_box.lat_min, bounding_box.lat_max),
                    longitude=slice(bounding_box.lon_min,bounding_box.lon_max))
        return ds

    def import_files(self, filepaths, bounding_box, num_processes = MAX_THREADS, maxtasksperchild=1):
        with Pool(processes=num_processes, maxtasksperchild=maxtasksperchild) as pool:
            datasets = pool.starmap(self.import_file, zip(filepaths, repeat(bounding_box)))
        combined_ds = xr.combine_by_coords(datasets, combine_attrs = 'drop_conflicts')
        return combined_ds


    def build_climatology(self, ds: xr.Dataset, subset: list or None = None, window: int or None = 11):
        if subset is not None:
            ds = ds.sel(time = slice(subset[0], subset[1]))
        if window is None:
            dsc = ds.groupby('time.dayofyear').mean()  # Compute raw climatology with no smoothing.
        else:
            dsc = ds.groupby('time.dayofyear').mean()
            dsc = dsc.rolling({'dayofyear': window}, min_periods = 1,center = True).mean()
        return dsc

    def build_percentile(self, ds:xr.Dataset, percentile: float=0.9, subset: list or None = None, window: int or None = 11):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            if subset is not None:
                ds = ds.sel(time=slice(subset[0], subset[1]))
            if window is None:
                dsp = ds.groupby('time.dayofyear').quantile([percentile])
            else:
                dsp = ds.groupby('time.dayofyear').quantile([percentile])
                dsp = dsp.rolling({'dayofyear': window}, min_periods = 1,center = True).mean()
            dsp = dsp.sel(quantile=percentile)
        return dsp

    def mask_gte_year(self,ds, dsp,year):
        subds = ds.sel(time = slice(datetime(year,1,1),datetime(year, 12,31,23,59,59)))
        subds['dayofyear'] = subds['time.dayofyear']
        subds = subds.swap_dims({'time':'dayofyear'})
        gte = xr.where(subds - dsp  >= 0, 1, 0)
        gte = gte.swap_dims({'dayofyear':'time'})
        gte['gte'] = gte.sea_surface_temperature
        gte = gte.drop_vars(['sea_surface_temperature','quantile'])
        return gte

    def mask_gte(self, ds, dsp, years = range(2015,2024)):
        
        with Pool(MAX_THREADS) as pool:
            gte_list = pool.starmap(self.mask_gte_year, zip(repeat(ds), repeat(dsp), years))
        dsgte = xr.combine_by_coords(gte_list)
        return dsgte