

from functools import partial

from ilp import _risolvi
from ilp_n import _vincoli_vertici


def risolvi_ilp_nn(P, direzioni, s=None, limite_secondi=None):
    #Restituisce (stato, makespan, S)
    vincoli_nn = partial(_vincoli_vertici, occupazione_dallo_slot_uno=True)
    return _risolvi(P, direzioni, s, limite_secondi, vincoli_nn)