from datetime import datetime, timezone
import dateutil
import fsspec
import gsw
import numpy as np
import pandas as pd
import xarray as xr
import os
import re
import requests
import shutil
import time

from ormhw.drops import DROPS, drop_variables, drop_qc_variables, drop_qartod_variables
from ormhw.processing import get_windstress, get_SA_CT_rho_spiciness, process_metbk, process_flort, process_ctd, process_nutnr

class KDATA():
    def __init__(self, site, node, instrument, stream, 
                 bdt = datetime(2014,1,1,0,0,0), edt = datetime(2035,12,31,23,59,59)):
        self._local = fsspec.filesystem('file')
        self.base = f"{os.path.expanduser('~')}/ooi/kdata"
        self.files = self.get_files(site.upper(), node.upper(), instrument.upper(), stream.lower(), bdt, edt)
  
    def get_files(self, site, node, instrument, stream , bdt, edt):
        matching_directories = self.find_dataset_directories(site, node, instrument,stream)
        dataset_filepaths = []
        for matching_directory in matching_directories:
            matching_filepaths = self.find_dataset_filepaths(matching_directory)
            sorted_filepaths = self.sort_dataset_filepaths(matching_filepaths, bdt, edt)
            dataset_filepaths.append(sorted_filepaths)
        dataset_filepaths = [fp for dfp in dataset_filepaths for fp in dfp]
        return dataset_filepaths
                 
    def find_dataset_directories(self, site, node, instrument, stream):
        matching_directories = self._local.glob(f"{self.base}/*{site}*{node}*{instrument}*{stream}*")
        for kw in DROPS.DATASET_KW:
            matching_directories = [mf for mf in matching_directories if kw not in mf]
        return matching_directories
    
    def find_dataset_filepaths(self, dataset_path):
        snims = dataset_path.split("/")[-1]
        site, node, inst_num, inst_id, method, stream = snims.split('-')
        matching_filepaths = self._local.glob(f"{dataset_path}/*{site}*{node}*{inst_num}-{inst_id}*{method}*{stream}*.nc")
        self.site,self.node, self.instrument, self.stream = (site, node, '-'.join((inst_num, inst_id)), stream)
        return matching_filepaths
    
    def sort_dataset_filepaths(self, matching_filepaths, bdt, edt):
        sorted_filepaths = []
        for fp in matching_filepaths:
            file_begin, file_end = [datetime.strptime(dt,'%Y%m%dT%H%M%S') for dt in re.findall("(\d{8}T\d{6})",fp)]
            if (file_begin <= bdt <= file_end or file_begin <= edt <= file_end or 
                bdt <= file_begin <= edt or bdt <= file_end <= edt):
                sorted_filepaths.append(fp)
        return sorted_filepaths
        
        
        
class THREDDS():
    def __init__(self, site, node, instrument, stream,
                bdt = datetime(2014,1,1,0,0,0), edt = datetime(2035,12,31,23,59,59)):
        self.site, self.node, self.instrument, self.stream = site.upper(), node.upper(), instrument.upper(), stream.lower()
        self.bdt, self.edt = bdt, edt
        self.urls = self.find_urls()
        
    def get_base_catalog(self):
        base_catalog_url = "https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/catalog.html"
        txt = requests.get(base_catalog_url).text
        pattern = r'href=\'(.*?)/catalog.html'
        base_catalog =[x for x in list(np.unique(re.findall(pattern, txt))) if 'thredds' not in x]
        return base_catalog
    
    def find_matching_refdes(self):
        base_catalog = self.get_base_catalog()
        matching_refdes = []
        pattern = f'({self.site}.*?{self.node}.*?{self.instrument}.*?{self.stream}.*)'
        for refdes in base_catalog:
            try:
                match = re.findall(pattern, refdes)[0]
                for kw in DROPS.DATASET_KW:
                    if kw in match:
                        continue
                    else:
                        matching_refdes.append(match)
            except:
                continue
        else:
            return matching_refdes
    
    def get_refdes_catalog(self,refdes):
        rd = refdes.split('-')
        site, node, instrument, method, stream = rd[0], rd[1], '-'.join((rd[2],rd[3])), rd[4], rd[5]
        self.site, self.node, self.instrument, self.stream = site, node, instrument, stream
        refdes_catalog_url = f'https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/{refdes}/catalog.html'
        txt = requests.get(refdes_catalog_url).text        
        pattern = r'dataset=(ooigoldcopy.*?\.nc)\''
        refdes_catalog = list(np.unique(re.findall(pattern, txt)))   
        matching_refdes_catalog = []
        for rds in refdes_catalog:
            ds_split = rds.split('/')
            if instrument not in ds_split[-1]:
                continue
            else:
                matching_refdes_catalog.append(rds)
        return matching_refdes_catalog
    
    
    def find_matching_deployments(self,refdes_catalog):
        matching_deployments = []
        for rds in refdes_catalog:
            ds_split = rds.split('/')[-1]
            t_split = ds_split.split('_')[-1].replace('.nc','')
            file_bdt_str, file_edt_str = t_split.split('-')
            file_bdt, file_edt = dateutil.parser.parse(file_bdt_str), dateutil.parser.parse(file_edt_str)
            if (self.bdt <= file_bdt <= self.edt or self.bdt <= file_edt <= self.edt 
                or file_bdt <= self.bdt <= file_edt or file_bdt <= self.edt <= file_edt):
                matching_deployments.append(rds)
        return matching_deployments
            
    
    def find_urls(self):
        thredds_base_url = 'https://thredds.dataexplorer.oceanobservatories.org/thredds/fileServer/'
        matching_refdes = self.find_matching_refdes()
        ncs = []
        for mrd in matching_refdes:
            rdc = self.get_refdes_catalog(mrd)
            matching_deployments = self.find_matching_deployments(rdc)
            ncs.append(matching_deployments)
        ncs = [j for i in ncs for j in i]
        ncs = [requests.compat.urljoin(thredds_base_url, nc) for nc in ncs]        
        return ncs
            
    def download_files(self, save_directory = f"{os.path.expanduser('~')}/oregon-shelf-mhw/data/ooi/", overwrite = True):
        os.makedirs(save_directory, exist_ok = True)
        downloaded_files = []
        if self.urls == []:
            _ = '-'.join((self.site, self.node, self.instrument, '*',self.stream))
            print('-------------------------------')
            print(f'No files found for given refdes and datetimes.')
            print(_)
            print(self.bdt, self.edt)
            print('-------------------------------')
            return None
        for url in self.urls:
            save_filename = url.split('/')[-1]
            save_filepath = os.path.normpath(os.path.join(save_directory, save_filename))
            if os.path.isfile(save_filepath) and overwrite is False:
                downloaded_files.append(save_filepath)
                continue
            else:
                with requests.get(url, stream = True) as req:
                    time.sleep(0.01)
                    with open(save_filepath, 'wb') as f:
                        shutil.copyfileobj(req.raw, f)
                if not os.path.isfile(save_filepath):
                    raise FileNotFoundError
                else:
                    downloaded_files.append(save_filepath)
                    print(f"Downloaded {url} to {save_filepath}.")
        return downloaded_files
        
        
