from config.params import WorldLitter, Preproc
import numpy as np
from datetime import timedelta, datetime, date
from os.path import join

today_str = "Single_Release_FiveYears_EachMonth_2010_MONTH"
#main_name = "NoWinds_NoDiffusion_NoUnbeaching"
# main_name = "NoWinds_YesDiffusion_NoUnbeaching"
# main_name = "YesWinds_NoDiffusion_NoUnbeaching"
# main_name = "YesWinds_YesDiffusion_NoUnbeaching"

def get_preproc_config():
    cur_config = {
        Preproc.shapes_folder: '/home/olmozavala/Dropbox/TestData/GIS/Shapefiles/World/high_res/',
    }

    return {**get_op_config(), **cur_config}

data_folder = "/data/UN_Litter_data"

def get_op_config():
    cur_config = {
        WorldLitter.years: np.arange(2010, 2015),
        # WorldLitter.base_folder: "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/",
        WorldLitter.base_folder: join(data_folder, "HYCOM"),
        WorldLitter.loc_folder: "data/release_locations_reduced",
        WorldLitter.unbeach_file: join(data_folder, "HYCOM/unbeaching100000ms.nc"),
        # WorldLitter.output_folder: "/data/UN_Litter_data/Output/",
        WorldLitter.output_folder: join(data_folder, "output", "Difussion_and_Winds"),
        WorldLitter.output_file: F"{today_str}.nc",
        WorldLitter.stats_folder: "data/reached_data_tables",
        WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
        WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
        # lat_files = ["river_cat_1_x.csv"]
        # lon_files = ["river_cat_1_y.csv"]
        # WorldLitter.wind_factor: 0.035,
        # WorldLitter.repeat_release: timedelta(hours=0),  # 61
        WorldLitter.repeat_release: None,
        WorldLitter.output_freq: timedelta(hours=24),  # 24
        WorldLitter.dt: timedelta(hours=1), # 1 hour
        WorldLitter.output_folder_web: "/var/www/html/data",
        # WorldLitter.countries_file: "/home/data/UN_Litter_data/Particles_by_Country_large.csv",
        WorldLitter.countries_file: join(data_folder, "Particles_by_Country_small.csv")
    }
    return cur_config

