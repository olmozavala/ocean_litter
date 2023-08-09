from config.params import WorldLitter
import numpy as np
from datetime import timedelta, datetime, date

#today_str = datetime.today().strftime("%Y-%m-%d_%H_%M")
today_str = ""

def get_op_config():
    cur_config = {
        WorldLitter.years: np.arange(2010, 2020),
        WorldLitter.base_folder: "/gpfs/home/osz09/scratch",
        WorldLitter.loc_folder: "/gpfs/home/osz09/ocean_litter/data/release_locations_reduced/",
        WorldLitter.unbeach_file: "/gpfs/home/osz09/scratch/unbeaching100000ms.nc",
        WorldLitter.output_folder: "/gpfs/home/osz09/scratch/output",
        WorldLitter.output_file: F"{today_str}.nc",
        WorldLitter.lat_files: ["coasts_all_y.csv", "rivers_all_y.csv"],
        WorldLitter.lon_files: ["coasts_all_x.csv", "rivers_all_x.csv"],
        WorldLitter.repeat_release: None,
        WorldLitter.output_freq: timedelta(hours=24),  # 24
        WorldLitter.dt: timedelta(hours=1),  # 1

        WorldLitter.output_folder_web: "/gpfs/home/osz09/scratch/output_web_folder",
    }
    return cur_config

