from datetime import timedelta, datetime, date
from os.path import join
from utils.several_utils import get_file_name, str2bool
from config.params import WorldLitter
import sys
import xarray as xr
from config.MainConfig import get_op_config
try:
    from mpi4py import MPI
except:
    MPI = None

def mergeFiles(config, name, start_date, end_date, execution_days, unbeaching):
    """
    This code merges previous runs. It takes into account the 'extra' date that is repeated for each splitted file
    :param config:
    :param start_date:
    :param end_date:
    :param execution_days:
    :return:
    """
    exec_next = True
    if MPI:
        if MPI.COMM_WORLD.Get_rank() != 0:
            exec_next = False # The next code we want that only a single CPU executes it

    if exec_next:
        cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        part_n = 0
        while(cur_end_date < end_date):
            input_file = get_file_name(name, start_date, cur_end_date, part_n)
            restart_file = join(config[WorldLitter.output_folder], F"{input_file}{config[WorldLitter.output_file]}")
            print(F"Reading restart file: {restart_file}")
            if part_n == 0:
                merged_data = xr.open_dataset(restart_file)
                timevar = merged_data['time'].copy()
                trajectory = merged_data['trajectory'].copy()
                lat = merged_data['lat'].copy()
                lon = merged_data['lon'].copy()
                z = merged_data['z'].copy()
                if(unbeaching):
                    beached = merged_data['beached'].copy()
                    beached_count = merged_data['beached_count'].copy()

            else:
                temp_data = xr.open_dataset(restart_file)
                timevar = xr.concat([timevar, temp_data['time'][:,1:]], dim='obs')
                trajectory = xr.concat([trajectory, temp_data['trajectory'][:,1:]], dim='obs')
                lat = xr.concat([lat, temp_data['lat'][:,1:]], dim='obs')
                lon = xr.concat([lon, temp_data['lon'][:,1:]], dim='obs')
                z = xr.concat([z, temp_data['z'][:,1:]], dim='obs')
                if(unbeaching):
                    beached = xr.concat([beached, temp_data['beached'][:,1:]], dim='obs')
                    beached_count = xr.concat([beached_count, temp_data['beached_count'][:,1:]], dim='obs')

            start_date = cur_end_date # We need to add one or we will repeat a day
            cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
            part_n += 1
            print("Done adding this file!")

        # Last call
        print("Adding last file and merging all....")
        input_file = get_file_name(name, start_date, cur_end_date, part_n)
        restart_file = join(config[WorldLitter.output_folder], F"{input_file}{config[WorldLitter.output_file]}")
        temp_data = xr.open_dataset(restart_file)
        # The first location is already saved on the previous file
        timevar = xr.concat([timevar, temp_data['time'][:,1:]], dim='obs')
        trajectory = xr.concat([trajectory, temp_data['trajectory'][:,1:]], dim='obs')
        lat = xr.concat([lat, temp_data['lat'][:,1:]], dim='obs')
        lon = xr.concat([lon, temp_data['lon'][:,1:]], dim='obs')
        z = xr.concat([z, temp_data['z'][:,1:]], dim='obs')
        if(unbeaching):
            beached = xr.concat([beached, temp_data['beached'][:,1:]], dim='obs')
            beached_count = xr.concat([beached_count, temp_data['beached_count'][:,1:]], dim='obs')

        # Here we have all the variables merged, we need to create a new Dataset and save it
        if(unbeaching):
            ds = xr.Dataset(
                {
                    "time": (("traj", "obs"), timevar),
                    "trajectory": (("traj", "obs"), trajectory),
                    "lat": (("traj", "obs"), lat),
                    "lon": (("traj", "obs"), lon),
                    "z": (("traj", "obs"), z),
                    "beached": (("traj", "obs"), beached),
                    "beached_count": (("traj", "obs"), beached_count),
                }
            )
        else:
            ds = xr.Dataset(
                {
                    "time": (("traj", "obs"), timevar),
                    "trajectory": (("traj", "obs"), trajectory),
                    "lat": (("traj", "obs"), lat),
                    "lon": (("traj", "obs"), lon),
                    "z": (("traj", "obs"), z),
                }
            )
        ds.attrs = temp_data.attrs

        output_file = join(config[WorldLitter.output_folder], F"{name}{config[WorldLitter.output_file]}")
        ds.to_netcdf(output_file)

        print("REAL DONE DONE DONE!")

if __name__ == "__main__":
    if len(sys.argv) >= 5:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        unbeaching = str2bool(sys.argv[3])
        name = sys.argv[4]
        execution_days = int(sys.argv[5])
        config = get_op_config()
        print(F"Start date: {start_date} End date: {end_date} unbeaching={unbeaching}")
        mergeFiles(config, name, start_date, end_date, execution_days, unbeaching)
