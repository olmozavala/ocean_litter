from matplotlib import cm
import os
from os.path import join, exists
from netCDF4 import Dataset
import numpy as np
import functools
from parcels.scripts.plottrajectoriesfile import plotTrajectoriesFile
import json
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import matplotlib as mpl
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from config.MainConfig import get_op_config
from config.params import WorldLitter
from multiprocessing import Pool
from utils.ParticlesByCountry import indexForCountries

# -------------- Plot with OP ---------------
def dateFromCF(str_date):
    sp = str_date.split(' ')
    # For the moment it assumes it is in days 'days since 2010-01-01 00:00:00'
    return datetime.strptime(sp[2][:10],'%Y-%m-%d')

def plotOceanParcelsAccumulatedResultsByParticleTime(input_data_folder, output_folder, start_year, end_year, dt=1, countries="all"):
    """
   It plots the ACCUMULATED particles from all the files.
   :param input_data_folder:
   :param start_year: when to start
   :param end_year: when to end
   :param dt: how often to plot
   :param countries: which countries do we want to plot.
   :return:
   """
    # Only for
    tot_days = (end_year-start_year)*365
    start_date = datetime.strptime(str(start_year),'%Y')

    first_file = True
    open_files = []
    for c_day_idx in np.arange(0, tot_days, dt):
        print(F"------- {c_day_idx}---------")
        # Released months
        c_date = start_date + timedelta(days=int(c_day_idx))  # What is the current date to plot
        months = (c_date.year - start_date.year)*12  + c_date.month - start_date.month   # How many monts should we plot
        # cmap = cm.get_cmap('Greens_r', months+1)
        cmap = cm.get_cmap('gist_earth', months+1)

        # Iterate over all the files that should contribute to the image
        fig = plt.figure(figsize=(20,10))
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        for c_month_idx in range(0, months + 1):
            c_file_year = (start_date + relativedelta(months=int(c_month_idx))).year
            c_file_month = (start_date + relativedelta(months=int(c_month_idx))).month
            skip_days = c_day_idx - (c_date - datetime.strptime(F"{c_file_year}-{c_file_month}",'%Y-%m')).days

            if len(open_files) <= c_month_idx:
                file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{c_file_year}_{(c_file_month):02d}.nc"
                print(F"Reading new file: {file_name}")
                open_files.append(Dataset(join(input_data_folder, file_name), "r", format="NETCDF4"))
                if first_file:  # If is the first file we are going to open then we verify we don't need to mix with the countries
                    if countries != "all":  # In this case we plot all the locations
                        idx_locations_df = indexForCountries(countries)
                        idx_locations = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                                                         [np.genfromtxt([country_locations.replace("]","").replace("[","")], delimiter=",", dtype="int")
                                                          for country_locations in idx_locations_df.loc[:,"idx_country"]])


                    first_file = False  # If is the first file we are going to open then we veri

            c_time_step = c_day_idx - skip_days
            # lats = open_files[c_month_idx].variables['lat'][:,c_time_step]
            # lons = open_files[c_month_idx].variables['lon'][:,c_time_step]
            if countries == "all":  # In this case we plot all the locations
                ax.scatter(open_files[c_month_idx].variables['lon'][:,c_time_step], open_files[c_month_idx].variables['lat'][:,c_time_step], color='c', s=1)
            else:
                # c_color = ((c_month_idx)/(months+1),0,0)
                c_color =  cmap(np.min([1.0, .9 - c_month_idx/(months+1)]))  # Los primeros meses son mas oscuros
                # alpha = np.min([1.0, .2 + (c_month_idx + 1)/(months+1)])   # Los primeros meses son mas claros/transparentes
                alpha = 1
                ax.scatter(open_files[c_month_idx].variables['lon'][idx_locations,c_time_step],
                           open_files[c_month_idx].variables['lat'][idx_locations,c_time_step],
                           color=c_color, s=1, alpha=alpha)

        title = F"{start_date.strftime('%Y-%m-%d')} - {c_date.strftime('%Y-%m-%d')}"
        ax.coastlines()
        ax.set_title(title, fontsize=30)

        # plt.show()
        plt.savefig(F"{output_folder}/{start_date.strftime('%Y_%m')}_{c_day_idx:04d}.png")
        plt.close()

