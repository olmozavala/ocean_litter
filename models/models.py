import gc
from config.params import WorldLitter
from os.path import join
from datetime import timedelta
from utils.io_hycom import read_files
import functools
import numpy as np
from parcels import FieldSet, JITParticle, ScipyParticle, ParticleSet, ErrorCode, AdvectionRK4
from utils.io_hycom import add_Kh, add_unbeaching_field
from mykernels.custom_particles import LitterParticle
from mykernels.wl_kernels import *
import time
try:
    from mpi4py import MPI
except:
    MPI = None

def sequential(start_date, end_date, config, name='', winds=True, diffusion=True, unbeaching=True, restart_file=""):
    # years = config[WorldLitter.years]
    years = np.arange(start_date.year, end_date.year+1)
    base_folder = config[WorldLitter.base_folder]
    release_loc_folder = config[WorldLitter.loc_folder]
    output_file = join(config[WorldLitter.output_folder], name)
    unbeach_file = config[WorldLitter.unbeach_file]
    lat_files = config[WorldLitter.lat_files]
    lon_files = config[WorldLitter.lon_files]
    dt = config[WorldLitter.dt]
    kh = 1
    repeat_release = config[WorldLitter.repeat_release]

    run_time = timedelta(seconds=(end_date - start_date).total_seconds())

    file_names = read_files(base_folder, years, wind=winds, start_date=start_date, end_date=end_date)
    if len(file_names) == 0:
        raise Exception("ERROR: We couldn't read any file!")

    print("Reading initial positions.....")
    lat0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
    lon0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

    variables = {'U': 'surf_u',
                 'V': 'surf_v'}

    dimensions = {'lat': 'latitude',
                  'lon': 'longitude',
                  'time': 'time'}

    print("Reading netcdf files.....", flush=True)
    # Adding the vector fields it may be currents or currents + winds
    main_fieldset = FieldSet.from_netcdf(file_names, variables, dimensions,
                                                   allow_time_extrapolation=True,
                                                   field_chunksize=(2048,2048))
    # -------  Making syntetic diffusion coefficient
    U_grid = main_fieldset.U.grid
    lat = U_grid.lat
    lon = U_grid.lon
    # Getting proporcional size by degree
    if diffusion:
        print("Adding diffusion .....")
        add_Kh(main_fieldset, lat, lon, kh)
    if unbeaching:
        print("Adding unbeaching.....")
        add_unbeaching_field(main_fieldset, lat, lon, unbeach_file)

    # -------  Adding constants for periodic halo
    main_fieldset.add_constant('halo_west', main_fieldset.U.grid.lon[0])
    main_fieldset.add_constant('halo_east', main_fieldset.U.grid.lon[-1])
    main_fieldset.add_periodic_halo(zonal=True)                                   #create a zonal halo


    print("Setting up everything.....")
    if unbeaching:
        particle_class = LitterParticle
    else:
        particle_class = JITParticle

    if restart_file != '':
        print(F"Using restart file {restart_file}")
        pset = ParticleSet.from_particlefile(fieldset=main_fieldset, pclass=particle_class,
                                             filename=restart_file, repeatdt=repeat_release)
    else:
        pset = ParticleSet(fieldset=main_fieldset, pclass=particle_class, lon=lon0, lat=lat0,
                           repeatdt=repeat_release)


    out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[WorldLitter.output_freq])
    t = time.time()

    print(F"Adding kernels...")
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

    print(F"Running with {pset.size} number of particles for {run_time}", flush=True)
    pset.execute(kernels,
                 runtime=run_time,
                 dt=dt,
                 output_file=out_parc_file,
                 recovery={ErrorCode.ErrorOutOfBounds: outOfBounds})

    print(F"Done time={time.time()-t}.....")

    print(F"Saving output to {output_file}!!!!!")
    # domain = {'N': 31, 'S': 16, 'E': -76, 'W': -98}
    # pset.show(field=main_fieldset.U, domain=domain)  # Draw current particles
    out_parc_file.export() # Save trajectories to file

    if MPI:
        print(F"----- Waiting for file to be saved proc {MPI.COMM_WORLD.Get_rank()} ... ---------", flush=True)
        MPI.COMM_WORLD.Barrier()

    # out_parc_file.close()
    # del pset
    # del kernels
    # del main_fieldset
    # # plotTrajectoriesFile(output_file) # Plotting trajectories
    # print("Forcing gc.collect")
    # gc.collect()

    print("Done!!!!!!!!!!!! YEAH BABE!!!!!!!!", flush=True)
