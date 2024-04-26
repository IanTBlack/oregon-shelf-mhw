## Bloom Compression by Marine Heatwaves Contemporary With the Oregon Upwelling Season
## Black, I., Kavanaugh, M.T., and Reimers, C.E. -- In Revision
***
### Please use the repository [Issues](https://github.com/IanTBlack/oregon-shelf-mhw/issues) page for code issues or if items in this README need to be updated. All other correspondence can be directed toward Ian Black (blackia@oregonstate.edu).
***


### Project Installation
This project was built around the OOI JupyterHub. You can sign up for a free account [here](https://jupyter.oceanobservatories.org).

Steps
1. First navigate to your user directory (/home/jovyan).
    - `cd ~`
2. Clone this repository to your user directory.
    - `git clone https://github.com/IanTBlack/oregon-shelf-mhw.git`
3. Create a new virtual environment.
   - `cd ~`
   - `conda create -n ormhw python=3.11`
   - `conda activate ormhw`
   - `python -m ipykernel install --user --name ormhw --display-name "Python (ormhw)"`
4. Install ooijh. ooijh is a Python package specifically built for the OOI JupyterHub that streamlines data access and analysis of OOI datasets.
    - `cd ~`
    - `conda activate ormhw`
    - `git clone https://github.com/IanTBlack/ooijh.git`
    - `cd ooijh`
    - `pip install -r requirements.txt`
    - `pip install .`
5. Install required packages.
    - `cd ~`
    - `cd oregon-shelf-mhw`
    - `pip install -r requirements.txt`
    
***

## How To Rerun
Notebooks in the main project repository are ordered. It is expected that you run these notebooks in order if you are running this project for the first time. Many notebooks rely on data that was previously downloaded or curated by another notebook.

***

## Running Multiple Notebooks
By default, curating NASA data is done iteratively for each year, which can take about 24 hours. 
It is beneficial to run multiple notebooks at once. Simply copy the notebook and reassign a new year.
This will reduce processing time considerably.

***
    
## Datasets Used In Analysis
- [NOAA OISSTV2](https://psl.noaa.gov/data/gridded/data.noaa.oisst.v2.highres.html): 1983-2023
- [NASA MODIS-Aqua L2 Ocean Color](https://search.earthdata.nasa.gov/search/granules?portal=idn&p=C2330511440-OB_DAAC&pg[0][v]=f&pg[0][qt]=2015-04-01T00%3A00%3A00.000Z%2C2023-12-31T23%3A59%3A59.999Z&pg[0][gsk]=-start_date&q=Aqua&fi=MODIS&fdc=Ocean%2BBiology%2BDistributed%2BActive%2BArchive%2BCenter%2B%2528OB.DAAC%2529&fl=2%2B-%2BGeophys.%2BVariables%252C%2BSensor%2BCoordinates&gdf=NetCDF&tl=1713721830.004!3!!&lat=43.27790324375852&long=-144.80859375&zoom=4): 2015-2023
- [GEBCO 2023](https://www.gebco.net/data_and_products/gridded_bathymetry_data/#global): 2023
- [CUTI and BEUTI](https://mjacox.com/upwelling-indices/): 2015-2023


### OOI Datasets

#### Brief Intro to OOI Dataset Syntax
OOI datasets are identified by a site, node, instrument, method, and stream. These describe the spatial location (site), the logger (node, which can also be loosely used to identify the vertical location), the sensor, the data delivery method, and the data stream (most sensors have one data stream, but some datasets are split into scientific/engineering, which is where the stream id comes in). 

Example:
- site: CE01ISSM
- node: RID16
- instrument: 03-CTDBPC000
- method: recovered_host
- stream: ctdbp_cdef_dcl_instrument_recovered 

Below are THREDDS catalog links to the `recovered_host` datasets that were used in this study. Note that the [ooijh](https://github.com/IanTBlack/ooijh) package (under development) will automatically merge datasets that were delivered by different methods in order to achieve the most complete time-series.

- [OOI CE01ISSM 7M CTD](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE01ISSM-RID16-03-CTDBPC000-recovered_host-ctdbp_cdef_dcl_instrument_recovered/catalog.html)
- [OOI CE02SHSM 7M CTD](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE02SHSM-RID27-03-CTDBPC000-recovered_host-ctdbp_cdef_dcl_instrument_recovered/catalog.html)
- [OOI CE04OSSM 7M CTD](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE04OSSM-RID27-03-CTDBPC000-recovered_host-ctdbp_cdef_dcl_instrument_recovered/catalog.html)
- [OOI CE01ISSM 7M Fluorometer](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE01ISSM-RID16-02-FLORTD000-recovered_host-flort_sample/catalog.html)
- [OOI CE02SHSM 7M Fluorometer](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE02SHSM-RID27-02-FLORTD000-recovered_host-flort_sample/catalog.html)
- [OOI CE04OSSM 7M Fluorometer](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/CE04OSSM-RID27-02-FLORTD000-recovered_host-flort_sample/catalog.html)
- [All OOI Datasets](https://thredds.dataexplorer.oceanobservatories.org/thredds/catalog/ooigoldcopy/public/catalog.html)

Additional information about each platform can be found in the list below.
- [CE01ISSM](https://oceanobservatories.org/site/ce01issm/)
- [CE02SHSM](https://oceanobservatories.org/site/ce02shsm/)
- [CE04OSSM](https://oceanobservatories.org/site/ce04ossm/)
- [All OOI Coastal Endurance Array Platforms](https://oceanobservatories.org/array/coastal-endurance/)

***
## Downloading Data
The provided notebooks will automatically download files, with two exceptions.
1. The CUTI/BEUTI dataset must be manually downloaded and then reuploaded to the OOI JupyterHub.
2. The NASA data requests require login information input into a `.netrc` file within the user directory.
- `machine urs.earthdata.nasa.gov`
- `login your-login-here`
- `password your-password-here`