from os.path import join
from netCDF4 import Dataset
import xarray as xr
import numpy as np
import functools
import matplotlib.pyplot as plt
from config.MainConfig import get_op_config
from config.params import GlobalModel
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


def make_hist(config, input_file):
    """
    It computes the histogram of a single file in parallel, using tot processors
    :return:
    """
    # Parameters. How many processors and what resolution to create the histogram
    tot_proc = 10
    resolution = 1/10  # In degrees
    resolution_txt = "one_tenth"  # In degrees

    # Reads input folders
    input_folder = config[GlobalModel.output_folder]
    file_name = join(input_folder, input_file)

    # Creates output folders and file names
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

    # Creates the output data frame and creates the output grid
    print(F"Working with file: {file_name}")
    ds = Dataset(file_name, "r", format="NETCDF4")

    tot_lats = int(180/resolution)
    tot_lons = int(360/resolution)

    # lats and lons contain ALL the positions from the files
    lats = ds['lat'][:]
    lons = ds['lon'][:]
    tot_particles = len(lats)

    LATS = np.linspace(-90, 90, tot_lats+1)
    LONS = np.linspace(-180, 180, tot_lons+1)

    # Computes the histogram in parallel
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
    idx = acum_histo <= 0
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
    """
    Depending on the assigned id proc it will sum its corresponding lats and lons into the grid
    :param lats:
    :param lons:
    :param LATS:
    :param LONS:
    :param id_proc:
    :param tot_proc:
    :return:
    """

    # makes the grid and flattens the arrays
    histo = np.zeros((len(LATS), len(LONS)))
    c_lats = lats.flatten()
    c_lons = lons.flatten()
    tot_particles = len(c_lats)

    # Patch to retrieve those below -180 and above 180 (assuming it wont make 2 turns)
    id_below = c_lons <= -180
    id_above = c_lons >= 180
    c_lons[id_below] = c_lons[id_below] + 360
    c_lons[id_above] = c_lons[id_above] - 360

    segment_size = int(np.ceil(tot_particles/tot_proc))
    seg_from = int(segment_size*id_proc)
    seg_to = int(np.min((segment_size*(id_proc+1), tot_particles)))
    print(F"Id: {id_proc}, tot_proc: {tot_proc}, tot particles: {tot_particles} from: {seg_from} to: {seg_to}")

    # Iterate over all particles. It searches the index in the GRID for each particle and adds it into the position
    for c_part in np.arange(seg_from, seg_to):
        i = np.argmax(c_lats[c_part] <= LATS) - 1
        j = np.argmax(c_lons[c_part] <= LONS) - 1
        histo[i, j] += 1

        # Plot some of the results
        if c_part% 100000 == 0:
            print(F"Proc: {id_proc} Time: {c_part} of {seg_to} ")

    return histo


def addAttributes(ds, var_name):
    """Adds default attributes the the netcdf to make it CF-Compliant"""
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
    # By default the outputs should be on your 'data/output' folder
    config = get_op_config()

    # =========================== Makes histogram =====================
    # This part is to generate (in a loop) CF-netcdf files of the accumulated locations.
    for i in range(5,13):
        # I modify it so that it takes the names from heere NOT from the config file
        file_name = F"YesWinds_YesDiffusion_NoUnbeaching_2010_{i:02d}.nc"
        # make_hist(config, file_name)

    # =========================== Merges histograms =====================
    # Here we can merge those files into a single one
    total_days = (365 * 12) - (11 * (6 * 30))# How many time steps were evaluated in TOTAL by all the model
    all_files = []

    resolution = 1/10  # In degrees
    tot_lats = int(180/resolution)
    tot_lons = int(360/resolution)

    first_file = True
    input_folder = "/data/UN_Litter_data/output/histo"
    for i in range(1,13):
        input_file = F"YesWinds_YesDiffusion_NoUnbeaching_2010_{i:02d}_histogram_one_tenth.nc"
        file_name = join(input_folder, input_file)
        ds = Dataset(file_name, "r", format="NETCDF4")

        if first_file:
            lat = ds['lat'][:]
            lon = ds['lon'][:]
            c_histo = ds['histo'][:]
            first_file = False
        else:
            c_histo += ds['histo'][:]

        ds.close()

    f_histo = c_histo/total_days
    print(F"Saving merged file.... min value: {np.amin(f_histo)} max value: {np.amax(f_histo)}")
    ds = xr.Dataset({"histo": (("lat", "lon"), f_histo)}, {"lat": lat, "lon": lon})
    ds = addAttributes(ds, 'histo')
    ds.to_netcdf(join(input_folder,F"Merged.nc"))
    ds.close()


