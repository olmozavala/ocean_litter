from parcels import FieldSet, ParticleSet, Variable, JITParticle, AdvectionRK4
import numpy as np
from datetime import timedelta, datetime
import time
from os.path import join
import parcels.plotting as pplt
from parcels.scripts import *
import functools

today_str = datetime.today().strftime("%Y-%m-%d_%H_%M")

# -------------- LOCAL MACHINE ----------------
# filenames = "/p/work1/xbxu/hycom/GLBb0.08/NetCDF/K17/039_archm.*_12_K17_quvc.nc"
# filenames = "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/2010/*.nc"
# filenames = "/data/COAPS_nexsan/people/xbxu/hycom/GLBv0.08/2010/hycom_GLBv0.08_536_201001021*.nc"
# release_loc_folder = "release_locations"
# output_file = F'/data/UN_Litter_data/Output/{today_str}_output.nc'

# -------------- COAPS MACHINE ----------------
filenames = "/nexsan/people/xbxu/hycom/GLBv0.08/2010/*.nc"
# release_loc_folder = "/home/xbxu/hycom/GLBv0.08/release_locations"
release_loc_folder = "release_locations"
output_file = F'/Net/work/ozavala/WorldLitterOutput/{today_str}_output.nc'

# lat_files = ['river_cat_1_x.cvs']
# lon_files = ['river_cat_1_y.cvs']
lat_files = ['coasts_all_y.cvs', 'rivers_all_y.cvs']
lon_files = ['coasts_all_x.cvs','rivers_all_x.cvs']

print("Reading initial positions.....")
lat0 = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lat_files])
lon0 = functools.reduce(lambda a,b: np.concatenate((a,b), axis=0),
                      [np.genfromtxt(join(release_loc_folder, x), delimiter='') for x in lon_files])


variables = {'U': 'surf_u',
             'V': 'surf_v'}
dimensions = {'lat': 'latitude',
              'lon': 'longitude',
              'time': 'time'}

print("Reading data.....")
fieldset = FieldSet.from_netcdf(filenames, variables, dimensions,allow_time_extrapolation=True)     #Defining the velocity field


print("Setting up everything.....")
#periodic boundary
fieldset.add_constant('halo_west', fieldset.U.grid.lon[0])
fieldset.add_constant('halo_east', fieldset.U.grid.lon[-1])
fieldset.add_periodic_halo(zonal=True)                                   #create a zonal halo

#periodic boundary kernal
def periodicBC(particle, fieldset, time):
    if particle.lon < fieldset.halo_west:
        particle.lon += fieldset.halo_east - fieldset.halo_west            #if a particle falls into halo west, its lon is corrected
    elif particle.lon > fieldset.halo_east:
        particle.lon -= fieldset.halo_east - fieldset.halo_west


pset = ParticleSet(fieldset=fieldset, pclass=JITParticle, lon=lon0, lat=lat0)

print("Running.....")
out_parc_file = pset.ParticleFile(name=output_file, outputdt=timedelta(hours=24))
t = time.time()
pset.execute(AdvectionRK4+pset.Kernel(periodicBC),
# pset.execute(AdvectionRK4,
             runtime=timedelta(days=365),
             dt=timedelta(minutes=60),
             output_file=out_parc_file)

print(F"Done time={time.time()-t}.....")

print("Plotting output........")
out_parc_file.export() # Save trajectories to file
# plotTrajectoriesFile(output_file) # Plotting trajectories
