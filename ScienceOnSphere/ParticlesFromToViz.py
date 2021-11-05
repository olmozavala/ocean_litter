from datetime import datetime
import os
from os.path import join, exists
from netCDF4 import Dataset
import numpy as np
import functools
# from parcels.scripts.plottrajectoriesfile import plotTrajectoriesFile
import json
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import matplotlib as mpl
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from config.MainConfig import get_op_config
from config.params import GlobalModel
from multiprocessing import Pool
import geopandas
import matplotlib.pyplot as plt
import geoplot.crs as gcrs
import geoplot as gplt
import time
import mapclassify

def dateFromCF(str_date):
    sp = str_date.split(' ')
    # For the moment it assumes it is in days 'days since 2010-01-01 00:00:00'
    return datetime.strptime(sp[2],'%Y-%m-%d')

def plotOceanParcelsAccumulatedResults(input_data_folder, output_folder, start_year, end_year, dt=1):
    """
    It plots the ACCUMULATED or NOT particles from all the files
    :param input_data_folder:
    :param start_year:
    :param end_year:
    :param dt:
    :return:
    """
    # Only for
    tot_days = (end_year-start_year)*365
    start_date = datetime.strptime(str(start_year),'%Y')

    open_files = []
    for c_day in np.arange(0, tot_days, dt):
        print(F"------- {c_day}---------")
        # Released months
        c_date = start_date + timedelta(days=int(c_day))
        months = (c_date.year - start_date.year)*12  + c_date.month - start_date.month

        # Iterate over all the files that should contribute to the image
        fig = plt.figure(figsize=(20,10))
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        for c_month in range(0, months + 1):
            c_file_year = (start_date + relativedelta(months=int(c_month))).year
            c_file_month = (start_date + relativedelta(months=int(c_month))).month
            skip_days = c_day - (c_date - datetime.strptime(F"{c_file_year}-{c_file_month}",'%Y-%m')).days

            if len(open_files) <= c_month:
                file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{c_file_year}_{(c_file_month):02d}.nc"
                print(F"Reading new file: {file_name}")
                open_files.append(Dataset(join(input_data_folder, file_name), "r", format="NETCDF4"))

            c_time_step = c_day - skip_days
            # lats = open_files[c_month].variables['lat'][:,c_time_step]
            # lons = open_files[c_month].variables['lon'][:,c_time_step]
            ax.scatter(open_files[c_month].variables['lon'][:,c_time_step], open_files[c_month].variables['lat'][:,c_time_step], color='c', s=1)

        title = F"{start_date.strftime('%Y-%m-%d')} - {c_date.strftime('%Y-%m-%d')}"
        ax.coastlines()
        ax.set_title(title, fontsize=30)

        # plt.show()
        plt.savefig(F"{output_folder}/{start_date.strftime('%Y_%m')}_{c_day:04d}.png")
        plt.close()


def plotOceanParcelOutputParallel(TOT_PROC, procid, input_data_folder, output_folder, file_name, usebeached=True, dt=1, ):
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

def plotScatter(lats, lons, color='b',title=''):
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

def getCountriesStats(maincountry, search_type="from"):
    countries = []
    tons = []
    percs = []
    try:
        if search_type == "from":
            for country in maincountry['from']['from']:
                countries.append(country['name'])
                tons.append(country['tons'])
                percs.append(country['perc'])
    except Exception as e:
        print(F"Failed for country: {stat}")
    return [c.lower() for c in countries], tons, percs

if __name__ == "__main__":
    config = get_op_config()

    # Read geojson
    web_folder = config[GlobalModel.output_folder_web]
    geojson_file = join(web_folder, "countries.json")
    stats_file = join(web_folder, "ReachedTablesData.json")
    geo_data = geopandas.read_file(geojson_file)

    ##
    with open(stats_file) as f:
        stats = json.load(f)
        # Iterate over each country
        for country, stat in stats.items():
            geo_country = geo_data[geo_data["name"].str.lower() == country] # Finds the corresponding geo data
            # Obtain all the countries that receive litter from it
            countries, tons, percs = getCountriesStats(stat)
            geo_from_countries = geo_data[geo_data["name"].str.lower().isin(countries)] # Finds the corresponding geo data
            # gplt.polyplot(geo_country, figsize=(8, 4))
            # gplt.polyplot(geo_from_countries, figsize=(8, 4))
            # Note: this code sample requires gplt>=0.4.0.
            if len(tons) > 0 and len(geo_from_countries) == len(tons):
                scheme = mapclassify.Quantiles(tons, k=min(5,len(tons)))
                ax = gplt.polyplot(geo_data, figsize=(8, 4))
                # ax = gplt.webmap(geo_data, projection=gcrs.WebMercator())
                ax2 = gplt.choropleth(geo_from_countries, hue=tons, scheme=scheme, cmap='Greens', ax=ax)
                # gplt.choropleth(geo_country, hue=[1],  cmap='gray', ax=ax2)
                plt.title(country.capitalize())
                plt.show()
            else:
                print(F"------------- failed ------------")
                print(list(geo_from_countries["name"]))
                print(countries)

    exit()
    ##


    input_folder = config[GlobalModel.output_folder]
    input_file = config[GlobalModel.output_file]
    file_name = join(input_folder, input_file)

    lat_files = config[GlobalModel.lat_files]
    lon_files = config[GlobalModel.lon_files]
    release_loc_folder = config[GlobalModel.loc_folder]
    lats = functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
    lons = functools.reduce(lambda a, b: np.concatenate((a, b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

    # ------------------- Parallel plots (not accumulated) ---------------
    # Here I'm plotting separated files
    input_data_folder = "/data/UN_Litter_data/output/YesWinds_YesDiffusion_NoUnbeaching"
    # output_folder = "/data/UN_Litter_data/output/OutputImages"
    output_folder = "/home/olmozavala/Desktop/DELETE"
    TOT_PROC = 10
    p = Pool(TOT_PROC)
    # for year in range(2010, 2011):
    for year in range(2010, 2011):
        try:
            # for month in range(1, 13):
            for month in range(1, 2):
                print(F"===================== MONTH {month} ====================")
                file_name = F"TenYears_YesWinds_YesDiffusion_NoUnbeaching_{year}_{month:02d}.nc"
                output_folder = join(output_folder, F"{year}_{month:02d}")
                print(file_name)
                p.starmap(plotOceanParcelOutputParallel, [[TOT_PROC, procid, input_data_folder, output_folder, file_name, False, 1] for procid in range(TOT_PROC)])
        except Exception as e:
            print(F"Failed for {year}: {e}")

    # ---------- Plots JSON files ----------------
    # This plots directly the json file
    # json_file = F"/var/www/html/data/6/{input_file.replace('.nc','_00.json')}"
    # json_file = F"/var/www/html/data/6/Single_Release_FiveYears_EachMonth_2010_01_04.json"
    # json_file = F"/var/www/html/data/6/JUN22JUN22Test_Unbeaching_00.json"
    # plotJsonFile(json_file)

