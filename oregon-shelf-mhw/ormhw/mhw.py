from datetime import datetime
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import os
import pandas as pd
import xarray as xr
import math


def get_90th_percentile(ds):
    """Compute the historic daily 90th percentile."""
    
    ds['yd'] =  ds.time.dt.dayofyear
    ds90 = xr.Dataset()
    for j in range(1,367):
        _dsyd = ds.where(ds.yd == j, drop = True)
        _ds90 = float(np.round(np.nanpercentile(_dsyd.sst,[90]),2))
        d = {'yd': j, 'sst': _ds90}
        ds90 = xr.concat([ds90,xr.Dataset(d)], dim = 'time')
    return ds90


def find_mhws(ds,dsclim,ds90):
    """Identify MHWs using the climatology and daily 90th percentile."""
    years = range(1983,2023)
    all_events = pd.DataFrame()
    for year in years:
        days_above = []
        yds = ds.sel(time=slice(f"{year}-01-01",f"{year}-12-31"))

        # Identify days above 90th percentile.
        for j in yds.yd.values:
            y = yds.where(yds.yd == j, drop = True).sst.values
            p = ds90.where(ds90.yd == j,drop = True).sst.values
            if float(y) >= float(p):
                days_above.append(j)
                

        # Identify Events
        j = 1
        year_events = pd.DataFrame()
        for k, g in groupby(enumerate(days_above), lambda ix: ix[0]-ix[1]):
            days = list(map(itemgetter(1), g))
            if max(days) - min(days) >= 5:
                flag = 'mhw'
            else:
                flag = 'spike'
                # j += 1
                continue
            d = {'year': [year], 'event': [j], 'category': [flag],
                 'D': [max(days) - min(days)], 'Ts': [min(days)], 'Te': [max(days)]}
            _df = pd.DataFrame(d)
            year_events = pd.concat([year_events,_df])
            j += 1       

        # Combine events if there is a 2 day or less gap.
        cleaned_year_events = pd.DataFrame()
        if len(year_events) == 0:
            continue
        elif year_events.event.max() == 1:
            entry  = {'year': [year], 'Ts': [int(year_events.Ts.iloc[0])], 'Te': [int(year_events.Te.iloc[0])], 'D' : [int(year_events.Te.iloc[0] - year_events.Ts.iloc[0])], 'event': int(year_events.event.iloc[0]),'category':['mhw']}
            cleaned_year_events = pd.DataFrame(entry)
        else:
            year_events = year_events.reset_index(drop = True)
            for idx in range(len(year_events)):
                if idx >= year_events.index.max():
                    cleaned_year_events = pd.concat([cleaned_year_events,e1])
                    break
                if idx == 0:
                    e1 = year_events[year_events.index == idx]
                    e2 = year_events[year_events.index == idx + 1]
                if e2.empty:
                    cleaned_year_events = pd.concat([cleaned_year_events,e1])
                    break
                if int(e2.Ts.values) - int(e1.Te.values) <=2:
                    entry  = {'year': [year], 'Ts': [int(e1.Ts.iloc[0])], 'Te': [int(e2.Te.iloc[0])], 'D' : [int(e2.Te.iloc[0] - e2.Ts.iloc[0])], 'event': int(e1.event.iloc[0]),'category':['mhw']}
                    _df = pd.DataFrame(entry)
                    e1 = _df
                    e2 = year_events[year_events.index == idx + 2]
                    #cleaned_year_events = pd.concat([cleaned_year_events,_df])
                else:
                    cleaned_year_events = pd.concat([cleaned_year_events,e1])
                    e1 = year_events[year_events.index == idx + 1]
                    e2 = year_events[year_events.index == idx + 2]
        
        # Recompute duration because the above for loop is not optimized.  
        cleaned_year_events['D'] = cleaned_year_events['Te'] - cleaned_year_events['Ts'] 
                        
        # Reindex events.
        num_events = len(cleaned_year_events)
        cleaned_year_events['event'] = list(range(1,num_events + 1))
        all_events = pd.concat([all_events, cleaned_year_events])

    all_events = all_events.reset_index(drop = True)
    df = ds.to_dataframe()
    climatology = dsclim.to_dataframe()
    
    imaxs = []
    imeans = []
    ronsets = []
    rdeclines = []
    ivars = []
    for idx, row in all_events.iterrows():
        ydf = df[(df.index >= datetime(row.year,1,1)) & (df.index <= datetime(row.year,12,31))]
        _df = ydf[(ydf.yd >= row.Ts) & (ydf.yd <= row.Te)]
        _cdf = climatology[(climatology.index >= row.Ts) & (climatology.index <= row.Te)]
        imax = np.float64(np.max(np.array(_df.sst) - np.array(_cdf.sst)))
        imaxs.append(imax)
        imean = np.mean(np.array(_df.sst) - np.array(_cdf.sst))
        imeans.append(imean)
        Tmax = np.float64(_df.sst.max())
        Ts = np.float64(_df.sst[_df.yd == _df.yd.min()])
        Cs = np.float64(_cdf.sst[_cdf.index == _cdf.index.min()])
        Te = np.float64(_df.sst[_df.yd == _df.yd.max()])
        Ce = np.float64(_cdf.sst[_cdf.index == _cdf.index.max()])
        ivar = np.std(_df.sst)
        ivars.append(ivar)
        ronset = (imax - (Ts - Cs))/((Tmax - Ts))
        if math.isinf(ronset):
            ronset = 0
        ronsets.append(ronset)
        rdecline = (imax - (Te - Ce))/(Te - Tmax)
        rdeclines.append(rdecline)
    all_events['imax'] = imaxs
    all_events['imean'] = imeans
    all_events['ivar'] = ivars
    all_events['ronset'] = ronsets
    all_events['rdecline'] = rdeclines
    return all_events