class GoldCopy():
    def __init__(self, site, node, instrument, stream,
                bdt = datetime(2014,1,1,0,0,0), edt = datetime(2035,12,31,23,59,59), data_directory = None):
        user_home = os.path.expanduser('~')
        if 'jovyan' in user_home:
            REPO = KDATA(site,node,instrument, stream, bdt, edt)
            self.files = REPO.files
        else:
            REPO = THREDDS(site,node, instrument,stream, bdt, edt)
            if data_directory is None:
                self.files = REPO.download_files(overwrite = False)

            else:
                self.files = REPO.download_files(save_directory = data_directory, overwrite = False)
        self.site, self.node, self.instrument, self.stream = REPO.site, REPO.node, REPO.instrument, REPO.stream


    def import_file(self, filepath):
        ds = xr.open_dataset(filepath)
        df = ds.to_dataframe()
        df = df.reset_index()
        df.index = df.time
        df = df.drop(columns = ['time'])
        df = drop_variables(df, DROPS.COMMON)
        df = drop_qc_variables(df)
        
        df = self.nan_by_qartod(df)
        df = drop_qartod_variables(df)
        
        if 'lat' not in df.columns: 
            df['lat'] = np.array([np.unique(ds.lat)] * len(df))
        if 'lon' not in df.columns: 
            df['lon'] = np.array([np.unique(ds.lon)] * len(df))
        
        if 'METBK' in self.instrument:
            df = drop_variables(df, DROPS.METBK)
        elif 'FLORT' in self.instrument:
            df = drop_variables(df, DROPS.FLORT)
        elif 'NUTNR' in self.instrument:
            df = drop_variables(df, DROPS.NUTNR)
        return df
        
        
    def nan_by_qartod(self, df, nan_flags = [4,9], variables = 'all', handle_confusion = True):
        if variables == 'all':
            qecs = [v for v in list(df.columns) if 'qartod_executed' in v]
        else:
            qecs = [v + '_qartod_executed' for v in variables]
        for qec in qecs:
            qdc = qec.split('_qartod_executed')[0]
            qrc = qdc + '_qartod_results'   
            df[qdc] = df[qdc].where(df[qec] != 1 & ~df[qrc].isin(nan_flags), np.nan)
            if handle_confusion is True:
                df[qdc] = df[qdc].where(~df[qec].isin([3, 4]), np.nan)
        return df
        
        
    def import_files(self, filepaths):
        dfs = []
        for filepath in filepaths:
            _df = self.import_file(filepath)
            dfs.append(_df)    
        mdf = pd.concat(dfs)
        mdf = mdf.drop_duplicates()
        return mdf
        
        
    def data(self, resample = 'auto'):
        mdf = self.import_files(self.files)
        if 'METBK' in self.instrument:
            mdf = process_metbk(mdf)
        elif 'FLORT' in self.instrument:
            mdf = process_flort(mdf)
        elif 'CTD' in self.instrument:
            mdf = process_ctd(mdf)
        elif 'NUTNR' in self.instrument:
            mdf = process_nutnr(mdf)
        
        if resample == 'auto':
            if 'SBD' in self.node or 'RID' in self.node:
                mdf = mdf.resample('3H').mean()
            elif 'SP' in self.node or 'SF' in self.node: 
                mdf = mdf.resample('3S').mean()
        elif resample is None:
            pass
        elif resample is not None and resample != 'auto':
            mdf = mdf.resample(resample).mean()
        
        return mdf
        