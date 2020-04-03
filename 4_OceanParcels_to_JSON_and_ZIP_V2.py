import numpy as np
from netCDF4 import Dataset
import os
from os.path import join
import json
import zipfile
import zlib
import pandas as pd
from utils.ParticlesByCountry import case1
from config.MainConfig import get_op_config
from config.params import WorldLitter


compression = zipfile.ZIP_DEFLATED

def myfmt(r): # 'Round to 2 decimals'
    return F"{r:.2f}"
vecfmt = np.vectorize(myfmt)

config = get_op_config()

# ------- Home ---------
output_folder = config[WorldLitter.output_folder_web]
input_folder = config[WorldLitter.output_folder]
input_file = config[WorldLitter.output_file]

countries_file_name = config[WorldLitter.countries_file]
df_country_list = pd.read_csv(countries_file_name, index_col=0)
df_country_list = df_country_list.dropna()

all_reduce_particles_by = [10, 8, 4]
min_number_particles = 20

# Iterate over the options to reduce the number of particles
for reduce_particles_global in all_reduce_particles_by:
    final_ouput_folder = F"{output_folder}/{reduce_particles_global}"
    if not(os.path.exists(final_ouput_folder)):
        os.makedirs(final_ouput_folder)

    nc_file = Dataset(join(input_folder, input_file), "r", format="NETCDF4")

    print("----- Attributes ----")
    for name in nc_file.ncattrs():
        print(name, "=", getattr(nc_file, name))

    # Print variables
    print("----- Variables ----")
    all_vars = nc_file.variables
    for name in all_vars.keys():
        print(name)

    tot_time_steps = nc_file.dimensions['obs'].size
    glob_num_particles = nc_file.dimensions['traj'].size
    print(F"Total number of timesteps: {tot_time_steps} Total number of particles: {tot_time_steps * glob_num_particles} ")

    # 4936, 731 (Asia)
    traj = all_vars['trajectory']
    time = all_vars['time']
    lat = all_vars['lat']
    lon = all_vars['lon']
    Z = all_vars['z']

    cur_idx = 0

    countries = {}
    # Iterate over each country
    tot_countries = df_country_list.size
    for cur_country_name in df_country_list.index:
        print(F'-------- {cur_country_name} ----------')
        # First and last particle position
        particles_for_country_str = df_country_list.loc[cur_country_name]['idx_country'].replace(']','').replace('[','').split(',')
        particles_for_country = [int(x) for x in particles_for_country_str]

        tot_particles = len(particles_for_country)
        reduce_particles_by_country = reduce_particles_global
        # If there are not enough particles then we need to reduce the 'separation' of particles
        while (((tot_particles / reduce_particles_by_country) < min_number_particles) and (
                reduce_particles_by_country > 1)):
            reduce_particles_by_country -= 1

        red_particles_for_country = particles_for_country[::reduce_particles_by_country]

        # Append the particles
        cur_lat_all_part = lat[red_particles_for_country].filled()
        cur_lon_all_part = lon[red_particles_for_country].filled()
        countries[cur_country_name] = {'lat_lon':[vecfmt(cur_lat_all_part).tolist(), vecfmt(cur_lon_all_part).tolist()],
                                       'oceans': [x for x in df_country_list.loc[cur_country_name]['oceans'].split(';')]}
        cur_idx += 3  # Hardcoded because the way the country list is made

    print(" Saving json file .....")
    json_txt = json.dumps(countries)
    merged_output_file = F"{final_ouput_folder}/world_{input_file.replace('.nc','')}.json"
    f = open(merged_output_file,"w+")
    f.write(json_txt)

    print(" Saving zip file .....")
    json_txt = json.dumps(countries)
    zip_file_name = merged_output_file.replace('json','zip')
    zf = zipfile.ZipFile(zip_file_name, mode='w')
    zf.write(merged_output_file, compress_type=compression)
    zf.close()
