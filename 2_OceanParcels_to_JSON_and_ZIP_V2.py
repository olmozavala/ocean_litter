from __future__ import division
# https://docs.python.org/2/library/struct.html
import struct
import numpy as np
__author__="Olmo S. Zavala Romero"
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
import matplotlib.pyplot as plt

def createBinFiles():

    parts = 2
    times = 5

    info = F" a chis a chis a chis; {parts}, {times}"
    particles = (np.random.random((2,parts,times))*10000).astype(np.int16)
    print(F"Input \n\t txt: {info}  \n\t data: {particles}")

    file_name = 'test.bin'
    # -------- Writing to file ---------------
    f = open(file_name,'wb')
    text = struct.pack(F"{len(info)}s", bytes(info, 'utf-8'))
    f.write(text)
    f.write(particles.tobytes())
    f.close()

    # -------- Writing to file ---------------
    f = open(file_name,'rb')
    data = f.read(len(info))
    outputtxt = struct.unpack(F"{len(info)}s", data)
    data = f.read(parts*times*2*2)
    outputdata = struct.unpack(F"{parts*times*2}h", data)
    f.close()
    print(F"Output \n\t txt: {outputtxt[0]}  \n\t data: {outputdata}")

def createFiles():
    compression = zipfile.ZIP_DEFLATED
    all_reduce_particles_by = [1, 4, 6]
    min_number_particles = 20
    BEACHED = False  # Indicate if we are testing the beached particles

    def myfmt(r): # 'Round to 2 decimals'
        return float(F"{r:.2f}")
    vecfmt = np.vectorize(myfmt)

    config = get_op_config()

    # ------- Home ---------
    output_folder = config[WorldLitter.output_folder_web]
    input_folder = config[WorldLitter.output_folder]
    input_file = config[WorldLitter.output_file]

    countries_file_name = config[WorldLitter.countries_file]
    # Reading the json file with the names and geometries of the countries
    df_country_list = pd.read_csv(countries_file_name, index_col=0)

    # Reading the output from Ocean Parcles
    nc_file = Dataset(join(input_folder, input_file), "r", format="NETCDF4")

    print("----- Attributes ----")
    for name in nc_file.ncattrs():
        print(name, "=", getattr(nc_file, name))
    # plt.imshow(nc_file['beached'])
    # Print variables
    print("----- Variables ----")
    all_vars = nc_file.variables
    for name in all_vars.keys():
        print(name)

    glob_num_particles = nc_file.dimensions['traj'].size

    traj = all_vars['trajectory']
    time = all_vars['time']
    lat = all_vars['lat']
    lon = all_vars['lon']
    Z = all_vars['z']
    if BEACHED:
        beached = all_vars['beached']
        beached_count = all_vars['beached_count']

    # Iterate over the options to reduce the number of particles
    for reduce_particles_global in all_reduce_particles_by:
        final_ouput_folder = F"{output_folder}/{reduce_particles_global}"
        if not(os.path.exists(final_ouput_folder)):
            os.makedirs(final_ouput_folder)

        cur_idx = 0

        tot_assigned_particles = 0
        countries = {}
        # Iterate over each country
        for cur_country_name in df_country_list.index:
            print(F'-------- {cur_country_name} ----------')
            # First and last particle position
            particles_for_country_str = df_country_list.loc[cur_country_name]['idx_country'].replace(']','').replace('[','').split(',')
            particles_for_country = [int(x) for x in particles_for_country_str]

            tot_particles = len(particles_for_country)
            tot_assigned_particles += tot_particles
            reduce_particles_by_country = reduce_particles_global
            # If there are not enough particles then we need to reduce the 'separation' of particles
            while (((tot_particles / reduce_particles_by_country) < min_number_particles) and (
                    reduce_particles_by_country > 1)):
                reduce_particles_by_country -= 1

            red_particles_for_country = particles_for_country[::reduce_particles_by_country]

            # Append the particles
            cur_lat_all_part = lat[red_particles_for_country].filled()
            cur_lon_all_part = lon[red_particles_for_country].filled()
            if BEACHED:
                cur_beached_all_part = beached[red_particles_for_country].filled() == 4
                countries[cur_country_name] = {'lat_lon': [vecfmt(cur_lat_all_part).tolist(),
                                                           vecfmt(cur_lon_all_part).tolist()],
                                               'beached': [cur_beached_all_part.tolist()],
                                               'oceans': [x for x in df_country_list.loc[cur_country_name]['oceans'].split(';')],
                                               'continent': df_country_list.loc[cur_country_name]['continent']}
            else:
                countries[cur_country_name] = {'lat_lon': [vecfmt(cur_lat_all_part).tolist(),
                                                           vecfmt(cur_lon_all_part).tolist()],
                                               'oceans': [x for x in df_country_list.loc[cur_country_name]['oceans'].split(';')],
                                               'continent': df_country_list.loc[cur_country_name]['continent']}

            cur_idx += 3  # Hardcoded because the way the country list is made

        # ------------- Writing the binary file form the countries object --------------
        txt = ''
        bindata = b''
        for c_country in countries.keys():
            # name, continent, num_particles, num_timesteps
            txt += F"{c_country}, {countries[c_country]['continent']}, {len(countries[c_country]['lat_lon'][0])}, {len(countries[c_country]['lat_lon'][0][0])}\n"
            bindata += (np.array(countries[c_country]['lat_lon'][0])*100).astype(np.int16).tobytes()
            bindata += (np.array(countries[c_country]['lat_lon'][1])*100).astype(np.int16).tobytes()

        print(" Saving binary file .....")
        header_output_file = F"{final_ouput_folder}/{input_file.replace('.nc','')}.txt"
        binary_file = F"{final_ouput_folder}/{input_file.replace('.nc','')}.bin"
        zip_output_file = F"{final_ouput_folder}/{input_file.replace('.nc','')}.zip"
        # -------- Writing header file ---------------
        f = open(header_output_file,'w')
        f.write(txt)
        f.close()
        # -------- Writing binary file---------------
        f = open(binary_file,'wb')
        f.write(bindata)
        f.close()

        # -------- Writing zip file---------------
        print(" Saving zip file .....")
        with zipfile.ZipFile(zip_output_file, 'w') as zip_file:
            zip_file.write(binary_file)
        zip_file.close()
        print(F"Original particles {glob_num_particles} assigned: {tot_assigned_particles}")

    nc_file.close()


def testReadingFile():

    #-------- Reading file ---------
    # -------- This part is just to test the reading of a specific binary file
    header_file = "/var/www/html/data/4/YesWinds_YesDiffusion_NoUnbeaching_2010_01.txt"
    data_file = "/var/www/html/data/4/YesWinds_YesDiffusion_NoUnbeaching_2010_01.bin"
    f_header = open(header_file,'r')
    header_lines = f_header.readlines()

    f_data = open(data_file,'rb')
    for country_line in header_lines:
        split = country_line.split(',')
        name = split[0]
        continent = split[1]
        num_particles = int(split[2])
        time_steps = int(split[3])

        lats_bin = f_data.read(num_particles*time_steps*2)
        lons_bin = f_data.read(num_particles*time_steps*2)
        lats_int = struct.unpack(F"{num_particles*time_steps}h", lats_bin)
        lons_int = struct.unpack(F"{num_particles*time_steps}h", lons_bin)
        lats = np.array([lats_int])[0]/100
        lons = np.array([lons_int])[0]/100
        print(lats[0:3])
        print(lons[0:3])
        break

    f_data.close()
    f_header.close()

if __name__ == "__main__":
    createFiles()
    # testReadingFile()

