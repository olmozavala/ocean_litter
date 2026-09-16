"""In-place movement kernels compiled by the legacy OceanParcels JIT.

All kernels receive (particle, fieldset, time) and return None. Time and
particle.dt are in seconds; particle latitude/longitude are in degrees.
Parcels applies the configured spherical field conversions when sampling.
Signatures intentionally remain unannotated. Function documentation uses comments
because Parcels 2.2.0 can emit concatenated docstrings as invalid C on Python 3.10.
See LitterParticle for beach-state meanings.
"""

from parcels import rng as random
import math

def AdvectionRK4Beached(particle, fieldset, time):
    # Advance only state-0 particles with four-stage Runge–Kutta advection.
    #
    # Sample fieldset.UV at four intermediate positions/times, update lon/lat,
    # then mark state 1 so BeachTesting_2D can inspect the destination.
    if particle.beached == 0:
        (u1, v1) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        lon1, lat1 = (particle.lon + u1*.5*particle.dt, particle.lat + v1*.5*particle.dt)

        (u2, v2) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat1, lon1]
        lon2, lat2 = (particle.lon + u2*.5*particle.dt, particle.lat + v2*.5*particle.dt)

        (u3, v3) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat2, lon2]
        lon3, lat3 = (particle.lon + u3*particle.dt, particle.lat + v3*particle.dt)

        (u4, v4) = fieldset.UV[time + particle.dt, particle.depth, lat3, lon3]
        particle.lon += (u1 + 2*u2 + 2*u3 + u4) / 6. * particle.dt
        particle.lat += (v1 + 2*v2 + 2*v3 + v4) / 6. * particle.dt
        particle.beached = 1


def BeachTesting_2D(particle, fieldset, time):
    # Classify particles after advection (1) or diffusion (2).
    #
    # If both sampled UV components have magnitude below 1e-14, set state 3
    # (needs unbeaching); otherwise restore state 0. This is a zero-velocity
    # criterion, not a geometric coastline intersection test.
    if particle.beached == 1 or particle.beached == 2:
        (ubt, vbt) = fieldset.UV[time, particle.depth, particle.lat, particle.lon]
        if math.fabs(ubt) < 1e-14 and math.fabs(vbt) < 1e-14:
            particle.beached = 3
        else:
            particle.beached = 0


def UnBeaching(particle, fieldset, time):
    # Move state-3 particles with unBeachU/unBeachV and count attempts.
    #
    # The threshold is expressed as ten days of positive integration steps, but
    # beached_count is cumulative and never reset: it does not measure continuous
    # time ashore. After the threshold is exceeded, set state 4. Particles remain
    # in the output; the deletion code below is disabled.
    days_to_delete = 10  # Historical name: cumulative attempt threshold, expressed in days.
    # Deletion remains disabled so output keeps a consistent particle count.
    # if particle.beached == 4:
    #     particle.delete()  # This is causing problems because th enumber of particles decreases
    # return

    if particle.beached == 3:
        ub = fieldset.unBeachU[time, particle.depth, particle.lat, particle.lon]
        vb = fieldset.unBeachV[time, particle.depth, particle.lat, particle.lon]
        particle.lon += ub * particle.dt
        particle.lat += vb * particle.dt
        particle.beached = 0
        if particle.beached_count > ((24*days_to_delete)/(particle.dt/3600)):
            particle.beached = 4
        else:
            particle.beached_count += 1



def BrownianMotion2DUnbeaching(particle, fieldset, time):
    # Diffuse state-0 particles, then mark state 2 for beach testing.
    #
    # Requires Kh_zonal and Kh_meridional. Independent uniform draws on [-1, 1]
    # are scaled to variance 2*abs(dt)*Kh in each sampled coordinate direction.
    if particle.beached == 0:
        r = 1 / 3.
        kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
        particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
        kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
        particle.lon += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_zonal / r)
        particle.beached = 2


def BrownianMotion2D(particle, fieldset, time):
    # Apply diffusion regardless of beach state using the two Kh fields.
    #
    # Uniform draws on [-1, 1] are scaled to variance 2*abs(dt)*Kh. This variant
    # can run with a plain JITParticle because it does not access beach variables.
    r = 1 / 3.
    kh_meridional = fieldset.Kh_meridional[time, particle.depth, particle.lat, particle.lon]
    particle.lat += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_meridional / r)
    kh_zonal = fieldset.Kh_zonal[time, particle.depth, particle.lat, particle.lon]
    particle.lon += random.uniform(-1., 1.) * math.sqrt(2 * math.fabs(particle.dt) * kh_zonal / r)


def periodicBC(particle, fieldset, time):
    # Wrap longitude once across fieldset.halo_west/halo_east.
    #
    # Assumes a timestep cannot move a particle by more than one domain width.
    if particle.lon < fieldset.halo_west:
        particle.lon += fieldset.halo_east - fieldset.halo_west            #if a particle falls into halo west, its lon is corrected
    elif particle.lon > fieldset.halo_east:
        particle.lon -= fieldset.halo_east - fieldset.halo_west


def outOfBounds(particle, fieldset, time):
    # Mark a particle as state 4 without deleting it or changing its position.
    #
    # Requires a particle with a beached variable. The legacy runner also
    # registers this callback when using plain JITParticle; that case needs
    # compatibility review before relying on out-of-bounds recovery.
    particle.beached = 4

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
