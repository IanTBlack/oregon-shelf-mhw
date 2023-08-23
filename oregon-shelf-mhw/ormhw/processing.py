import gsw
import numpy as np
import pandas as pd
import xarray as xr


def get_windstress(velocity, direction, rho_air = 1.225, kappa = 0.4, sensor_height = 3):
    theta = direction * np.pi/180
    u = velocity * np.sin(theta)
    v = velocity * np.cos(theta)
    cdn = (0.49 + 0.65 * velocity) * 10**-3
    cdn = np.where(velocity < 11, 1.2 * 10**-3, cdn)
    a = np.log(sensor_height/10)/kappa
    U10 = velocity/(1+ a * np.sqrt(cdn))  
    tau = rho_air * cdn * U10 **2
    tau_x = rho_air * cdn * U10 * u
    tau_y = rho_air * cdn * U10 * v
    return (tau, tau_x, tau_y)


def get_SA_CT_rho_spiciness(S, T, P , lat, lon):
    SA = gsw.SA_from_SP(S, lon = lon, lat = lat, p = P)
    CT = gsw.CT_from_t(SA, T, p = P)
    rho = gsw.density.rho(SA, CT, p = P)
    spiciness = gsw.spiciness0(SA,CT)
    return (SA,CT,rho,spiciness)



def process_metbk(df):
    if 'ct_depth' in df.columns:
        P = gsw.p_from_z(np.array(-1 * df.ct_depth),np.array(df.lat))
    else:
        P = 0
        
    
    df['met_salsurf'] = df['met_salsurf'].where(df['met_salsurf'] > 2, np.nan)
    df['met_salsurf'] = df['met_salsurf'].where(df['met_salsurf'] < 42, np.nan)
    
    df['sea_surface_temperature'] = df['sea_surface_temperature'].where(df['sea_surface_temperature'] > 0, np.nan)
    df['sea_surface_temperature'] = df['sea_surface_temperature'].where(df['sea_surface_temperature'] < 35, np.nan)
     
        
        
    df['met_relwind_speed'] = df['met_relwind_speed'].where(df['met_relwind_speed'] < 1000, np.nan)
        
    df['SA'], df['CT'], df['rho'],df['spiciness'] = get_SA_CT_rho_spiciness(np.array(df.met_salsurf), np.array(df.sea_surface_temperature), P, np.array(df.lat), np.array(df.lon))
    
    
    df['tau'], df['tau_x'], df['tau_y'] = get_windstress(df.met_relwind_speed, df.met_relwind_direction)  
    
    df['tau_y'] = df['tau_y'].where(df['tau_y'] < 10, np.nan)
    df['tau_y'] = df['tau_y'].where(df['tau_y'] > -10, np.nan)
    
    df['tau_x'] = df['tau_x'].where(df['tau_x'] < 10, np.nan)
    df['tau_x'] = df['tau_x'].where(df['tau_x'] > -10, np.nan)
    
    df['barometric_pressure'] = df.met_barpres * 0.01
    df['sirr'] = df.met_netsirr
    df['current_vel'] = df.met_current_speed
    df['current_dir'] = df.met_current_direction
    
    df = df[['tau','tau_x','tau_y','SA','CT','rho','spiciness','air_temperature','lat','lon','barometric_pressure','sirr','current_vel','current_dir']]
    return df



def process_flort(df):
    df['fluorometric_chlorophyll_a'] = df['fluorometric_chlorophyll_a'].where(df['fluorometric_chlorophyll_a'] > 0, np.nan)
    df['fluorometric_chlorophyll_a'] = df['fluorometric_chlorophyll_a'].where(df['fluorometric_chlorophyll_a'] < 50, np.nan)
    df['fluorometric_cdom'] = df['fluorometric_cdom'].where(df['fluorometric_cdom'] > 0, np.nan)
    df['fluorometric_cdom'] = df['fluorometric_cdom'].where(df['fluorometric_cdom'] < 500, np.nan)
    
    df['fchla'] = df['fluorometric_chlorophyll_a']
    df['fdom'] = df['fluorometric_cdom']
    
    if 'pressure' in df.columns:
        D = gsw.z_from_p(np.array(df['pressure']),np.array(df.lat)) * -1
        df['depth'] = D
        df = df[['fchla','fdom','depth']]
    elif 'int_ctd_pressure' in df.columns:
        D = gsw.z_from_p(np.array(df['int_ctd_pressure']),np.array(df.lat)) * -1
        df['depth'] = D
        df = df[['fchla','fdom','depth']]
    else:
        df = df[['fchla','fdom']]
    return df



def process_ctd(df):
    if 'sea_water_pressure' in df.columns:
        P = np.array(df.sea_water_pressure)
    else:
        print(df.columns)
        raise ValueError
        
    D = gsw.z_from_p(P,np.array(df.lat)) * -1
    df['depth'] = D        
    
    df['sea_water_practical_salinity'] = df['sea_water_practical_salinity'].where(df['sea_water_practical_salinity'] > 2, np.nan)
    df['sea_water_practical_salinity'] = df['sea_water_practical_salinity'].where(df['sea_water_practical_salinity'] < 42, np.nan)
    
    df['sea_water_temperature'] = df['sea_water_temperature'].where(df['sea_water_temperature'] > 0, np.nan)
    df['sea_water_temperature'] = df['sea_water_temperature'].where(df['sea_water_temperature'] < 35, np.nan)
     
    df['SA'], df['CT'], df['rho'],df['spiciness'] = get_SA_CT_rho_spiciness(np.array(df.sea_water_practical_salinity), np.array(df.sea_water_temperature), P, np.array(df.lat), np.array(df.lon))
    
    df = df[['SA','CT','rho','spiciness','depth']]
    
    return df


def process_nutnr(df):      
    df['salinity_corrected_nitrate'] = df['salinity_corrected_nitrate'].where(df['salinity_corrected_nitrate'] > 0, np.nan)
    df['salinity_corrected_nitrate'] = df['salinity_corrected_nitrate'].where(df['salinity_corrected_nitrate'] < 50, np.nan)
    
    df['nitrate'] = df['salinity_corrected_nitrate']
    
    if 'int_ctd_pressure' in df.columns:
        P = np.array(df.int_ctd_pressure)
        D = gsw.z_from_p(np.array(df['pressure']),np.array(df.lat)) * -1
        df['depth'] = D   
        df = df[['nitrate','depth']]
    else:
        df = df[['nitrate']]
    return df