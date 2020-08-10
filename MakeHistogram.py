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
import functools
from multiprocessing import Pool

np.set_printoptions(precision=4)

def make_plot(LONS, LATS, data, title, file_name):
    # IMPORTANT IT MAY LOOK WRONG ON PYCHARM BUT CORRECT ON THE PNG
    n_colors = 30  # NUmber of color sin the color bar
    fig, ax= plt.subplots(1, 1, figsize=(20,20), subplot_kw={'projection': ccrs.PlateCarree()})
    # axs.stock_img()    # Only for transparency
    # cs = plt.contourf(LONS, LATS, data, n_colors, transform=ccrs.PlateCarree(),
    #                   cmap=cm.PuBu_r)
    # cax, kw = mpl.colorbar.make_axes(axs, location='top', shrink=1)
    # fig.colorbar(cs, cax=cax, extend='both', **kw)

    norm = mpl.colors.LogNorm(vmin=1, vmax=max(10, int(np.nanmax(data))))
    cs = ax.contourf(LONS, LATS, data, n_colors, transform=ccrs.PlateCarree(), cmap=cm.PuBu_r, norm=norm)
    fig.colorbar(cs, shrink=.3)
    # cax.set_title(title)
    plt.savefig(file_name, bbox_inches='tight')
    # plt.show()
    plt.close()


def make_hist(only_acc):
    config = get_op_config()

    input_folder = config[WorldLitter.output_folder]
    input_file = config[WorldLitter.output_file]
    file_name = join(input_folder, input_file)

    resolution = 1/10  # In degrees
    resolution_txt = "one_tenth"  # In degrees
    # resolution = 1/4  # In degrees
    # resolution_txt = "one_quarter"  # In degrees

    output_histogram_folder = join(input_folder, "histo")
    output_imgs_folder = join(input_folder, "images")
    output_tiff_folder = join(input_folder, "tiffs")

    if not(os.path.exists(output_histogram_folder)):
        os.makedirs(output_histogram_folder)
    if not(os.path.exists(output_imgs_folder)):
        os.makedirs(output_imgs_folder)
    if not(os.path.exists(output_tiff_folder)):
        os.makedirs(output_tiff_folder)

    output_file = join(output_histogram_folder, F"{input_file.replace('.nc','')}_histogram_{resolution_txt}")
    output_file_tiff = join(output_tiff_folder, F"{input_file.replace('.nc','')}_histogram_{resolution_txt}.tiff")

    ds = Dataset(file_name, "r", format="NETCDF4")

    tot_lats = int(180/resolution)
    tot_lons = int(360/resolution)

    lats = ds['lat'][:]
    lons = ds['lon'][:]
    tot_particles = len(lats)

    LATS = np.linspace(-90, 90, tot_lats+1)
    LONS = np.linspace(-180, 180, tot_lons+1)

    # Computing accumulated histogram
    tot_proc = 10
    with Pool(tot_proc) as pool:
        acum_histo_par = pool.starmap(parallelSum, [(lats, lons, LATS, LONS, i, tot_proc) for i in range(tot_proc)])

    acum_histo_par = np.array(acum_histo_par)
    acum_histo = np.sum(acum_histo_par, axis=0)
    # REVIEW THIS PART!!! THE 12 IS BECAUSE WE ASSUME 12  RELEASES PER YEAR
    tons_per_particle = ((6.4e6)/(tot_particles * 12))
    acum_histo = tons_per_particle*acum_histo + 1
    idx = acum_histo == 1
    acum_histo[idx] = np.nan
    # Avoid zeros
    idx = acum_histo == 0
    acum_histo[idx] = 1
    # Saving accumulated histogram as netcdf
    print("Saving files....")
    ds = xr.Dataset({"histo": (("lat", "lon"), acum_histo)}, {"lat": LATS, "lon": LONS})
    ds = addAttributes(ds, 'histo')
    ds.to_netcdf(F"{output_file}.nc")
    ds.close()

    make_plot(LONS, LATS, acum_histo, F"Acumulated  {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_Accumulated.png"))
    # os.system(F"gdal_translate -a_srs EPSG:4326 NETCDF:{output_file}.nc:histo {output_file_tiff}")
    os.system(F"gdal_translate  NETCDF:{output_file}.nc:histo {output_file_tiff}")


def parallelSum(lats, lons, LATS, LONS, id_proc, tot_proc):

    histo = np.zeros((len(LATS), len(LONS)))
    c_lats = lats.flatten()
    c_lons = lons.flatten()
    tot_particles = len(c_lats)

    # Patch to retrieve those below -180 and above 180 (assuming it wont make 2 turns)
    id_below = c_lons <= -180
    id_above = c_lons >= 180
    c_lons[id_below] = c_lons[id_below] + 360
    c_lons[id_above] = c_lons[id_above] - 360
    # Iterate over all particles
    segment_size = int(np.ceil(tot_particles/tot_proc))
    seg_from = int(segment_size*id_proc)
    seg_to = int(np.min((segment_size*(id_proc+1), tot_particles)))
    print(F"Id: {id_proc}, tot_proc: {tot_proc}, tot particles: {tot_particles} from: {seg_from} to: {seg_to}")
    for c_part in np.arange(seg_from, seg_to):
        i = np.argmax(c_lats[c_part] <= LATS) - 1
        j = np.argmax(c_lons[c_part] <= LONS) - 1
        histo[i, j] += 1

        # Plot some of the results
        if c_part% 100000 == 0:
            print(F"Proc: {id_proc} Time: {c_part} of {seg_to} ")

    return histo


def addAttributes(ds, var_name):
    ds.attrs['Conventions'] = "CF-1.0"
    ds['lat'].attrs['standard_name'] = "latitude"
    ds['lat'].attrs['long_name'] = "latitude"
    ds['lat'].attrs['units'] = "degrees_north"
    ds['lat'].attrs['axis'] = "Y"
    ds['lon'].attrs['standard_name'] = "longitude"
    ds['lon'].attrs['long_name'] = "longitude"
    ds['lon'].attrs['units'] = "degrees_east"
    ds['lon'].attrs['axis'] = "X"
    ds[var_name].attrs['standard_name'] = "sea_surface_temperature"
    ds[var_name].attrs['units'] = "K"
    return ds


if __name__ == "__main__":
    make_hist(only_acc=True)

