import os
import sys
from datetime import datetime
import requests
import time
import shutil
from ormhw.core import BBox, L2_DIR

year = int(sys.argv[1])


def main():
    os.makedirs(L2_DIR, exist_ok = True)
    bdt = datetime(year,7,1)
    edt = datetime(year,10,15)
    remote_files = find_oc_files(bdt, edt, BBox)
    download_oc_files(remote_files)
    
    
    
def find_oc_files(begin_datetime, end_datetime, bounding_box):
    """
    Discover OC L2 files for a given day and area.
    """
    start_date = begin_datetime.strftime('%Y-%m-%d')
    end_date = end_datetime.strftime('%Y-%m-%d')
    base = 'https://cmr.earthdata.nasa.gov/search/granules.umm_json'
    params = {'page_size': 2000,
              'short_name': 'MODISA_L2_OC',
              'temporal': f'{start_date},{end_date}',
              'bounding_box': f"{bounding_box.lon_min},{bounding_box.lat_min},{bounding_box.lon_max},{bounding_box.lat_max}",
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



def download_oc_files(items, save_directory = L2_DIR, overwrite = False, verbose = True):
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
    


if __name__ == "__main__":
    main()