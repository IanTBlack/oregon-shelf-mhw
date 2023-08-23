import pandas as pd
import xarray as xr

def drop_variables(obj, variables):
    """
    Drop any variables in the given data object that that are provided as a list or tuple. 
    
    Input can be a Pandas dataframe or an Xarray dataset.
    """
    if isinstance(obj, xr.Dataset):
        obj = obj.drop(variables, errors = 'ignore')
    elif isinstance(obj, pd.DataFrame):
        obj = obj.drop(columns = variables, errors = 'ignore')
    return obj

def drop_qc_variables(obj):
    """
    Drop any variables that have 'qc_' in the variable name. The corresponding data variable is retained.
    For example, 'temperature_qc_results' would be removed.
    
    Input can be a Pandas dataframe or an Xarray dataset.
    """
    if isinstance(obj, xr.Dataset):
        variables = obj.data_vars
        qc_vars = [v for v in variables if 'qc_' in v]
        obj = obj.drop(qc_vars, errors = 'ignore')
    elif isinstance(obj, pd.DataFrame):
        variables = obj.columns
        qc_vars = [v for v in variables if 'qc_' in v]
        obj = obj.drop(columns = qc_vars, errors = 'ignore')
    return obj 

def drop_qartod_variables(obj):
    """
    Drop any variables that have 'qartod_' in the variable name. The corresponding data variable is retained.
    For example, 'temperature_qartod_results' would be removed.
    
    Input can be a Pandas dataframe or an Xarray dataset.
    """
    if isinstance(obj, xr.Dataset):
        variables = obj.data_vars
        qc_vars = [v for v in variables if 'qartod_' in v]
        obj = obj.drop(qc_vars, errors = 'ignore')
    elif isinstance(obj, pd.DataFrame):
        variables = obj.columns
        qc_vars = [v for v in variables if 'qartod_' in v]
        obj = obj.drop(columns = qc_vars, errors = 'ignore')
    return obj 



class DROPS: 
    """
    A class for defining keywords that are used to drop ancillary datasets or variables of no use.
    """
    
    DATASET_KW = ['metadata', 'dark', 'hourly', 'calibration_coeff', 'cal', 
                  'no_config', 'no_hardware', 'no_status', 'optaa_status', 
                  'diagnostics', 'blank', 'power', 'cd_data_header', 'cd_system_data', 'status']
    
    
    COMMON = ['preferred_timestamp', 'driver_timestamp', 'port_timestamp',
              'profiler_timestamp', 'id', 'provenance',
              'internal_timestamp', 'ingestion_timestamp', 'deployment',
              'suspect_timestamp', 'dcl_controller_timestamp','obs']
    
    METBK = ['met_windavg_mag_corr_east', 'sea_surface_conductivity',
             'met_spechum', 'met_windavg_mag_corr_north',
             'met_netlirr_minute', 'longwave_irradiance',
             'met_heatflx_minute','precipitation','met_sensflx_minute',
             'met_latnflx_minute','barometric_pressure','relative_humidity']
    
    FLORT = ['raw_signal_cdom','measurement_wavelength_beta','optical_backscatter',
             'measurement_wavelength_chl','seawater_scattering_coefficient','raw_signal_beta',
            'raw_signal_chl','sea_water_practical_salinity','raw_internal_temp',
             'total_volume_scattering_coefficient','measurement_wavelength_cdom','sea_water_temperature',
             'signal_1_scale_factor','signal_3_offset','signal_2_scale_factor','signal_3_scale_factor',
             'signal_1_offset','signal_2_offset','time_string','date_string']
    
    NUTNR = ['wavelength','nutnr_spectrum_average','nutnr_fit_base_2','nutnr_fit_base_1',
             'nutnr_current_main','voltage_main','spectral_channels','frame_type','temp_spectrometer','temp_lamp',
             'nutnr_nitrogen_in_nitrate','nitrate_concentration','nutnr_absorbance_at_350_nm',
             'nutnr_absorbance_at_254_nm','temp_interior','nutnr_bromide_trace','nutnr_integration_time_factor','lamp_time',
             'sea_water_practical_salinity','time_of_sample','serial_number','sea_water_temperature','nutnr_voltage_int','date_of_sample',
             'checksum','humidity','nutnr_fit_rmse','nutnr_dark_value_used_for_fit','aux_fitting_1','aux_fitting_2','voltage_lamp']