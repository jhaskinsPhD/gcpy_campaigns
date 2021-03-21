"""
Script to make ObsPack & Planelight.dat input files for individual campaigns.

Created on Sun Feb 14 19:25:16 2021

@author: Dr. Jessica D. Haskins
"""

import xarray as xr
import pandas as pd
import numpy as np 
import sys

sys.path.insert(0, 'C:\\Users\\jhask\\OneDrive\\Documents\\Research\\Projects\\MIT\\pOrgNO3\\code\\analysis\\gcpy_campaigns\\')
import write_obspack_inputs as obs
import write_planeflight_inputs as pln

# =============================================================================
# #########################  SENEX planeflight.date files  ####################
# =============================================================================

# Open SENEX merged data. Convert times to a pandas datetime array. 
senex="C:\\Users\\jhask\\OneDrive\\Documents\\Research\\Projects\\MIT\\pOrgNO3\\code\\campaign_merge_files\\SENEX.nc"
sn=xr.open_dataset(senex) 
dt=pd.to_datetime(sn.time.values).to_series().reset_index(drop=True)

#  OPTION 1:  Make a planeflight.dat file for all SENEX flights. Sample just NO, O3, CO. 
pln.make_planeflightdat_files(outpath='C:/Users/jhask/Desktop/SENEX1/',
                            datetimes=dt,
                            lat_arr=sn.GpsLat.values, 
                            lon_arr=sn.GpsLon.values, 
                            pres_arr=sn.StaticPrs.values,
                            campaign='SENEX',
                            tracers=['NO', 'O3', 'CO'],
                            username= 'jdh',
                            drop_dupes = False,
                            diags = ['all'])

#  OPTION 2:  Make a planeflight.dat file for all SENEX flights. 
# Sample all tracers in your input file and all optional diagnostics
pln.make_planeflightdat_files(outpath='C:/Users/jhask/Desktop/SENEX2/',
                            input_file='C:/Users/jhask/Desktop/input.geos.standard', 
                            campaign='SENEX',
                            datetimes=dt,
                            lat_arr=sn.GpsLat.values, 
                            lon_arr=sn.GpsLon.values, 
                            pres_arr=sn.StaticPrs.values,
                            username= 'jdh',
                            drop_dupes = False,
                            diags = ['all'],
                            print_diag_options= False)
 
#  OPTION 3:  Make a planeflight.dat file for all SENEX flights. 
# Sample all tracers in your input file except those in "minus". 
minus=["AODC_SULF","AODC_BLKC","AODC_ORGC","AODC_SALA","AODC_SALC",
"AODC_DUST","AODB_SULF","AODB_BLKC","AODB_ORGC","AODB_SALA","AODB_SALC",
"AODB_DUST","HG2_FRACG" ,"HG2_FRACP","GMAO_ICE00","GMAO_ICE10","GMAO_ICE20", 
"GMAO_ICE30", "GMAO_ICE40","GMAO_ICE50", "GMAO_ICE60","GMAO_ICE70", "GMAO_ICE80","GMAO_ICE90"]
pln.make_planeflightdat_files(outpath='C:/Users/jhask/Desktop/SENEX3/',
                            input_file='C:/Users/jhask/Desktop/input.geos.standard', 
                            campaign='SENEX',
                            datetimes=dt,
                            lat_arr=sn.GpsLat.values, 
                            lon_arr=sn.GpsLon.values, 
                            pres_arr=sn.StaticPrs.values,
                            username= 'jdh',
                            drop_dupes = False,
                            diags = ['all'],
                            diags_minus=minus,
                            print_diag_options= False)


# =============================================================================
#    ####################    SOAS Centreville  ObsPack ######################
# =============================================================================
# Create ObsPack files for the Centreville, Alabama site during SOAS 
# sampling the model there every hour of the campaign between 6/1/2013 and 7/15/2013.

filenames = obs.ground_make_ObsPack_Input_netcdfs('SOAS-Ground', lat=32.903281, 
                                      lon=-87.249942, alt=2,
                                      datestart='20130601 00:00:00',
                                      dateend='20130715 00:00:00', 
                                      samplefreq=3600,
                                      sample_stragety=2, 
                                      outpath='C:\\Users\\jhask\\Desktop\\SOAS\\')

# =============================================================================
#   ####################    SENEX ObsPack     #####################
# =============================================================================

# Open SENEX data to get lat, long, alt info. 
# Open SENEX merged data. Convert times to a pandas datetime array. 
senex="C:\\Users\\jhask\\OneDrive\\Documents\\Research\\Projects\\MIT\\pOrgNO3\\code\\campaign_merge_files\\SENEX.nc"
sn=xr.open_dataset(senex) 

# Make sure my alt, lat, lon, time data is formatted correctly: 
alt = sn.GpsAlt.values # Pull alt from ds
alt[alt < 0] = np.NaN  # Don't allow negatives. 
# Create smaller xarray with ONLY the data we need, drop any NaNs from it! 
sen =  xr.Dataset({'alt':xr.DataArray( data= alt , dims=['obs']), 
                      'lat':xr.DataArray( data= sn.GpsLat.values , dims=['obs']),
                      'lon':xr.DataArray( data= sn.GpsLon.values , dims=['obs']),
                      'time':xr.DataArray( data= sn.time.values , dims=['obs'])}).dropna(dim='obs')
# Get time to not be an index and not be weird. 
time= pd.to_datetime(sen.time.values).to_series().reset_index(drop=True)

# Now make ObsPack files for all flights: 
filenames = obs.flight_make_ObsPack_Input_netcdfs('SENEX',lat=sen.lat.values, 
                                                  lon=sen.lon.values,
                                                  alt=sen.alt.values,
                                                  time=time, 
                                                  sample_stragety=4,
                                                  outpath='C:\\Users\\jhask\\Desktop\\SENEX\\')

# =============================================================================
#############    Combine SENEX and SOAS files on common dates   ###############
# =============================================================================
# I want to sample GEOS-Chem at the SOAS Centerville site and 
# along the SENEX flight path during June- July of 2013. Some flights took
# place on the same days as continous ground monitoring, so we have mutliple files for 
# the same day which isn't allowed as input, so we need to combine them.
# (( You could seperate the output by either using the lat/lon of the ground site 
# or probably, easier, by filtering by the obspack_ID string (which is unique
# for those from SOAS vs those from SENEX.)))
    
#Folders to each of their indvidual ObsPack Files 
senex_folder = 'C:\\Users\\jhask\\Desktop\\SENEX\\'
soas_folder = 'C:\\Users\\jhask\\Desktop\\SOAS\\'
desktop = 'C:\\Users\\jhask\\Desktop\\both\\' # output folder for all files.

commons= obs.combine_common_ObsPacks(soas_folder, senex_folder, outpath=desktop, 
                            copy_not_common= True)

# Open a file and take a peek for sanity! 
t=xr.open_dataset(desktop+commons[0])

lat= t.latitude.values
lon= t.longitude.values
alt= t.altitude.values
tm= t.time_components.values
obspack_id= str(t.obspack_id.values)
sample= t.CT_sampling_strategy.values
