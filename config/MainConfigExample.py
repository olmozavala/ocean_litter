from config.params import WorldLitter
import numpy as np
from datetime import timedelta, datetime

# today_str = datetime.today().strftime("%Y-%m-%d_%H_%M")
today_str = "2020-04-02_19_15"
def get_op_config():
    cur_config = {
        WorldLitter.years: np.arange(2010, 2011),
        WorldLitter.base_folder: "/home/data/UN_Litter_data/HYCOM/",
        WorldLitter.loc_folder: "data/release_locations",
        WorldLitter.output_folder: "/home/data/UN_Litter_data/output/",
        WorldLitter.output_file: F"{today_str}_output.nc",
        WorldLitter.lat_files: ["coasts_all_y.cvs", "rivers_all_y.cvs"],
        WorldLitter.lon_files: ["coasts_all_x.cvs", "rivers_all_x.cvs"],
        # lat_files = ["river_cat_1_x.cvs"]
        # lon_files = ["river_cat_1_y.cvs"]
        WorldLitter.wind_factor: 0.035,
        WorldLitter.run_time: timedelta(hours=2),   # 365
        WorldLitter.repeat_release: timedelta(minutes=60),  # 61
        WorldLitter.output_freq: timedelta(hours=1),  # 24

        WorldLitter.output_folder_web: "/var/www/html/data",
        WorldLitter.countries_file: "/home/data/UN_Litter_data/Particles_by_Country.csv"
    }
    return cur_config

#
# # ------- LOCAL MACHINE ---------
# def get_config():
#     cur_config = {
#         WorldLitter.years: np.arange(2010, 2016),
#         WorldLitter.base_folder: "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/",
#         WorldLitter.loc_folder: "data/release_locations",
#         WorldLitter.output_file: F"/data/UN_Litter_data/Output/{today_str}_output.nc",
#         WorldLitter.lat_files: ["coasts_all_y.cvs", "rivers_all_y.cvs"],
#         WorldLitter.lon_files: ["coasts_all_x.cvs", "rivers_all_x.cvs"],
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
#             WorldLitter.lat_files: ["coasts_all_y.cvs", "rivers_all_y.cvs"],
#             WorldLitter.lon_files: ["coasts_all_x.cvs", "rivers_all_x.cvs"],
#             WorldLitter.wind_factor: 0.035
#         }
#         return cur_config