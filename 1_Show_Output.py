from datetime import datetime
from os.path import join
from netCDF4 import Dataset
import gmplot
import numpy as np
import functools

from config.MainConfig import get_op_config
from config.params import WorldLitter

config = get_op_config()

input_folder = config[WorldLitter.output_folder]
input_file = config[WorldLitter.output_file]
file_name = join(input_folder, input_file)

lat_files = config[WorldLitter.lat_files]
lon_files = config[WorldLitter.lon_files]
release_loc_folder = config[WorldLitter.loc_folder]
lats = functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
lons =  functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

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
# print("Done!")


gmap3 = gmplot.GoogleMapPlotter(0, 0, 3)
gmap3.scatter(lats, lons, '# FF0000', size=80, marker=False)

gmap3.draw("sopas.html")
