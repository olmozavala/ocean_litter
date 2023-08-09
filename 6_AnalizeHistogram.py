from os.path import join
from netCDF4 import Dataset
import xarray as xr
import numpy as np
import functools
import matplotlib.pyplot as plt
from config.MainConfig import get_op_config
from config.params import WorldLitter
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import multiprocessing as mp
from matplotlib import cm
import matplotlib as mpl
import os

if __name__ == "__main__":
    file_name = "/home/data/UN_Litter_data/output/histo/Single_Release_FiveYears_EachMonth_2010_12_histogram_one_quarter.nc"

    ds = xr.open_dataset(file_name)
    histo = ds['histo']

    plt.imshow(histo[400:450,0:3])
    plt.show()

    x = 1

