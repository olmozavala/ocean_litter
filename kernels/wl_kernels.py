from parcels import rng as random
import math
import numpy as np
from parcels import AdvectionRK4

def periodicBC(particle, fieldset, time):
    if particle.lon < fieldset.halo_west:
        particle.lon += fieldset.halo_east - fieldset.halo_west            #if a particle falls into halo west, its lon is corrected
    elif particle.lon > fieldset.halo_east:
        particle.lon -= fieldset.halo_east - fieldset.halo_west

def RandomWalkSphere(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""

    # lat_diff_coeff = math.sin(math.fabs(math.radians(particle.lat)))  # latitude
    lat_diff_coeff = math.sin(math.fabs(math.pi*particle.lat/180))
    df = 1  # Diffussion coefficient
    r_lat = random.uniform(-1., 1.)
    r_lon = random.uniform(-1., 1.)
    particle.lat += df*r_lat*lat_diff_coeff
    particle.lon += df*r_lon*lat_diff_coeff

def BrownianMotion2D_OZ(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    r = 1
    # kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
    kh_meridional = 1
    particle.lat += random.uniform(-1., 1.) * math.sqrt(2 *kh_meridional / (particle.dt *r))
    # kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
    kh_zonal = 1
    particle.lon += random.uniform(-1., 1.) * math.sqrt(2 * kh_zonal / (particle.dt *r))

def BrownianMotion2D(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    r = 1/3.
    kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
    particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
    kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
    particle.lon += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_zonal/r)

# def BrownianMotion2D_OZ(particle, fieldset, time):
#     """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
#     Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
#     r = 1/3.
#     print("time: %f depth: %f lon: %f, lat: %f, dt: %f" % (time, particle.depth, particle.lon, particle.lat, particle.dt))
#     kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
#     print("Mer: %f" % (kh_meridional))
#     a = (2 * math.fabs(particle.dt) * kh_meridional)
#     print("1: %f" % (a))
#     b = (2 * math.fabs(particle.dt) * kh_meridional / r)
#     print("2: %f" % (b))
#     c = (math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r))
#     print("3: %f" % (c))
#     d = (random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r))
#     print("4: %f" % (d))
#
#     temp = random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
#     print("temp_kh_mer %f" % (temp))
#     particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
#
#     kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
#     print("Zon: %f" % (kh_zonal))
#     temp = random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_zonal/r)
#     print("temp_kh_zon %f" % (temp))
#     particle.lon += random.uniform(-1., 1.) * math.sqrt(2*math.fabs(particle.dt)*kh_zonal/r)