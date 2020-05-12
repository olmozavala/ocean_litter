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

    resolution = 1/4  # In degrees
    resolution_txt = "one_quarter"  # In degrees

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
    output_file_beached = join(output_histogram_folder,  F"{input_file.replace('.nc','')}_beached_histogram_{resolution_txt}")
    output_file_beached_tiff = join(output_tiff_folder,  F"{input_file.replace('.nc','')}_beached_histogram_{resolution_txt}.tiff")

    ds = Dataset(file_name, "r", format="NETCDF4")

    lats = ds['lat'][:]
    lons = ds['lon'][:]
    beached = ds['beached'][:]
    time_steps = lats.shape[1]


    tot_lats = int(180/resolution)
    tot_lons = int(360/resolution)
    tot_particles = lats.shape[0]
    LATS = np.linspace(-90, 90, tot_lats)
    LONS = np.linspace(-180, 180, tot_lons)
    if (only_acc):
        histo = np.ones((tot_lats, tot_lons))
        beached_histo = np.ones((tot_lats, tot_lons))
    else:
        histo = np.ones((time_steps, tot_lats, tot_lons))
        beached_histo = np.ones((time_steps, tot_lats, tot_lons))

    # Iterate over all the times
    for c_time in range(2):
    # for c_time in range(time_steps):
        c_lats = lats[:,c_time]
        c_lons = lons[:,c_time]
        c_beached = beached[:,c_time]

        # Iterate over all particles
        for c_part in range(tot_particles):
            i = np.argmax(c_lats[c_part] <= LATS)
            j = np.argmax(c_lons[c_part] <= LONS)
            if only_acc:
                histo[i, j] += 1
                beached_histo[i, j] += c_beached[c_part]
            else:
                histo[c_time, i, j] += 1
                beached_histo[c_time, i, j] += c_beached[c_part]

        # Plot some of the results
        if c_time % 50 == 0:
            print(F" Time: {c_time} ")
            if only_acc:
                make_plot(LONS, LATS, beached_histo, F"Beached Day {c_time} {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_beached_{c_time}.png"))
                make_plot(LONS, LATS, histo, F"Day {c_time} {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_{c_time}.png"))
            else:
                make_plot(LONS, LATS, beached_histo[c_time], F"Beached Day {c_time} {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_beached_{c_time}.png"))
                make_plot(LONS, LATS, histo[c_time], F"Day {c_time} {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_{c_time}.png"))


    # Computing accumulated histogram
    if only_acc:
        acum_histo = histo
        acum_beached = beached_histo
    else:
        acum_histo = np.sum(histo, axis=0)
        acum_beached = np.sum(beached_histo, axis=0)

    idx = acum_histo == 1
    acum_histo[idx] = np.nan
    # Avoid zeros
    idx = acum_histo == 0
    acum_histo[idx] = 1
    # Saving accumulated histogram as netcdf
    print("Saving files....")
    ds = xr.Dataset( { "histo": (("lat","lon"), acum_histo),
                       }, {"lat": LATS, "lon": LONS} )
    ds.attrs['Conventions'] = "CF-1.0"
    ds['lat'].attrs['standard_name'] = "latitude"
    ds['lat'].attrs['long_name'] = "latitude"
    ds['lat'].attrs['units'] = "degrees_north"
    ds['lat'].attrs['axis'] = "Y"
    ds['lon'].attrs['standard_name'] = "longitude"
    ds['lon'].attrs['long_name'] = "longitude"
    ds['lon'].attrs['units'] = "degrees_east"
    ds['lon'].attrs['axis'] = "X"
    ds['histo'].attrs['standard_name'] = "sea_surface_temperature"
    ds['histo'].attrs['units'] = "K"
    ds.to_netcdf(F"{output_file}.nc")
    ds.close()
    ds = xr.Dataset( { "beached": (("lat","lon"), acum_beached) } )
    ds.to_netcdf(F"{output_file_beached}.nc")
    ds.close()

    make_plot(LONS, LATS, acum_histo, F"Acumulated  {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_Accumulated.png"))
    make_plot(LONS, LATS, acum_beached, F"Acumulated beached  {input_file}", join(output_imgs_folder, F"{input_file.replace('.nc','')}_AccumulatedBeached.png"))

    os.system(F"gdal_translate -a_srs EPSG:4326 NETCDF:{output_file}.nc:histo {output_file_tiff}")
    os.system(F"gdal_translate -a_srs EPSG:4326 NETCDF:{output_file_beached}.nc:beached {output_file_beached_tiff}")

    if not(only_acc):
        np.save(output_file, histo)
        np.save(output_file_beached, beached_histo)
    # Save the plot by calling plt.savefig() BEFORE plt.show()
    print("Done!!!")

if __name__ == "__main__":
    make_hist(only_acc=True)

