from parcels import Field, FieldSet, ParticleSet, Variable, JITParticle, ScipyParticle
from parcels import plotTrajectoriesFile, ErrorCode, VectorField
import numpy as np
from datetime import timedelta, datetime, date
import time
from os.path import join
from kernels.wl_kernels import periodicBC, AdvectionRK4, UnBeaching, BeachTesting_2D, BrownianMotion2D
import parcels.plotting as pplt
from parcels.scripts import *
from utils.io_hycom import read_files
import functools
from config.params import WorldLitter
from config.MainConfig import get_op_config
import sys
from netCDF4 import Dataset

def outOfBounds(particle, fieldset, time):
    particle.beached = 4


class PlasticParticle(JITParticle):
    # age = Variable('age', dtype=np.float32, initial=0.)
    # beached : 0 sea, 1 beached,  2  please unbeach
    beached = Variable('beached', dtype=np.int32, initial=0.)

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


def main(start_date = -1, end_date = -1, name='', winds=True, diffusion=True, unbeaching=True):
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
    if repeat_release:
        pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=PlasticParticle, lon=lon0, lat=lat0,
                           repeatdt=repeat_release)
    else:
        pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=PlasticParticle, lon=lon0, lat=lat0)

    print(F"Running with {pset.size} number of particles")
    out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[WorldLitter.output_freq])
    t = time.time()

    print(F"Running for {run_time} hour", flush=True)
    kernels = pset.Kernel(AdvectionRK4)
    if unbeaching:
        kernels += pset.Kernel(BeachTesting_2D)
        kernels += pset.Kernel(UnBeaching)
    if diffusion:
        kernels += pset.Kernel(BrownianMotion2D)
        kernels += pset.Kernel(BeachTesting_2D)

    kernels += pset.Kernel(periodicBC)

    pset.execute(kernels,
                runtime=run_time,
                 dt=dt,
                 output_file=out_parc_file,
                recovery = {ErrorCode.ErrorOutOfBounds: outOfBounds})

    print(F"Done time={time.time()-t}.....")

    print("Saving output!!!!!")
    # domain = {'N': 31, 'S': 16, 'E': -76, 'W': -98}
    # pset.show(field=winds_currents_fieldset.U, domain=domain)  # Draw current particles
    out_parc_file.export() # Save trajectories to file
    # plotTrajectoriesFile(output_file) # Plotting trajectories
    print("Done!!!!!!!!!!!! YEAH BABE!!!!!!!!")

if __name__ == "__main__":
    if len(sys.argv) >= 6:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d:%H")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d:%H")
        winds = bool(sys.argv[3])
        diffusion = bool(sys.argv[4])
        unbeaching = bool(sys.argv[5])
        name = sys.argv[6]
        print(F"Start date: {start_date} End date: {end_date}")
        main(start_date, end_date, name, winds=winds, unbeaching=unbeaching, diffusion=diffusion)
    else:
        print("Not enough parameters, using defaults!!!!")
        main()
