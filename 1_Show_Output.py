from parcels import plotTrajectoriesFile
from datetime import datetime
from os.path import join
from netCDF4 import Dataset



from config.MainConfig import get_op_config
from config.params import WorldLitter

config = get_op_config()

input_folder = config[WorldLitter.output_folder]
input_file = config[WorldLitter.output_file]
file_name = join(input_folder, input_file)

ds = Dataset(file_name, "r+", format="NETCDF4")
this_many = 10
print(F"Variables: {ds.variables.keys()}")
print(F"Trajectory: {ds.variables['trajectory'].shape}:{ds.variables['trajectory'][0:this_many]}")
print(F"time: {ds.variables['time'].shape}:{ds.variables['time'][0:this_many]}")
print(F"lat: {ds.variables['lat'].shape}:{ds.variables['lat'][0:this_many]}")
print(F"lon: {ds.variables['lon'].shape}:{ds.variables['lon'][0:this_many]}")
print(F"z: {ds.variables['z'].shape}:{ds.variables['z'][0:this_many]}")

print("Done!")
