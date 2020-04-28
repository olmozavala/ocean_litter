from parcels import rng as random
import math

def AdvectionRK4(particle, fieldset, time):
    if particle.beached == 0:
        (u1, v1) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        lon1, lat1 = (particle.lon + u1*.5*particle.dt, particle.lat + v1*.5*particle.dt)

        (u2, v2) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat1, lon1]
        lon2, lat2 = (particle.lon + u2*.5*particle.dt, particle.lat + v2*.5*particle.dt)

        (u3, v3) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat2, lon2]
        lon3, lat3 = (particle.lon + u3*particle.dt, particle.lat + v3*particle.dt)

        (u4, v4) = fieldset.UV[time + particle.dt, particle.depth, lat3, lon3]
        # print("u:", u1)
        # print("v:", v1, flush=True)
        particle.lon += (u1 + 2*u2 + 2*u3 + u4) / 6. * particle.dt
        particle.lat += (v1 + 2*v2 + 2*v3 + v4) / 6. * particle.dt
        particle.beached = 2

def BeachTesting_2D(particle, fieldset, time):
    if particle.beached == 2 or particle.beached == 3:
        (u, v) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        if math.fabs(u) < 1e-14 and math.fabs(v) < 1e-14:
            particle.beached = 1
        else:
            particle.beached = 0

def UnBeaching(particle, fieldset, time):
    if particle.beached == 1:
        (ub, vb) = fieldset.UVunbeach[time, particle.depth, particle.lat, particle.lon]
        particle.lon += ub * particle.dt
        particle.lat += vb * particle.dt
        # if ub > .1:
        print("OLD:", particle)
        print("NEW:", particle)
        print("dt:", particle.dt)
        print("u:", ub)
        print("v:", vb, flush=True)
        particle.beached = 0

def BrownianMotion2D(particle, fieldset, time):
    """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
    Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
    if particle.beached == 0:
        r = 1 / 3.
        kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
        particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
        kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
        particle.lon += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_zonal / r)
        particle.beached = 3

def periodicBC(particle, fieldset, time):
    if particle.lon < fieldset.halo_west:
        particle.lon += fieldset.halo_east - fieldset.halo_west            #if a particle falls into halo west, its lon is corrected
    elif particle.lon > fieldset.halo_east:
        particle.lon -= fieldset.halo_east - fieldset.halo_west

# def RandomWalkSphere(particle, fieldset, time):
#     """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
#     Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
#
#     # lat_diff_coeff = math.sin(math.fabs(math.radians(particle.lat)))  # latitude
#     # lat_diff_coeff = math.sin(math.fabs(math.pi*particle.lat/180))
#     lat_diff_coeff = 1 # We are assuming this part is already computed by Ocean Parcels
#     df = .01  # Diffussion coefficient
#     r_lat = random.uniform(-1., 1.)
#     r_lon = random.uniform(-1., 1.)
#     particle.lat += df*r_lat*lat_diff_coeff
#     particle.lon += df*r_lon*lat_diff_coeff

# def EricSolution(particle, fieldset, time):
#     """Kernel for simple Brownian particle diffusion in zonal and meridional direction.
#     Assumes that fieldset has fields Kh_zonal and Kh_meridional"""
#     (u, v) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
#     mag = math.sqrt(u*u + v*v)*.05
#     particle.lat += random.uniform(-1., 1.) * mag
#     particle.lon += random.uniform(-1., 1.) * mag

