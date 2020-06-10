from datetime import datetime
from os.path import join
from netCDF4 import Dataset
# import gmplot
import numpy as np
import functools
from parcels.scripts.plottrajectoriesfile import plotTrajectoriesFile
import json
import matplotlib.pyplot as plt
import multiprocessing as mp
from matplotlib import cm
import cartopy.crs as ccrs
import matplotlib as mpl

from config.MainConfig import get_op_config
from config.params import WorldLitter
# -------------- Plot with OP ---------------

# -------------- Info about variables ---------------
# ds = Dataset(file_name, "r+", format="NETCDF4")
# this_many = 10
# print(F"Variables: {ds.variables.keys()}")
# print(F"Trajectory: {ds.variables['trajectory'].shape}:{ds.variables['trajectory'][0:this_many]}")
# print(F"time: {ds.variables['time'].shape}:{ds.variables['time'][0:this_many]}")
# print(F"lat: {ds.variables['lat'].shape}:{ds.variables['lat'][0:this_many]}")
# print(F"lon: {ds.variables['lon'].shape}:{ds.variables['lon'][0:this_many]}")
# print(F"z: {ds.variables['z'].shape}:{ds.variables['z'][0:this_many]}")
# print(F"beached: {ds.variables['beached'].shape}:{ds.variables['beached'][0:this_many]}")
#

# -------------- Location in a map ---------------
# gmap3 = gmplot.GoogleMapPlotter(0, 0, 3)
# gmap3.scatter(lats, lons, '# FF0000', size=80, marker=False)
#
# gmap3.draw("sopas.html")

def plotOceanParcelsOutput(file_name):
    plotTrajectoriesFile(file_name, mode='2d')
    print("Done!")

def plotJsonFile(file_name):
    with open(file_name) as f:
        data = json.load(f)
        tot_times = len(data['Yemen']['lat_lon'][0][0])
        for c_time_step in range(tot_times):
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

    # This plots directly the json file
    json_file = F"/var/www/html/data/4/{input_file.replace('.nc','_00.json')}"
    plotJsonFile(json_file)
