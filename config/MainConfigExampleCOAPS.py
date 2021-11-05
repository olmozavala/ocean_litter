from config.params import GlobalModel, Preproc
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
        GlobalModel.years: np.arange(2010, 2015),
        # WorldLitter.base_folder: "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/",
        GlobalModel.base_folder: join(data_folder, "HYCOM"),
        GlobalModel.loc_folder: "data/release_locations_reduced",
        GlobalModel.unbeach_file: join(data_folder, "HYCOM/unbeaching100000ms.nc"),
        # WorldLitter.output_folder: "/data/UN_Litter_data/Output/",
        GlobalModel.output_folder: join(data_folder, "output", "Difussion_and_Winds"),
        GlobalModel.output_file: F"{today_str}.nc",
        GlobalModel.stats_folder: "data/reached_data_tables",
        GlobalModel.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
        GlobalModel.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
        # lat_files = ["river_cat_1_x.csv"]
        # lon_files = ["river_cat_1_y.csv"]
        # WorldLitter.wind_factor: 0.035,
        # WorldLitter.repeat_release: timedelta(hours=0),  # 61
        GlobalModel.repeat_release: None,
        GlobalModel.output_freq: timedelta(hours=24),  # 24
        GlobalModel.dt: timedelta(hours=1), # 1 hour
        GlobalModel.output_folder_web: "/var/www/html/data",
        # WorldLitter.countries_file: "/home/data/UN_Litter_data/Particles_by_Country_large.csv",
        GlobalModel.countries_file: join(data_folder, "Particles_by_Country_small.csv")
    }
    return cur_config

