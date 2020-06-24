from datetime import datetime
from os.path import join
from netCDF4 import Dataset
import numpy as np
import functools
# from parcels.scripts.plottrajectoriesfile import plotTrajectoriesFile
import json
import matplotlib.pyplot as plt
import multiprocessing as mp
from matplotlib import cm
import cartopy.crs as ccrs
import matplotlib as mpl

from config.MainConfig import get_op_config
from config.params import WorldLitter
# -------------- Plot with OP ---------------

def plotDataOZ(file_name):
    # -------------- Info about variables ---------------
    ds = Dataset(file_name, "r+", format="NETCDF4")
    this_many = 10
    # print(F"Variables: {ds.variables.keys()}")
    # print(F"Trajectory: {ds.variables['trajectory'].shape}:{ds.variables['trajectory'][0:this_many]}")
    # print(F"time: {ds.variables['time'].shape}:{ds.variables['time'][0:this_many]}")
    # print(F"lat: {ds.variables['lat'].shape}:{ds.variables['lat'][0:this_many]}")
    # print(F"lon: {ds.variables['lon'].shape}:{ds.variables['lon'][0:this_many]}")
    # print(F"z: {ds.variables['z'].shape}:{ds.variables['z'][0:this_many]}")
    # print(F"beached: {ds.variables['beached'].shape}:{ds.variables['beached'][0:this_many]}")
    # print(F"beached_count: {ds.variables['beached_count'].shape}:{ds.variables['beached_count'][0:this_many]}")

    tot_times = ds.variables['trajectory'].shape[1]
    # for c_time_step in np.arange(0,tot_times,1):
    for c_time_step in np.arange(11,tot_times,1):
        print(F"------------------ {c_time_step} ----------------------")
        fig = plt.figure(figsize=(20,10))

        lats = ds.variables['lat'][:,c_time_step]
        lons = ds.variables['lon'][:,c_time_step]
        beached = ds.variables['beached'][:,c_time_step]
        beached_count = ds.variables['beached_count'][:,c_time_step]
        trajectory = ds.variables['trajectory'][:,c_time_step]

        id0 = beached == 0
        id1 = beached == 1
        id2 = beached == 2

        if c_time_step == 11:
            id3 = beached == 3
            id4 = beached == 4
        else:
            id3 = np.logical_or(id3, beached == 3)
            id4 = np.logical_or(id4, beached == 4)
            id4 = np.logical_or(id4, beached.mask)

        print(beached[id4])
        print(beached_count[id4])
        print(trajectory[id4])

        title = F'Current time step: {c_time_step}'
        # plotScatter(lats[id0], lons[id0], 'b', title)
        # plotScatter(lats[id1], lons[id1], 'r', title)
        # plotScatter(lats[id2], lons[id2], 'g', title)
        # plotScatter(lats[id3], lons[id3], 'm', title)
        plotScatter(lats[id4], lons[id4], 'y', title)
        # plt.show()
        # plt.close()


def plotScatter(lats, lons, color='b',title=''):
    ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.scatter(lons, lats, color=color)
    ax.coastlines()
    ax.set_title(title, fontsize=30)
    # plt.savefig(file_name.replace('json','png'), bbox_inches='tight')

def plotJsonFile(file_name):
    with open(file_name) as f:
        data = json.load(f)
        tot_times = len(data['Yemen']['lat_lon'][0][0])
        print(F"Total times in this file: {tot_times}")
        for c_time_step in np.arange(0,tot_times,1):
            print(c_time_step)
            fig = plt.figure(figsize=(20,10))
            ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
            lats = []
            lons = []
            for c_country in data:
                c_data = np.array(data[c_country]['lat_lon'])
                c_lats = c_data[0,:,c_time_step]
                c_lons = c_data[1,:,c_time_step]
                lats.extend(c_lats)
                lons.extend(c_lons)

            ax.scatter(lons, lats)
            ax.coastlines()
            ax.set_title(F'Current time step: {c_time_step}', fontsize=30)
            # plt.savefig(file_name.replace('json','png'), bbox_inches='tight')
            plt.show()
            plt.close()

if __name__ == "__main__":
    config = get_op_config()

    input_folder = config[WorldLitter.output_folder]
    input_file = config[WorldLitter.output_file]
    file_name = join(input_folder, input_file)

    lat_files = config[WorldLitter.lat_files]
    lon_files = config[WorldLitter.lon_files]
    release_loc_folder = config[WorldLitter.loc_folder]
    lats = functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
    lons = functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

    # This will plot the output netcdf from ocean parcels
    # plotTrajectoriesFile(file_name)
    # file_name = "/data/UN_Litter_data/output/JUN22_2010-01-01_2010-01-31__00_JUN22JUN22Test_Unbeaching.nc"
    # file_name = "/data/UN_Litter_data/output/JUN22_2010-01-31_2010-03-02__01_JUN22JUN22Test_Unbeaching.nc"
    file_name = "/data/UN_Litter_data/output/JUN22_2010-03-02_2010-04-01__02_JUN22JUN22Test_Unbeaching.nc"
    plotDataOZ(file_name)

    # This plots directly the json file
    # json_file = F"/var/www/html/data/6/{input_file.replace('.nc','_00.json')}"
    # json_file = F"/var/www/html/data/6/Single_Release_FiveYears_EachMonth_2010_01_04.json"
    # json_file = F"/var/www/html/data/6/JUN22JUN22Test_Unbeaching_00.json"
    # plotJsonFile(json_file)
