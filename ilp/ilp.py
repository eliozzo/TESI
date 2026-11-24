

from collections import defaultdict
from itertools import combinations
from numbers import Integral

import pulp as pl


def risolvi_ilp(P, direzioni, s=None, limite_secondi=None):
    #(stato, makespan, S)
    return _risolvi(P, direzioni, s, limite_secondi)


def _risolvi(P, direzioni, s, limite_secondi, vincoli_vertici=None):
    n = len(P)
    m = len(P[0]) if n else 0
    disponibilita = [1] * n if s is None else list(s)

    if len(direzioni) != n or any(d not in (1, -1) for d in direzioni):
        raise ValueError("le direzioni sono 1 e -1")
    if len(disponibilita) != n or any(
        not isinstance(slot, Integral) or slot < 1 for slot in disponibilita
    ):
        raise ValueError("Serve uno slot intero positivo per ogni drone")
    if not n:
        return "Optimal", 0, []

    percorsi = []
    for i, riga in enumerate(P):
        if len(riga) != m or any(valore not in (0, 1) for valore in riga):
            raise ValueError("P deve essere una matrice binaria rettangolare")
        archi = [j for j, presente in enumerate(riga, start=1) if presente]
        if not archi or archi[-1] - archi[0] + 1 != len(archi):
            raise ValueError(f"Il drone {i} deve avere un percorso contiguo non vuoto")
        if direzioni[i] == -1:
            archi.reverse()
        percorsi.append(archi)

    # Dopo l'ultimo rilascio servono solo slot con movimenti o nuovi ingressi
    H = int(max(disponibilita)) + sum(map(len, percorsi)) + n
    modello = pl.LpProblem("DPSP", pl.LpMinimize)
    makespan = pl.LpVariable("C_max", lowBound=1, upBound=H, cat="Integer")
    modello += makespan

    t = {}
    uso_archi = defaultdict(list)

    for i, archi in enumerate(percorsi):
        for j in archi:
            t[i, j] = pl.LpVariable(
                f"t_{i}_{j}", lowBound=1, upBound=H, cat="Integer"
            )
            uso_archi[j].append(i)

        modello += t[i, archi[0]] >= int(disponibilita[i]) + int(vincoli_vertici is not None)
        modello += makespan >= t[i, archi[-1]]
        for precedente, successivo in zip(archi, archi[1:]):
            modello += t[i, successivo] >= t[i, precedente] + 1

    for j, droni in uso_archi.items():
        for i, k in combinations(droni, 2):
            _separa_intervalli(
                modello, (t[i, j], t[i, j]), (t[k, j], t[k, j]),
                H, f"arco_{j}_{i}_{k}",
            )

    if vincoli_vertici is not None:
        vincoli_vertici(modello, percorsi, direzioni, t, H)

    modello.solve(pl.PULP_CBC_CMD(msg=True, timeLimit=limite_secondi,threads=12))

    if modello.sol_status == pl.LpSolutionIntegerFeasible:
        return "Feasible", None, None
    if modello.status != pl.LpStatusOptimal:
        return pl.LpStatus[modello.status], None, None
    if modello.sol_status != pl.LpSolutionOptimal:
        return "Not Solved", None, None

    S = [[slot if vincoli_vertici is not None else 0] + [0] * m for slot in disponibilita]
    for (i, j), variabile in t.items():
        S[i][j] = round(variabile.value())
    return "Optimal", round(makespan.value()), S


def _separa_intervalli(modello, intervallo_i, intervallo_k, H, nome):
    inizio_i, fine_i = intervallo_i
    inizio_k, fine_k = intervallo_k
    i_prima = pl.LpVariable(nome, cat="Binary")
    modello += fine_i + 1 <= inizio_k + H * (1 - i_prima)
    modello += fine_k + 1 <= inizio_i + H * i_prima

