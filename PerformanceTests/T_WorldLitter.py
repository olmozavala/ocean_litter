from parcels import Field, FieldSet, ParticleSet, Variable, JITParticle, ScipyParticle, AdvectionRK4, plotTrajectoriesFile
import numpy as np
from datetime import timedelta, datetime, date
import time
from os.path import join
from kernels.wl_kernels import periodicBC, RandomWalkSphere, BrownianMotion2D, EricSolution, BrownianMotion2D
from utils.io_hycom import read_files
import functools
from config.params import GlobalModel
from config.MainConfig import get_op_config
import sys
from netCDF4 import Dataset

def main(start_date = -1, end_date = -1, name=''):
    config = get_op_config()
    years = config[GlobalModel.years]
    base_folder = config[GlobalModel.base_folder]
    release_loc_folder = config[GlobalModel.loc_folder]
    output_file = join(config[GlobalModel.output_folder], F"{name}_{config[GlobalModel.output_file]}")
    lat_files = config[GlobalModel.lat_files]
    lon_files = config[GlobalModel.lon_files]
    dt = config[GlobalModel.dt]
    kh = 1
    repeat_release = config[GlobalModel.repeat_release]
    if start_date == -1:
        start_date = config[GlobalModel.start_date]
    if end_date == -1:
        end_date = config[GlobalModel.end_date]
    run_time = timedelta(seconds=(end_date - start_date).total_seconds())

    file_names = read_files(base_folder, years, wind=False, start_date=start_date, end_date=end_date)
    if len(file_names) == 0:
        print("ERROR: We couldn't read any file!")
        return 0

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

    print("Reading data.....")
    # Adding the currents field
    # chunk_sizes = [False, 'auto', 128, 256, 512, 1024, 2048]
    chunk_sizes = [False, 'auto', 128, 256, 512, 1024, 2048]
    for chunk_size in chunk_sizes:
        if chunk_size not in ['auto', False]:
            cs = (chunk_size, chunk_size)
            winds_currents_fieldset = FieldSet.from_netcdf(file_names, variables, dimensions,
                                                           allow_time_extrapolation=True,
                                                           field_chunksize=cs)
        else:
            winds_currents_fieldset = FieldSet.from_netcdf(file_names, variables, dimensions,
                                                           allow_time_extrapolation=True,
                                                           field_chunksize=chunk_size)

        # -------  Adding constants for periodic halo
        winds_currents_fieldset.add_constant('halo_west', winds_currents_fieldset.U.grid.lon[0])
        winds_currents_fieldset.add_constant('halo_east', winds_currents_fieldset.U.grid.lon[-1])
        winds_currents_fieldset.add_periodic_halo(zonal=True)                                   #create a zonal halo

        # -------  Making syntetic diffusion coefficient
        U_grid = winds_currents_fieldset.U.grid
        lat = U_grid.lat
        lon = U_grid.lon
        # Getting proporcional size by degree

        print("Making Kh.....")
        kh_mer = Field('Kh_meridional', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                       lon=lon, lat=lat, allow_time_extrapolation=True,
                       fieldtype='Kh_meridional', mesh='spherical')
        kh_zonal = Field('Kh_zonal', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
                       lon=lon, lat=lat, allow_time_extrapolation=True,
                       fieldtype='Kh_zonal', mesh='spherical')

        winds_currents_fieldset.add_field(kh_mer, 'Kh_meridional')
        winds_currents_fieldset.add_field(kh_zonal, 'Kh_zonal')

        print("Setting up everything.....")
        if repeat_release:
            pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=JITParticle, lon=lon0, lat=lat0,
                               repeatdt=repeat_release)
        else:
            pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=JITParticle, lon=lon0, lat=lat0)

        print(F"Running with {pset.size} number of particles", flush=True)
        out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[GlobalModel.output_freq])
        t = time.time()
        # pset.execute(AdvectionRK4,
        # pset.execute(AdvectionRK4 + pset.Kernel(periodicBC),
        # pset.execute(AdvectionRK4 + pset.Kernel(periodicBC),
        # pset.execute(AdvectionRK4 + pset.Kernel(EricSolution),
        # pset.execute(AdvectionRK4 + pset.Kernel(RandomWalkSphere),
        print(F"Running for {run_time} hour")
        pset.execute(AdvectionRK4,
                    runtime=run_time, dt=dt,
                     output_file=out_parc_file)

        print(F"####### Done time={time.time()-t} ChunkSize: {chunk_size} ####### ")
        # out_parc_file.export() # Save trajectories to file

if __name__ == "__main__":
    if len(sys.argv) == 2:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        main(start_date=start_date)
    elif len(sys.argv) == 3:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        print(F"Start date: {start_date} End date: {end_date}")
        main(start_date, end_date)
    elif len(sys.argv) == 4:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        name = sys.argv[3]
        print(F"Start date: {start_date} End date: {end_date}")
        main(start_date, end_date, name)
    else:
        main()