def plotOceanParcelsAccumulatedResults(input_data_folder, output_folder, start_year, end_year, dt=1, countries="all"):
    """
    It plots the ACCUMULATED particles from all the files.
    :param input_data_folder:
    :param start_year: when to start
    :param end_year: when to end
    :param dt: how often to plot
    :param countries: which countries do we want to plot.
    :return:
    """
    # Only for
    tot_days = (end_year-start_year)*365
    start_date = datetime.strptime(str(start_year),'%Y')

    first_file = True
    open_files = []
    for c_day_idx in np.arange(0, tot_days, dt):
        print(F"------- {c_day_idx}---------")
        # Released months
        c_date = start_date + timedelta(days=int(c_day_idx))  # What is the current date to plot
        months = (c_date.year - start_date.year)*12  + c_date.month - start_date.month   # Which month we want to plot

        # Iterate over all the files that should contribute to the image
        fig = plt.figure(figsize=(20,10))
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        for c_month_idx in range(0, months + 1):
            c_file_year = (start_date + relativedelta(months=int(c_month_idx))).year
            c_file_month = (start_date + relativedelta(months=int(c_month_idx))).month
            skip_days = c_day_idx - (c_date - datetime.strptime(F"{c_file_year}-{c_file_month}",'%Y-%m')).days

            if len(open_files) <= c_month_idx:
                file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{c_file_year}_{(c_file_month):02d}.nc"
                print(F"Reading new file: {file_name}")
                open_files.append(Dataset(join(input_data_folder, file_name), "r", format="NETCDF4"))
                if first_file:  # If is the first file we are going to open then we verify we don't need to mix with the countries
                    if countries != "all":  # In this case we plot all the locations
                        idx_locations_df = indexForCountries(countries)
                        idx_locations = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                                                [np.genfromtxt([country_locations.replace("]","").replace("[","")], delimiter=",", dtype="int")
                                                 for country_locations in idx_locations_df.loc[:,"idx_country"]])


                    first_file = False  # If is the first file we are going to open then we veri

            c_time_step = c_day_idx - skip_days
            # lats = open_files[c_month_idx].variables['lat'][:,c_time_step]
            # lons = open_files[c_month_idx].variables['lon'][:,c_time_step]
            if countries == "all":  # In this case we plot all the locations
                ax.scatter(open_files[c_month_idx].variables['lon'][:,c_time_step], open_files[c_month_idx].variables['lat'][:,c_time_step], color='c', s=1)
            else:
                ax.scatter(open_files[c_month_idx].variables['lon'][idx_locations,c_time_step], open_files[c_month_idx].variables['lat'][idx_locations,c_time_step], color='c', s=1)

        title = F"{start_date.strftime('%Y-%m-%d')} - {c_date.strftime('%Y-%m-%d')}"
        ax.coastlines()
        ax.set_title(title, fontsize=30)

        # plt.show()
        plt.savefig(F"{output_folder}/{start_date.strftime('%Y_%m')}_{c_day_idx:04d}.png")
        plt.close()

