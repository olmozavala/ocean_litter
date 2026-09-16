"""Parcels particle schema for optional beaching and unbeaching kernels."""

from parcels import FieldSet, JITParticle, ScipyParticle, Variable
import numpy as np

class LitterParticle(JITParticle):
    """Particle with integer beach-state and cumulative unbeaching counters.

    States: 0 at sea; 1 after advection; 2 after diffusion; 3 needs unbeaching;
    4 permanently stopped by the custom movement kernels. beached_count counts
    unbeaching attempts and is never reset on return to sea. Both attributes
    are Parcels Variable descriptors, not ordinary Python class integers.
    """
    beached = Variable('beached', dtype=np.int32, initial=0.)
    beached_count = Variable('beached_count', dtype=np.int32, initial=0.)
