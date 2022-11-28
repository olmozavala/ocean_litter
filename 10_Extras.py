import xarray as xr
import matplotlib.pyplot as plt

## ======== Make geotiff for figure 2 =========
file_name = "/home/olmozavala/Dropbox/MyProjects/EOAS/COAPS/UN_Ocean_Litter/WorldLitter/data/Extras/mpw_ocean_2010_2019.nc"
ds = xr.load_dataset(file_name)

## =====
grid_res