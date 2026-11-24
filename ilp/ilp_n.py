
from collections import defaultdict
from itertools import combinations

from progetto_tesi.ilp.ilp import _risolvi, _separa_intervalli


def risolvi_ilp_n(P, direzioni, s=None, limite_secondi=None):
    """Restituisce (stato, makespan, S)."""
    return _risolvi(P, direzioni, s, limite_secondi, _vincoli_vertici)


def _vincoli_vertici(
    modello, percorsi, direzioni, t, H, occupazione_dallo_slot_uno=False
):
    uso_vertici = defaultdict(list)
    partenze = set()

    for i, archi in enumerate(percorsi):
        primo, ultimo = archi[0], archi[-1]
        verso = direzioni[i]
        partenza = primo if verso == 1 else primo + 1
        if partenza in partenze:
            raise ValueError("I droni devono partire da vertici distinti")
        partenze.add(partenza)

        fine_partenza = t[i, primo] - 1
        inizio_partenza = 1 if occupazione_dallo_slot_uno else fine_partenza
        uso_vertici[partenza].append((i, (inizio_partenza, fine_partenza)))

        for entrata, uscita in zip(archi, archi[1:]):
            vertice = entrata + 1 if verso == 1 else entrata
            uso_vertici[vertice].append((i, (t[i, entrata], t[i, uscita] - 1)))

        destinazione = ultimo + 1 if verso == 1 else ultimo
        arrivo = t[i, ultimo]
        uso_vertici[destinazione].append((i, (arrivo, arrivo)))

    for vertice, occupazioni in uso_vertici.items():
        for (i, intervallo_i), (k, intervallo_k) in combinations(occupazioni, 2):
            _separa_intervalli(
                modello, intervallo_i, intervallo_k, H, f"vertice_{vertice}_{i}_{k}"
            )

