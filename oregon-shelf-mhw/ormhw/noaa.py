import fsspec
import lxml.html
import os
import pandas as pd
import requests
from requests.compat import urljoin
import shutil
import urllib
import xarray as xr



def download_oisstv2_sst_mean(years: list or tuple , save_directory: os.path.abspath = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/noaa/", overwrite: bool = False) -> None:
    base ="https://downloads.psl.noaa.gov/Datasets/noaa.oisst.v2.highres/"
    os.makedirs(save_directory, exist_ok = True)
    for year in years:
        filename = f"sst.day.mean.{year}.nc"
        save_filepath = os.path.normpath(os.path.join(save_directory,filename))
        if os.path.isfile(save_filepath) and overwrite is False:
            continue
        download_url = urljoin(base,filename)
        with requests.get(download_url, stream = True) as response:
            with open(save_filepath, 'wb') as fileobj:
                shutil.copyfileobj(response.raw, fileobj)
                if os.path.isfile(save_filepath):
                    print(f"Downloaded {filename} to {save_directory}.")
                else:
                    msg = f"{filename} download failed!"
                    raise ConnectionError(msg)

                    
def import_oisstv2_sst_mean(years, data_dir = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/noaa/"):
    dss = []
    local = fsspec.filesystem('file')
    if len(years) == 1:
        year = int(years[0])
        [file] = local.glob(data_dir + f'/*mean.{year}*.nc')
        mds = xr.open_dataset(file)
    else:
        for year in years:
            year = int(year)
            [file] = local.glob(data_dir + f'/*mean.{year}*.nc')
            _mds = xr.open_dataset(file)
            dss.append(_mds)
        mds = xr.concat(dss,dim = 'time')
    return mds


                                 
def download_blobtracker_data(save_directory = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/noaa/", overwrite = False):
    os.makedirs(save_directory, exist_ok = True)
    save_filepath = os.path.join(save_directory,'blobtracker_data.csv')
    if os.path.isfile(save_filepath) and overwrite is False:
        return None
    response = requests.get('https://oceanview.pfeg.noaa.gov/erddap/tabledap/cciea_OC_MHW_EV.htmlTable')
    if response.status_code == requests.codes.ok:
        doc = lxml.html.fromstring(response.content)
        elements = doc.xpath('//tr')
        columns = [col for col in elements[1].text_content().split('\n') if col]
        df = pd.DataFrame()
        for i in range(3,len(elements)):
            row_data = [[col] for col in elements[i].text_content().split('\n')]
            row_data = row_data[1:-1]
            d = dict(zip(columns,row_data))
            df = pd.concat([df,pd.DataFrame(d)])
        df['min_dist_to_coast'] = pd.to_numeric(df.min_dist_to_coast)
        df['max_intensity'] = pd.to_numeric(df.max_intensity)
        df['duration'] = pd.to_numeric(df.duration)
        df['max_area'] = pd.to_numeric(df.max_area)
        df['mean_intensity'] = pd.to_numeric(df.mean_intensity)
        # df = df[df.feature_name.str.contains('NEP')]
        df = df.reset_index(drop = True)
        df.index = pd.to_datetime(df.time)
        df = df.drop(columns = ['time'])
        df.to_csv(save_filepath)
    else:
        raise ConnectionError

        
def import_blobtracker_data():
    response = requests.get('https://oceanview.pfeg.noaa.gov/erddap/tabledap/cciea_OC_MHW_EV.htmlTable')
    if response.status_code == requests.codes.ok:
        doc = lxml.html.fromstring(response.content)
        elements = doc.xpath('//tr')
        columns = [col for col in elements[1].text_content().split('\n') if col]
        df = pd.DataFrame()
        for i in range(3,len(elements)):
            row_data = [[col] for col in elements[i].text_content().split('\n')]
            row_data = row_data[1:-1]
            d = dict(zip(columns,row_data))
            df = pd.concat([df,pd.DataFrame(d)])
        df['min_dist_to_coast'] = pd.to_numeric(df.min_dist_to_coast)
        df['max_intensity'] = pd.to_numeric(df.max_intensity)
        df['duration'] = pd.to_numeric(df.duration)
        df['max_area'] = pd.to_numeric(df.max_area)
        df['mean_intensity'] = pd.to_numeric(df.mean_intensity)
        # df = df[df.feature_name.str.contains('NEP')]
        df = df.reset_index(drop = True)
        df.index = pd.to_datetime(df.time)
        df = df.drop(columns = ['time'])
        return df
    else:
        raise ConnectionError


def load_blobtracker_data(filepath):
    df = pd.read_csv(filepath)
    return df
    
        
def download_srtm30(save_directory = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/noaa/", overwrite = False):
    os.makedirs(save_directory, exist_ok = True)
    filename = 'srtm30.nc'
    save_filepath = os.path.join(save_directory, filename)
    if os.path.isfile(save_filepath) and overwrite is False:
        return None
    NLAT = 55  # Most northern latitude.
    SLAT = 35  # Most southern latitude.
    WLON = -143 # Most western longitude.
    ELON = -123 # Most eastern longitude
    download_url = f'https://coastwatch.pfeg.noaa.gov/erddap/griddap/usgsCeSrtm30v1.nc?topo%5B({NLAT}):1:({SLAT})%5D%5B({WLON}):1:({ELON})%5D' 
    urllib.request.urlretrieve(download_url, save_filepath)
    return save_filepath