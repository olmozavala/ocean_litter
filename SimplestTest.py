from parcels import Field, FieldSet, ParticleSet, JITParticle, ScipyParticle, AdvectionRK4, BrownianMotion2D, plotTrajectoriesFile
import numpy as np
from datetime import datetime
import math
from parcels import rng as random
from parcels.scripts import *
import matplotlib.pyplot as plt

# ############### README ################
# Here I'm testing diffusion and the hability to catch nan values. If a nan
# happens, then the particle moves to a different location
# https://github.com/OceanParcels/parcels/issues/61
npart = 200

def outOfBounds(particle, fieldset, time):
    particle.lon = 10e5 * random.uniform(0., 1.)
    print(F"Out of bounds!!!", particle)

def BrownianMotion2D_OZ(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    r = 1/3.
    (u, v) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
    if math.fabs(u) < 1e-14 and math.fabs(v) < 1e-14:
        print(F"Beached!  {particle}")
        particle.lon = 20
        particle.lat = 20
    else:
        kh_meridional = fieldset.U[time, particle.depth, particle.lat, particle.lon]
        particle.lat += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_meridional/r)
        kh_zonal = fieldset.V[time, particle.depth, particle.lat, particle.lon]
        particle.lon += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_zonal/r)

today_str = datetime.today().strftime("%Y-%m-%d_%H_%M")
output_file = F'TEST_delete.nc'

xdim, ydim = (100, 100)

lat = np.linspace(0., 100, xdim, dtype=np.float32)
lon = np.linspace(0., 100, ydim, dtype=np.float32)

U = np.zeros((ydim, xdim), dtype=np.float32)  # lon
V = np.ones((ydim, xdim), dtype=np.float32)  # lat

# Just for testing the nan check at the diffusion kernel
U[40:60, 40:60] = np.nan
# plt.imshow(U)
# plt.show()

Uflow = Field('U', U, lon=lat, lat=lon, allow_time_extrapolation=True, fieldtype='U')
Vflow = Field('V', V, lon=lat, lat=lon, allow_time_extrapolation=True, fieldtype='V')

print("Making Kh.....")
kh = 1
kh_mer = Field('Kh_meridional', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
               lon=lon, lat=lat, allow_time_extrapolation=False,
               fieldtype='Kh_meridional', mesh='spherical')
kh_zonal = Field('Kh_zonal', kh * np.ones((len(lat), len(lon)), dtype=np.float32),
               lon=lon, lat=lat, allow_time_extrapolation=False,
               fieldtype='Kh_zonal', mesh='spherical')

field_set = FieldSet(Uflow, Vflow)

print("Initalizing objects........")
# Initialize Particle set object
# pset = ParticleSet(fieldset=field_set, pclass=JITParticle,
pset = ParticleSet(fieldset=field_set, pclass=ScipyParticle,
                   lon=np.linspace(20,60,npart), lat=np.linspace(20,60,npart))

out_parc_file = pset.ParticleFile(name=output_file, outputdt=1)

# Draw initial particles
print(F"Running with {pset.size} number of particles")
pset.execute(AdvectionRK4 + pset.Kernel(BrownianMotion2D_OZ), runtime=20, dt=1,
             output_file=out_parc_file)

print("Plotting saved output........")
out_parc_file.export()  # Save trajectories to file
# plotTrajectoriesFile(output_file, mode='2d')  # Plotting trajectories
# plotTrajectoriesFile(output_file, mode='3d') # Plotting trajectories
# plotTrajectoriesFile(output_file, mode='hist2d') # Plotting trajectories
# plotTrajectoriesFile(output_file, mode='movie2d') # Plotting trajectories
# Available modes are  ‘2d’, ‘3d’, ‘hist2d’,
# ‘movie2d’ and # ‘movie2d_notebook’.
# The latter two give animations, with ‘movie2d_notebook’
# specifically designed for jupyter notebooks
