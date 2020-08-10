from parcels import Field
import os
from netCDF4 import Dataset
from os.path import join
from datetime import datetime
import numpy as np

def read_files(base_folder, years, wind=False, start_date=0, end_date=0):
    """ Reads the files based on the start and end date. Depending on the wind var, it decides which
    folder to read
    :param base_folder:
    :param years:
    :param wind:
    :param start_date:
    :param end_date:
    :return:
    """
    all_files = []
    for year in years:
        # 2019 — ocean current
        # 2019w — wind filed
        # 2019c — ocean current+1% wind combined
        if wind:
            c_year_path = join(base_folder, F'{year}c')
        else:
            c_year_path = join(base_folder, F'{year}')

        if os.path.exists(c_year_path):
            files = os.listdir(c_year_path)
            # Filtering just dates after initial date
            if start_date == 0:
                final_files = files
            else:
                final_files = []
                ds = [x.split('_')[3] for x in files]
                all_dates = [datetime(int(x[0:4]), int(x[4:6]), int(x[6:8]) ) for x in ds]
                for i, c_date in enumerate(all_dates):
                    if end_date != 0:
                        if start_date <= c_date <= end_date:
                            final_files.append(files[i])
                    else:
                        if c_date >= start_date:
                            final_files.append(files[i])

            for c_file in final_files:
                all_files.append(join(c_year_path, c_file))

    all_files.sort()
    return all_files

def add_unbeaching_field(field_set, lat, lon, input_file):
    """
    Adds the unbeaching field from the specified input_file into the current field_set
    :param field_set:
    :param lat:
    :param lon:
    :param input_file:
    :return:
    """
    ds = Dataset(input_file, "r+", format="NETCDF4")

    unBeachU= Field('unBeachU', ds['unBeachU'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_meridional', mesh='spherical', field_chunksize=(2048,2048))
    unBeachV= Field('unBeachV', ds['unBeachV'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_zonal', mesh='spherical', field_chunksize=(2048,2048))

    field_set.add_field(unBeachU, 'unBeachU')
    field_set.add_field(unBeachV, 'unBeachV')

def add_Kh(field_set, lat, lon, kh):
    """
    Adds constant diffusion coefficient to the fieldset
    :param field_set:
    :param lat:
    :param lon:
    :param kh:
    :return:
    """
    kh_mer = Field('Kh_meridional', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                   lon=lon, lat=lat, allow_time_extrapolation=True,
                   fieldtype='Kh_meridional', mesh='spherical', field_chunksize=(2048,2048))
    kh_zonal = Field('Kh_zonal', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                     lon=lon, lat=lat, allow_time_extrapolation=True,
                     fieldtype='Kh_zonal', mesh='spherical', field_chunksize=(2048,2048))

    field_set.add_field(kh_mer, 'Kh_meridional')
    field_set.add_field(kh_zonal, 'Kh_zonal')
