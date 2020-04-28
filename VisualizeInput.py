from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

def plot2d(input_file, title='', field='surf_u'):
    ds = Dataset(input_file, "r+", format="NETCDF4")
    print(F"Variables: {ds.variables.keys()}")
    plt.subplots(1,3)
    plt.subplot(1,3,1)
    plt.imshow(np.flipud(ds[field][:,:]))
    plt.subplot(1,3,2)
    plt.imshow(np.flipud(ds[field][1300:1800,1500:1900]))
    plt.subplot(1,3,3)
    # ds[field][0,1500:1510,1560:1590] = np.nan
    plt.imshow(np.flipud(ds[field][1500:1600,1560:1650]))
    plt.title(title)
    plt.show()
    print(np.amax(ds[field][1500:1600,1560:1650]))
    print(np.amin(ds[field][1500:1600,1560:1650]))
    ds.close()

def plot(input_file, title='', field='surf_u'):
    ds = Dataset(input_file, "r+", format="NETCDF4")
    print(F"Variables: {ds.variables.keys()}")
    # print(F"Trajectory: {ds.variables['trajectory'].shape}:{ds.variables['trajectory'][0:this_many]}")
    # print(F"time: {ds.variables['time'].shape}:{ds.variables['time'][0:this_many]}")
    # print(F"lat: {ds.variables['lat'].shape}:{ds.variables['lat'][0:this_many]}")
    # print(F"lon: {ds.variables['lon'].shape}:{ds.variables['lon'][0:this_many]}")
    # print(F"z: {ds.variables['z'].shape}:{ds.variables['z'][0:this_many]}")
    plt.subplots(1,3)
    plt.subplot(1,3,1)
    plt.imshow(np.flipud(ds[field][0,:,:]))
    plt.subplot(1,3,2)
    plt.imshow(np.flipud(ds[field][0,1300:1800,1500:1900]))
    plt.subplot(1,3,3)
    # ds[field][0,1500:1510,1560:1590] = np.nan
    plt.imshow(np.flipud(ds[field][0,1500:1600,1560:1650]))
    plt.title(title)
    plt.show()
    print(ds[field][0,1500:1600,1560:1650])
    print(np.amax(ds[field][0,1500:1600,1560:1650]))
    print(np.amin(ds[field][0,1500:1600,1560:1650]))
    ds.close()


input_file = "/home/data/UN_Litter_data/HYCOM/2010c/hycom_JRA55_GLBv0.08_20100101_t000.nc"
plot(input_file, 'combined')
input_file = "/home/data/UN_Litter_data/HYCOM/2010/hycom_GLBv0.08_536_2010010112_t000.nc"
plot(input_file, 'old')
#
input_file = "/home/data/UN_Litter_data/HYCOM/unbeaching.nc"
plot2d(input_file, 'beaching', 'unBeachU')


