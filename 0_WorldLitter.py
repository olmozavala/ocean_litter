from parcels import Field, FieldSet, ParticleSet, Variable, JITParticle, ScipyParticle
from parcels import plotTrajectoriesFile, ErrorCode, VectorField, AdvectionRK4
import numpy as np
from datetime import timedelta, datetime, date
from os.path import join
from kernels.wl_kernels import periodicBC, AdvectionRK4Beached, UnBeaching, BeachTesting_2D, BrownianMotion2D, BrownianMotion2DUnbeaching
import parcels.plotting as pplt
from parcels.scripts import *
from utils.io_hycom import read_files
import functools
from config.params import WorldLitter
from config.MainConfig import get_op_config
import sys
from netCDF4 import Dataset
import os
import xarray as xr
import time
try:
    from mpi4py import MPI
except:
    MPI = None

def outOfBounds(particle, fieldset, time):
    particle.beached = 4

class PlasticParticle(JITParticle):
# class PlasticParticle(ScipyParticle):
    # beached : 0 sea, 1 after RK, 2 after diffusion, 3 please unbeach, 4 final beached (and out of bounds)
    beached = Variable('beached', dtype=np.int32, initial=0.)
    beached_count = Variable('beached_count', dtype=np.int32, initial=0.)

def add_Kh(winds_currents_fieldset, lat, lon, kh):
    kh_mer = Field('Kh_meridional', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                   lon=lon, lat=lat, allow_time_extrapolation=True,
                   fieldtype='Kh_meridional', mesh='spherical')
    kh_zonal = Field('Kh_zonal', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                     lon=lon, lat=lat, allow_time_extrapolation=True,
                     fieldtype='Kh_zonal', mesh='spherical')

    winds_currents_fieldset.add_field(kh_mer, 'Kh_meridional')
    winds_currents_fieldset.add_field(kh_zonal, 'Kh_zonal')

def set_unbeaching(winds_currents_fieldset, lat, lon, input_file):
    ds = Dataset(input_file, "r+", format="NETCDF4")

    unBeachU= Field('unBeachU', ds['unBeachU'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_meridional', mesh='spherical')
    unBeachV= Field('unBeachV', ds['unBeachV'][:,:],
                    lon=lon, lat=lat, allow_time_extrapolation=True,
                    fieldtype='Kh_zonal', mesh='spherical')

    winds_currents_fieldset.add_field(unBeachU, 'unBeachU')
    winds_currents_fieldset.add_field(unBeachV, 'unBeachV')


def main(start_date = -1, end_date = -1, name='', winds=True, diffusion=True, unbeaching=True, restart_file=""):
    config = get_op_config()
    years = config[WorldLitter.years]
    base_folder = config[WorldLitter.base_folder]
    release_loc_folder = config[WorldLitter.loc_folder]
    output_file = join(config[WorldLitter.output_folder], F"{name}{config[WorldLitter.output_file]}")
    unbeach_file = config[WorldLitter.unbeach_file]
    lat_files = config[WorldLitter.lat_files]
    lon_files = config[WorldLitter.lon_files]
    dt = config[WorldLitter.dt]
    kh = 1
    repeat_release = config[WorldLitter.repeat_release]
    if start_date == -1:
        start_date = config[WorldLitter.start_date]
    if end_date == -1:
        end_date = config[WorldLitter.end_date]
    run_time = timedelta(seconds=(end_date - start_date).total_seconds())

    file_names = read_files(base_folder, years, wind=winds, start_date=start_date, end_date=end_date)
    if len(file_names) == 0:
        print(F"ERROR: We couldn't read any file! BaseFolder:{base_folder}")
        exit()

    print("Reading initial positions.....")
    lat0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
    lon0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

    #variables = {'U': 'U_combined',
    #'V': 'V_combined'}
    variables = {'U': 'surf_u',
                 'V': 'surf_v'}

    #dimensions = {'lat': 'lat',
    #'lon': 'lon',
    dimensions = {'lat': 'latitude',
                  'lon': 'longitude',
                  'time': 'time'}

    print("Reading data.....", flush=True)
    # Adding the vector fields it may be currents or currents + winds
    winds_currents_fieldset = FieldSet.from_netcdf(file_names, variables, dimensions,
                                                   allow_time_extrapolation=True,
                                                   field_chunksize=(2048,2048))
    # -------  Making syntetic diffusion coefficient
    U_grid = winds_currents_fieldset.U.grid
    lat = U_grid.lat
    lon = U_grid.lon
    # Getting proporcional size by degree
    if diffusion:
        print("Adding diffusion .....")
        add_Kh(winds_currents_fieldset, lat, lon, kh)
    if unbeaching:
        print("Adding unbeaching.....")
        set_unbeaching(winds_currents_fieldset, lat, lon, unbeach_file)

    # -------  Adding constants for periodic halo
    winds_currents_fieldset.add_constant('halo_west', winds_currents_fieldset.U.grid.lon[0])
    winds_currents_fieldset.add_constant('halo_east', winds_currents_fieldset.U.grid.lon[-1])
    winds_currents_fieldset.add_periodic_halo(zonal=True)                                   #create a zonal halo


    print("Setting up everything.....")
    if unbeaching:
        particle_class = PlasticParticle
    else:
        particle_class = JITParticle

    if restart_file != '':
        pset = ParticleSet.from_particlefile(fieldset=winds_currents_fieldset, pclass=particle_class,
                                             filename=restart_file, repeatdt=repeat_release)
    else:
        pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=particle_class, lon=lon0, lat=lat0,
                           repeatdt=repeat_release)


    print(F"Running with {pset.size} particles")
    out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[WorldLitter.output_freq])
    t = time.time()

    print(F"Running for {run_time} hour", flush=True)
    if unbeaching:
        kernels = pset.Kernel(AdvectionRK4Beached)
    else:
        kernels = pset.Kernel(AdvectionRK4)

    if unbeaching:
        kernels += pset.Kernel(BeachTesting_2D)
        kernels += pset.Kernel(UnBeaching)
        if diffusion:
            kernels += pset.Kernel(BrownianMotion2DUnbeaching)
            kernels += pset.Kernel(BeachTesting_2D)
    else:
        if diffusion:
            kernels += pset.Kernel(BrownianMotion2D)

    kernels += pset.Kernel(periodicBC)

    # When unbeaching the order of the kernels are: RK4, BeachTesting, Unbeaching, Diffussioon, BeachTesting
    pset.execute(kernels,
                 runtime=run_time,
                 dt=dt,
                 output_file=out_parc_file,
                 recovery={ErrorCode.ErrorOutOfBounds: outOfBounds})

    print(F"Done time={time.time()-t}.....")

    print(F"Saving output to {output_file}!!!!!")
    # domain = {'N': 31, 'S': 16, 'E': -76, 'W': -98}
    # pset.show(field=winds_currents_fieldset.U, domain=domain)  # Draw current particles
    out_parc_file.export() # Save trajectories to file
    # plotTrajectoriesFile(output_file) # Plotting trajectories
    print("Done!!!!!!!!!!!! YEAH BABE!!!!!!!!")

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1", "True")

