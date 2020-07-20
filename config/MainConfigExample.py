from config.params import WorldLitter, Preproc
import numpy as np
from datetime import timedelta, datetime, date
from os.path import join

# today_str = "Final_Five_Years_WindsCurrentsDiffusionUnbeaching_MONTH"
# today_str = "TESTUN_output"
# today_str = "OneYear_Currents_And_Diffusion2020-05-05_16_36_output.nc"
# today_str = "OneYear_Currents_And_Wind2020-05-05_16_36_output.nc"
# today_str = "OneYear_Currents_Winds_Diffusion2020-05-05_16_36_output.nc"
# today_str = "OneYear_Only_Currents2020-05-05_16_36_output.nc"

today_str = "YesWinds_YesDiffusion_NoUnbeaching_2010_MONTH"

def get_preproc_config():
    cur_config = {
        Preproc.shapes_folder: '/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/high_res/',
    }

    return {**get_op_config(), **cur_config}

data_folder = "/data/UN_Litter_data"
# data_folder = "/home/data/UN_Litter_data"

def get_op_config():
    cur_config = {
        WorldLitter.years: np.arange(2010, 2015),
        # WorldLitter.base_folder: "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/",
        WorldLitter.base_folder: join(data_folder,"HYCOM"),
        WorldLitter.loc_folder: "data/release_locations_reduced",
        WorldLitter.unbeach_file: join(data_folder,"HYCOM/unbeaching100000ms.nc"),
        # WorldLitter.output_folder: join(data_folder,"output"),
        WorldLitter.output_folder: join(data_folder,"output","YesWinds_YesDiffusion_NoUnbeaching"),
        WorldLitter.output_file: F"{today_str}.nc",
        WorldLitter.stats_folder: "data/reached_data_tables",
        WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
        WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
        # lat_files = ["river_cat_1_x.csv"]
        # lon_files = ["river_cat_1_y.csv"]
        # WorldLitter.wind_factor: 0.035,
        # WorldLitter.repeat_release: timedelta(hours=0),  # 61
        WorldLitter.repeat_release: False,
        WorldLitter.output_freq: timedelta(hours=24),  # 24
        WorldLitter.dt: timedelta(hours=1), # 1 hour

        WorldLitter.output_folder_web: "/var/www/html/data",
        # WorldLitter.countries_file: "/home/data/UN_Litter_data/Particles_by_Country_large.csv",
        WorldLitter.countries_file: join(data_folder,"Particles_by_Country_small.csv")
    }
    return cur_config

# # # ------- HPC ---------
# def get_op_config():
#     cur_config = {
#         WorldLitter.years: np.arange(2010, 2011),
#         WorldLitter.base_folder: "/gpfs/home/osz09/scratch",
#         #WorldLitter.loc_folder: "/gpfs/home/osz09/ocean_litter/data/release_locations",
#         WorldLitter.loc_folder: "/gpfs/home/osz09/ocean_litter/data/release_locations/",
#         WorldLitter.output_folder: "/gpfs/home/osz09/scratch/output",
#         WorldLitter.output_file: F"{today_str}_output.nc",
#         WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
#         WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
#         WorldLitter.wind_factor: 0.035,
#         WorldLitter.run_time: timedelta(days=365),   # 365
#         WorldLitter.repeat_release: timedelta(days=61),  # 61
#         WorldLitter.output_freq: timedelta(hours=1),  # 24
#         WorldLitter.dt: timedelta(hours=1),  # 1
#
#         WorldLitter.output_folder_web: "/gpfs/home/osz09/scratch/output_web_folder",
#         #WorldLitter.countries_file: "/home/data/UN_Litter_data/Particles_by_Country.csv"
#     }
#     return cur_config

#
# # ------- LOCAL MACHINE ---------
# def get_config():
#     cur_config = {
#         WorldLitter.years: np.arange(2010, 2016),
#         WorldLitter.base_folder: "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/",
#         WorldLitter.loc_folder: "data/release_locations",
#         WorldLitter.output_file: F"/data/UN_Litter_data/Output/{today_str}_output.nc",
#         WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
#         WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
#         WorldLitter.wind_factor: 0.035
#     }
#     return cur_config
#
# # -------------- COAPS MACHINE ----------------
# def get_config():
#         cur_config = {
#             WorldLitter.years: np.arange(2010, 2016),
#             WorldLitter.base_folder: "/nexsan/people/xbxu/hycom/GLBv0.08/",
#             WorldLitter.loc_folder: "data/release_locations",
#             WorldLitter.output_file: F"/Net/work/ozavala/WorldLitterOutput/{today_str}_output.nc",
#             WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
#             WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
#             WorldLitter.wind_factor: 0.035
#         }
#         return cur_config
