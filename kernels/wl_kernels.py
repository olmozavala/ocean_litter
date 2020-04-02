from parcels import rng as random
import math

def periodicBC(particle, fieldset, time):
    if particle.lon < fieldset.halo_west:
        particle.lon += fieldset.halo_east - fieldset.halo_west            #if a particle falls into halo west, its lon is corrected
    elif particle.lon > fieldset.halo_east:
        particle.lon -= fieldset.halo_east - fieldset.halo_west


def BrownianMotion2D_OZ(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    r = 1/3.
    kh_meridional = fieldset.U[time, particle.depth, particle.lat, particle.lon]
    particle.lat += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_meridional/r)
    kh_zonal = fieldset.V[time, particle.depth, particle.lat, particle.lon]
    particle.lon += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_zonal/r)