def get_file_name(name, start_date, end_date, part_n):
    time_format_red = "%Y-%m-%d"
    return F"{name}_{start_date.strftime(time_format_red)}_{end_date.strftime(time_format_red)}__{part_n:02d}_"


# THis should be improved it was copied from 0_WorldLItterSplitter to work with mpi
def runWithRestart():
    execution_days = 30
    time_format = "%Y-%m-%d:%H"
    time_format_red = "%Y-%m-%d"
    config = get_op_config()

    start_date = datetime.strptime(sys.argv[1], time_format)
    end_date = datetime.strptime(sys.argv[2], time_format)
    winds = str2bool(sys.argv[3])
    diffusion = str2bool(sys.argv[4])
    unbeaching = str2bool(sys.argv[5])
    name = sys.argv[6]
    part_n = 0

    # =================== Computing all the models in 'batches' =====================
    # --------- First run, no restart file needed ----------
    cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
    cur_name = get_file_name(name, start_date, cur_end_date, part_n)
    run = F"python 0_WorldLitter.py {start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} " \
          F"{winds} {diffusion} {unbeaching} {cur_name}"
    print(F"Running: {run}")
    main(start_date, cur_end_date, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)
    #
    # # --------- Iterate over all the rest of the models, specify the resart file in each case
    while(cur_end_date < end_date):
        prev_start_date = start_date
        prev_end_date = cur_end_date
        start_date = cur_end_date # We need to add one or we will repeat a day
        cur_end_date = min(start_date + timedelta(days=execution_days), end_date)
        # Define the restart file to use (previous output file)
        restart_file = join(config[WorldLitter.output_folder], F"{get_file_name(name, prev_start_date, prev_end_date, part_n)}{config[WorldLitter.output_file]}")

        if MPI:
            print(F"----- Waiting for file {part_n:02d} to be saved proc {MPI.COMM_WORLD.Get_rank()} ... ---------", flush=True)
            MPI.COMM_WORLD.Barrier()
            print("Done waiting!", flush=True)

        print(F" ================================================================================= ")
        print(F" ================================================================================= ")
        print(F" ================================================================================= ")

        # Define the new output file name
        part_n += 1
        cur_name = get_file_name(name, start_date, cur_end_date, part_n)
        run = F"{start_date.strftime(time_format)} {cur_end_date.strftime(time_format)} " \
              F"winds:{winds}  diff:{diffusion}  unbeaching:{unbeaching}  name:{cur_name}  restart:{restart_file}"
        print(F"Running with: {run}")
        main(start_date, cur_end_date, cur_name, winds=winds, unbeaching=unbeaching, diffusion=diffusion, restart_file=restart_file)

    # =================== Here we merge all the output files into one ===========================
    if MPI:
        print(F"----Waiting for file {part_n:02d} to be saved proc {MPI.COMM_WORLD.Get_rank()} ... -------------" , flush=True)
        MPI.COMM_WORLD.Barrier()
        print("Done waiting!", flush=True)

    print(F" ================================================================================= ")
    print(F" ================================================================================= ")
    print(F" ================================================================================= ")

    exec_next = True
    if MPI:
        if MPI.COMM_WORLD.Get_rank() != 0:
            exec_next = False # The next code we want that only a single CPU executes it

    if exec_next:
        start_date = datetime.strptime(sys.argv[1], time_format)
        end_date = datetime.strptime(sys.argv[2], time_format)
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
        input_file = F"{name}_{start_date.strftime(time_format_red)}_{cur_end_date.strftime(time_format_red)}__{part_n:02d}_"
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
    if len(sys.argv) > 6:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        winds = str2bool(sys.argv[3])
        diffusion = str2bool(sys.argv[4])
        unbeaching = str2bool(sys.argv[5])
        name = sys.argv[6]
        print(F"Start date: {start_date} End date: {end_date} winds={winds} diffusion={diffusion} unbeaching={unbeaching}")
        if len(sys.argv) > 7:
            # restart_file = sys.argv[7]
            # main(start_date, end_date, name, winds=winds, unbeaching=unbeaching,
            #      diffusion=diffusion, restart_file=restart_file)
            print("Running with restart!!!!! Splitter wont work!!!")
            runWithRestart()
        else:
            main(start_date, end_date, name, winds=winds, unbeaching=unbeaching,
                 diffusion=diffusion)
    else:
        print("Not enough parameters, using defaults!!!!")
        main()
