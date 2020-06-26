from parcels import FieldSet, JITParticle, ScipyParticle, Variable
import numpy as np

class LitterParticle(JITParticle):
    # beached : 0 sea, 1 after RK, 2 after diffusion, 3 please unbeach, 4 final beached
    beached = Variable('beached', dtype=np.int32, initial=0.)
    beached_count = Variable('beached_count', dtype=np.int32, initial=0.)