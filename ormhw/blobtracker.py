import lxml.html
import pandas as pd
import requests


def get_blobtracker() -> pd.DataFrame:
    """
    Import blobtracker (tabledap) and return as a Pandas dataframe.
    
    :return: A Pandas Dataframe containing Blobtracker data.
    """
    
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
        df = df.reset_index(drop = True)
        df.index = pd.to_datetime(df.time)
        df = df.drop(columns = ['time'])
        return df
    else:
        raise ConnectionError