def plotOceanParcelsParallelNotAccumulated(TOT_PROC, procid, input_data_folder, output_folder, file_name, usebeached=True, dt=1, ):
    """
    Plots not accumulated data with or without beaching
    :param TOT_PROC:
    :param procid:
    :param input_data_folder:
    :param output_folder:
    :param file_name:
    :param usebeached:
    :param dt:
    :return:
    """
    # -------------- Info about variables ---------------
    if not(exists(output_folder)):
        os.makedirs(output_folder)

    ds = Dataset(join(input_data_folder, file_name), "r", format="NETCDF4")
    # this_many = 10
    # print(F"Variables: {ds.variables.keys()}")
    # print(F"Trajectory: {ds.variables['trajectory'].shape}:{ds.variables['trajectory'][0:this_many]}")
    # print(F"time: {ds.variables['time'].shape}:{ds.variables['time'][0:this_many]}")
    # print(F"lat: {ds.variables['lat'].shape}:{ds.variables['lat'][0:this_many]}")
    # print(F"lon: {ds.variables['lon'].shape}:{ds.variables['lon'][0:this_many]}") # print(F"z: {ds.variables['z'].shape}:{ds.variables['z'][0:this_many]}") # print(F"beached: {ds.variables['beached'].shape}:{ds.variables['beached'][0:this_many]}") # print(F"beached_count: {ds.variables['beached_count'].shape}:{ds.variables['beached_count'][0:this_many]}")

    tot_times = ds.variables['trajectory'].shape[1]
    start_date = dateFromCF(ds.variables['time'].units)
    for c_time_step in np.arange(0,tot_times,dt):
        # print(F"proc_id: {procid} (c_time_step % TOT_PROC)=({c_time_step} % {TOT_PROC}) = {(c_time_step % TOT_PROC)}")
        if (c_time_step % TOT_PROC) == procid:
            print(F"------------------ procid: {procid} --> timestep {c_time_step} ----------------------")
            fig = plt.figure(figsize=(20,10))
            c_date = start_date + timedelta(days=int(c_time_step))

            lats = ds.variables['lat'][:,c_time_step]
            lons = ds.variables['lon'][:,c_time_step]
            trajectory = ds.variables['trajectory'][:,c_time_step]

            # title = F'{file_name} \n Current time step: {c_time_step}'
            title = F"{start_date.strftime('%Y-%m-%d')} - {c_date.strftime('%Y-%m-%d')}"
            if usebeached:
                beached = ds.variables['beached'][:,c_time_step]
                beached_count = ds.variables['beached_count'][:,c_time_step]
                id0 = beached == 0
                id1 = beached == 1
                id2 = beached == 2

                if c_time_step == 0:
                    id3 = beached == 3
                    id4 = beached == 4
                else:
                    id3 = np.logical_or(id3, beached == 3)
                    id4 = np.logical_or(id4, beached == 4)
                    id4 = np.logical_or(id4, beached.mask)

                print(beached[id4])
                print(beached_count[id4])
                print(trajectory[id4])

                # plotScatter(lats[id0], lons[id0], 'b', title)
                # plotScatter(lats[id1], lons[id1], 'r', title)
                # plotScatter(lats[id2], lons[id2], 'g', title) # plotScatter(lats[id3], lons[id3], 'm', title)
                plotScatter(lats[id4], lons[id4], 'y', title)
            else:
                plotScatter(lats, lons, 'y', title)

            # plt.show()
            plt.savefig(F"{output_folder}/{c_time_step:04d}.png")
            plt.close()

def plotOceanParcelsParallelSameDayDifferentReleases(TOT_PROC, procid, input_data_folder, output_folder, years, months, date_to_plot):
    """
    Plots a single day for multiple releases (with diferent colors
    :param TOT_PROC:
    :param procid:
    :param input_data_folder:
    :param output_folder:
    :param years: Which year of releases we want to include
    :param months: Which month of releases we want to include
    :param date_to_plot: Which date we want to plot
    :param file_name:
    :return:
    """
    # -------------- Info about variables ---------------
    if not(exists(output_folder)):
        os.makedirs(output_folder)

    for c_year in years:
        for c_month in months:
            # print(F"{c_year}_{c_month}")
            file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{c_year}_{c_month:02d}.nc"
            ds = Dataset(join(input_data_folder, file_name), "r", format="NETCDF4")
            print(ds.variables['time'].units)
            start_date = dateFromCF(ds.variables['time'].units)
            # Computes the difference between the start_date and the received date
            c_time_step = (date_to_plot - start_date).days
            if c_time_step >= 0:
                fig = plt.figure(figsize=(20,10))

                lats = ds.variables['lat'][:,c_time_step]
                lons = ds.variables['lon'][:,c_time_step]

                # title = F'{file_name} \n Current time step: {c_time_step}'
                title = F"Release: {c_year}_{c_month} date: {date_to_plot.strftime('%Y-%m-%d')}"

                plotScatter(lats, lons, 'y', title)

                # plt.show()
                plt.savefig(F"{output_folder}/{c_year}_{c_month:02}_{date_to_plot.strftime('%Y-%m-%d')}.png")
                plt.close()

