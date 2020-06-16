from datetime import timedelta, datetime, date
from netCDF4 import Dataset
import xarray as xr
import sys
import os
from os.path import join
from config.MainConfig import get_op_config
from config.params import WorldLitter
import numpy as np

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1", "True")

if __name__ == "__main__":
    execution_days = 2
    time_format = "%Y-%m-%d:%H"
    time_format_red = "%Y_%m_%d"
    config = get_op_config()

    if len(sys.argv) >= 6:
        start_date = datetime.strptime(sys.argv[1], time_format)
        end_date = datetime.strptime(sys.argv[2], time_format)
        winds = str2bool(sys.argv[3])
        diffusion = str2bool(sys.argv[4])
        unbeaching = str2bool(sys.argv[5])
        name = sys.argv[6]
        part_n = 0

        # =================== Computing all the models in 'batches' =====================
        # # --------- First run, no restart file needed ----------
        # cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        # cur_name = F"{name}_{start_date.strftime(time_format_red)}-{cur_end_date.strftime(time_format_red)}__{part_n:02d}_"
        # run = F"python 0_WorldLitter.py {start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} " \
        #       F"{winds} {diffusion} {unbeaching} {cur_name}"
        # print(F"Running: {run}")
        # os.system(run)
        #
        # # --------- Iterate over all the rest of the models, specify the resart file in each case
        # while(cur_end_date < end_date):
        #     prev_start_date = start_date
        #     prev_end_date = cur_end_date
        #     start_date = cur_end_date + timedelta(days=1) # We need to add one or we will repeat a day
        #     cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        #     # Define the restart file to use (previous output file)
        #     restart_file = join(config[WorldLitter.output_folder],
        #                         F"{name}_{prev_start_date.strftime(time_format_red)}-{prev_end_date.strftime(time_format_red)}__{part_n:02d}_{config[WorldLitter.output_file]}")
        #     restart_file = join(config[WorldLitter.output_folder],
        #                         F"{name}_{prev_start_date.strftime(time_format_red)}-{prev_end_date.strftime(time_format_red)}__{part_n:02d}_{config[WorldLitter.output_file]}")
        #     # Define the new output file name
        #     part_n += 1
        #     cur_name = F"{name}_{start_date.strftime(time_format_red)}-{cur_end_date.strftime(time_format_red)}__{part_n:02d}_"
        #     run = F"python 0_WorldLitter.py {start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} " \
        #           F"{winds} {diffusion} {unbeaching} {cur_name} {restart_file}"
        #     print(F"Running: {run}")
        #     os.system(run)

        # =================== Here we merge all the output files into one ===========================
        start_date = datetime.strptime(sys.argv[1], time_format)
        end_date = datetime.strptime(sys.argv[2], time_format)
        cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        part_n = 0
        while(cur_end_date < end_date):
            input_file = F"{name}_{start_date.strftime(time_format_red)}-{cur_end_date.strftime(time_format_red)}__{part_n:02d}_"
            restart_file = join(config[WorldLitter.output_folder], F"{input_file}{config[WorldLitter.output_file]}")
            if part_n == 0:
                merged_data = xr.open_dataset(restart_file)
                time = merged_data['time'].copy()
                trajectory = merged_data['trajectory'].copy()
                lat = merged_data['lat'].copy()
                lon = merged_data['lon'].copy()
                z = merged_data['z'].copy()
                obs = merged_data['obs'].copy()
            else:
                temp_data = xr.open_dataset(restart_file)
                time = xr.concat([time, temp_data['time']], dim='obs')
                trajectory = xr.concat([trajectory, temp_data['trajectory']], dim='obs')
                lat = xr.concat([lat, temp_data['lat']], dim='obs')
                lon = xr.concat([lon, temp_data['lon']], dim='obs')
                z = xr.concat([z, temp_data['z']], dim='obs')
            start_date = cur_end_date + timedelta(days=1) # We need to add one or we will repeat a day
            cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
            part_n += 1


        # Last call
        input_file = F"{name}_{start_date.strftime(time_format_red)}-{cur_end_date.strftime(time_format_red)}__{part_n:02d}_"
        restart_file = join(config[WorldLitter.output_folder], F"{input_file}{config[WorldLitter.output_file]}")
        temp_data = xr.open_dataset(restart_file)
        time = xr.concat([time, temp_data['time']], dim='obs')
        trajectory = xr.concat([trajectory, temp_data['trajectory']], dim='obs')
        lat = xr.concat([lat, temp_data['lat']], dim='obs')
        lon = xr.concat([lon, temp_data['lon']], dim='obs')
        z = xr.concat([z, temp_data['z']], dim='obs')

        # Here we have all the variables merged, we need to create a new Dataset and save it
        ds = xr.Dataset(
        {
            "time": (("traj", "obs"), time),
            "trajectory": (("traj", "obs"), trajectory),
            "lat": (("traj", "obs"), lat),
            "lon": (("traj", "obs"), lon),
            "z": (("traj", "obs"), z),
        }
        )
        ds.attrs = temp_data.attrs

        output_file = join(config[WorldLitter.output_folder], F"{name}{config[WorldLitter.output_file]}")
        ds.to_netcdf(output_file)
        print("Done!")

    else:
        print(F"ERROR we are expecting 6 arguments, only {len(sys.argv)} were received!!!!")
