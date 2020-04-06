from parcels import Field, FieldSet, ParticleSet, Variable, JITParticle, AdvectionRK4, plotTrajectoriesFile
import numpy as np
from datetime import timedelta, datetime
import time
from os.path import join
from kernels.wl_kernels import periodicBC, RandomWalkSphere, BrownianMotion2D_OZ
import parcels.plotting as pplt
from parcels.scripts import *
from utils.io_hycom import read_files
import os
import functools
from config.params import WorldLitter
from config.MainConfig import get_op_config

wind_factor = .035
def main():
    config = get_op_config()
    years = config[WorldLitter.years]
    base_folder = config[WorldLitter.base_folder]
    release_loc_folder = config[WorldLitter.loc_folder]
    output_file = join(config[WorldLitter.output_folder], config[WorldLitter.output_file])
    lat_files = config[WorldLitter.lat_files]
    lon_files = config[WorldLitter.lon_files]

    file_names = read_files(base_folder, years)

    print("Reading initial positions.....")
    lat0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
    lon0 = functools.reduce(lambda a, b: np.concatenate((a,b), axis=0), [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])

    variables = {'U': 'surf_u',
                 'V': 'surf_v'}

    dimensions = {'lat': 'latitude',
                  'lon': 'longitude',
                  'time': 'time'}

    print("Reading data.....")
    # Adding the currents field
    winds_currents_fieldset = FieldSet.from_netcdf(file_names, variables, dimensions,
                                                   allow_time_extrapolation=True)

    # -------  Adding constants for periodic halo
    winds_currents_fieldset.add_constant('halo_west', winds_currents_fieldset.U.grid.lon[0])
    winds_currents_fieldset.add_constant('halo_east', winds_currents_fieldset.U.grid.lon[-1])
    winds_currents_fieldset.add_periodic_halo(zonal=True)                                   #create a zonal halo

    # -------  Making syntetic diffusion coefficient
    # U_grid = winds_currents_fieldset.U.grid
    # grid = np.meshgrid(U_grid.lon, U_grid.lat)
    # lat = U_grid.lat
    # lon = U_grid.lon
    # # Getting proporcional size by degree
    # lat_diff_coeff = np.sin(np.abs(np.deg2rad(grid[1])))  # latitude
    # df_coeff_field = Field('diff_coeff', lat_diff_coeff, lat=lat, lon=lon)
    # winds_currents_fieldset.add_field(df_coeff_field, 'diff_coeff')

    print("Setting up everything.....")
    pset = ParticleSet(fieldset=winds_currents_fieldset, pclass=JITParticle, lon=lon0, lat=lat0,
                       repeatdt=timedelta(days=61))

    print("Running.....")
    out_parc_file = pset.ParticleFile(name=output_file, outputdt=config[WorldLitter.output_freq])
    t = time.time()
    # pset.execute(AdvectionRK4 + pset.Kernel(periodicBC),
    # pset.execute(AdvectionRK4 + pset.Kernel(RandomWalkSphere),
    # pset.execute(AdvectionRK4 + pset.Kernel(BrownianMotion2D_OZ),
    pset.execute(AdvectionRK4,
                 runtime=config[WorldLitter.run_time],
                 dt=timedelta(minutes=60),
                 output_file=out_parc_file)
    # pset.execute(AdvectionRK4 + BrownianMotion2D_OZ,
    #              runtime=timedelta(hours=6),
    #              dt=timedelta(minutes=60),
    #              output_file=out_parc_file)

    print(F"Done time={time.time()-t}.....")

    print("Plotting output........")
    # domain = {'N': 31, 'S': 16, 'E': -76, 'W': -98}
    # pset.show(field=winds_currents_fieldset.U, domain=domain)  # Draw current particles
    out_parc_file.export() # Save trajectories to file
    # plotTrajectoriesFile(output_file) # Plotting trajectories

if __name__ == "__main__":
    main()