def plotScatter(lats, lons, color='b',title=''):
    """
    Default function to plot lat and lons as scatter plot
    :param lats:
    :param lons:
    :param color:
    :param title:
    :return:
    """
    ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.scatter(lons, lats, color=color, s=1)
    ax.coastlines()
    ax.set_global()
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

    input_data_folder = "/data/COAPS_Net/work/ozavala/WorldLitterOutput/2010-2020_Eleven_Years"
    output_folder = "/home/olmozavala/Desktop/DELETE"

    # ------------------- For OceanParcels built in plots---------------
    # This will plot the output netcdf using ocean parcels function
    # file_name = join(input_data_folder, "TenYears_YesWinds_YesDiffusion_NoUnbeaching_2010_01.nc")
    # plotTrajectoriesFile(file_name)

    # ------------------- Accumulated plots ---------------
    # Here I'm plotting all the accumulated files for 10 years (it will never end)
    # countries = ["Cambodia","China","Indonesia", "South Korea", "Malaysia", "Philippines", "Thailand", "Vietnam"]
    # plotOceanParcelsAccumulatedResults(input_data_folder, output_folder, 2010, 2020, dt=1, countries=countries)

    # ------------------- Accumulated plots (dt is the dt of the particles and they are plotted with different colors)---------------
    # Here I'm plotting all the accumulated files for 10 years colored by particle time
    # countries = ["Cambodia","China","Indonesia", "South Korea", "Malaysia", "Philippines", "Thailand", "Vietnam"]
    # plotOceanParcelsAccumulatedResultsByParticleTime(input_data_folder, output_folder, 2010, 2020, dt=31, countries=countries)

    # ------------------- Parallel plots (not accumulated) ---------------
    # Here I'm plotting separated files
    TOT_PROC = 10
    p = Pool(TOT_PROC)
    dt = 1 # How often to plot
    # for year in range(2010, 2011):
    for year in range(2010, 2011):
        try:
            # for month in range(1, 13):
            for month in range(1, 2):
                print(F"===================== MONTH {month} ====================")
                file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{year}_{month:02d}.nc"
                output_folder = join(output_folder, F"{year}_{month:02d}")
                print(file_name)
                p.starmap(plotOceanParcelsParallelNotAccumulated, [[TOT_PROC, procid, input_data_folder, output_folder, file_name, False, dt] for procid in range(TOT_PROC)])
        except Exception as e:
            print(F"Failed for {year}: {e}")

    # ------------------- Plots single day multiple releases
    # Here I'm plotting separated files
#     TOT_PROC = 10
#     p = Pool(TOT_PROC)
#     years = range(2010,2020)
#     months = range(1,12)
#     date_to_plot = datetime.strptime("2011-05-01","%Y-%m-%d")
#     try:
#         plotOceanParcelsParallelSameDayDifferentReleases(1, 0, input_data_folder, output_folder, years, months, date_to_plot)
#         # p.starmap(plotOceanParcelsParallelSameDayDifferentReleases, [[TOT_PROC, procid, input_data_folder, output_folder, years, months, date_to_plot] for procid in range(TOT_PROC)])
# # def plotOceanParcelsParallelSameDayDifferentReleases(TOT_PROC, procid, input_data_folder, output_folder, years, months, date_to_plot):
#     except Exception as e:
#         print(F"Failed: {e}")

    # ---------- Plots JSON files ----------------
    # This plots directly the json file
    # json_file = F"/var/www/html/data/6/{input_file.replace('.nc','_00.json')}"
    # json_file = F"/var/www/html/data/6/Single_Release_FiveYears_EachMonth_2010_01_04.json"
    # json_file = F"/var/www/html/data/6/JUN22JUN22Test_Unbeaching_00.json"
    # plotJsonFile(json_file)

