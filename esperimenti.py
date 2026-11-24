

import argparse
import csv
import json
import random
from functools import partial
from importlib import import_module
from numbers import Integral
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

import pulp as pl

from algoritmi_benchmark import carica_algoritmo
from progetto_tesi.ilp.ilp import risolvi_ilp
from progetto_tesi.ilp.ilp_n import risolvi_ilp_n
from progetto_tesi.ilp.ilp_nn import risolvi_ilp_nn
from progetto_tesi.algoritmi.Heap_based import heap_based_unidirezionale
from progetto_tesi.algoritmi.REC import REC

SCENARI = {
    "dpsp_bi": (True, False, risolvi_ilp, {
        "Heap-Based": ("heap", True),
        "Bi-Alg": ("b1", True),
    }),
    "dpsp_n_uni": (False, True, risolvi_ilp_n, {"App-N": ("app_n", False)}),
    "dpsp_n_bi": (
        True, True, risolvi_ilp_n, {"App-N bidirezionale": ("app_n_bi", True)}
    ),
    "dpsp_nn_bi": (True, True, risolvi_ilp_nn, {}),
}

# Questi algoritmi del progetto usano partenze sincronizzate allo slot 1.
ALGORITMI_SINCRONIZZATI = {
    "dpsp_uni": {
        "REC": REC,
        "Heap-Based": heap_based_unidirezionale,
    },
    "dpsp_nn_uni": {"OPT-NN": import_module("algoritmi.OPT-NN").OPT_NN},
}

SCENARI.update({
    "dpsp_uni": (False, False, risolvi_ilp, {}),
    "dpsp_nn_uni": (False, True, risolvi_ilp_nn, {}),
})


def esegui_sincronizzato(algoritmo, P, direzioni, s):
    return algoritmo(P, len(P), len(P[0]))


COLONNE = [
    "scenario", "n", "m", "replica", "seme", "P", "direzioni", "s",
    "algoritmo", "stato_ilp", "ottimo", "makespan", "rho", "secondi",
]


def genera_istanza(n, m, bidirezionale, partenze_distinte, rng):
    direzioni = [rng.choice((1, -1)) if bidirezionale else 1 for _ in range(n)]
    s = [rng.randint(1, 5) for _ in range(n)]
    usati = set()
    P = []

    for verso in direzioni:
        # I vertici hanno indici da 0 a m. Gli archi da 0 a m - 1.
        candidati = range(m) if verso == 1 else range(1, m + 1)
        disponibili = [v for v in candidati if v not in usati]
        partenza = rng.choice(disponibili)

        if partenze_distinte:
            usati.add(partenza)

        limite = m - partenza if verso == 1 else partenza
        lunghezza = rng.randint(1, limite)
        primo = partenza if verso == 1 else partenza - lunghezza
        riga = [0] * m
        riga[primo:primo + lunghezza] = [1] * lunghezza
        P.append(riga)

    return P, direzioni, s


def verifica_piano(P, direzioni, s, S, capacita_vertici, partenza_dallo_slot_uno=False):
    archi_occupati = set()
    intervalli = {}

    for i, riga in enumerate(P):
        archi = [j for j, presente in enumerate(riga, 1) if presente]
        verso = direzioni[i]
        if verso == -1:
            archi.reverse()

        slot = [S[i][j] for j in archi]
        if slot[0] < s[i] + int(capacita_vertici) or any(a >= b for a, b in zip(slot, slot[1:])):
            raise ValueError(f"Tempi non validi per il drone {i}")

        for uso in zip(archi, slot):
            if uso in archi_occupati:
                raise ValueError(f"Conflitto arco-slot {uso}")
            archi_occupati.add(uso)

        if capacita_vertici:
            partenza = archi[0] if verso == 1 else archi[0] + 1
            fine_partenza = slot[0] - 1
            inizio_partenza = 1 if partenza_dallo_slot_uno else fine_partenza
            intervalli.setdefault(partenza, []).append((inizio_partenza, fine_partenza))

            for k, (arco, arrivo) in enumerate(zip(archi, slot)):
                vertice = arco + 1 if verso == 1 else arco
                fine = slot[k + 1] - 1 if k + 1 < len(slot) else arrivo
                intervalli.setdefault(vertice, []).append((arrivo, fine))

    for vertice, occupazioni in intervalli.items():
        ordinate = sorted(occupazioni)
        if any(a[1] >= b[0] for a, b in zip(ordinate, ordinate[1:])):
            raise ValueError(f"Conflitto al vertice {vertice}")

    return max(max(riga[1:]) for riga in S)


def leggi_risultati(percorso):
    risultati = {}
    with percorso.open(encoding="utf-8", newline="") as file:
        lettore = csv.DictReader(file)
        if lettore.fieldnames != COLONNE:
            raise ValueError(f"Intestazione inattesa in {percorso}")
        for riga in lettore:
            # Una riga incompleta può restare dopo un'interruzione.
            if None in riga or any(valore is None for valore in riga.values()):
                continue
            if riga["stato_ilp"] == "GrigliaEsclusa":
                continue
            chiave = tuple(riga[colonna] for colonna in ("scenario", "n", "m", "replica", "seme"))
            gruppo = risultati.setdefault(chiave, {})
            nome = riga["algoritmo"]
            if nome in gruppo:
                raise ValueError(f"Risultato duplicato per {chiave}, {nome}")
            if riga["secondi"] and riga["stato_ilp"]:
                gruppo[nome] = riga
    return risultati


def esegui(args):
    selezione = tuple(args.solo_replica) if args.solo_replica else None
    if selezione:
        scenario, n, m, replica = selezione
        if (
            scenario not in args.scenari
            or int(n) not in args.n
            or int(m) not in args.m
            or not 1 <= int(replica) <= args.repliche
            or (SCENARI[scenario][1] and int(n) > int(m))
        ):
            raise ValueError("La replica selezionata è fuori dalla griglia")
    precedenti = leggi_risultati(args.riprendi_da) if args.riprendi_da else {}
    riutilizzate = 0
    calcolate = 0
    # Carica tutte le funzioni prima di aprire il CSV.
    algoritmi_per_scenario = {}
    for scenario in args.scenari:
        algoritmi_per_scenario[scenario] = {
            nome: carica_algoritmo(getattr(args, opzione), usa_direzioni)
            for nome, (opzione, usa_direzioni) in SCENARI[scenario][3].items()
        }
        algoritmi_per_scenario[scenario].update({
            nome: partial(esegui_sincronizzato, algoritmo)
            for nome, algoritmo in ALGORITMI_SINCRONIZZATI.get(scenario, {}).items()
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLONNE)
        writer.writeheader()

        for scenario in args.scenari:
            bidirezionale, distinti, ilp, _ = SCENARI[scenario]
            algoritmi = algoritmi_per_scenario[scenario]
            for n in args.n:
                for m in args.m:
                    base = dict(scenario=scenario, n=n, m=m, seme=args.seme)
                    print(f"{scenario}: n={n}, m={m}", flush=True)
                    if distinti and n > m:
                        writer.writerow({**base, "stato_ilp": "GrigliaEsclusa"})
                        continue

                    for replica in range(1, args.repliche + 1):
                        rng = random.Random(f"{args.seme}/{scenario}/{n}/{m}/{replica}")
                        P, direzioni, s = genera_istanza(n, m, bidirezionale, distinti, rng)
                        if scenario in ALGORITMI_SINCRONIZZATI:
                            s = [1] * n
                        dati = {
                            **base, "replica": replica, "P": json.dumps(P),
                            "direzioni": json.dumps(direzioni), "s": json.dumps(s),
                        }

                        chiave = tuple(str(dati[colonna]) for colonna in ("scenario", "n", "m", "replica", "seme"))
                        gruppo = precedenti.get(chiave, {})
                        nomi = ("ILP", *algoritmi)
                        selezionata = chiave[:4] == selezione
                        completa = all(nome in gruppo for nome in nomi)
                        if completa and (
                            not selezionata or gruppo["ILP"]["stato_ilp"] == "Optimal"
                        ):
                            righe = [gruppo[nome] for nome in nomi]
                            for riga in righe:
                                if any(json.loads(riga[campo]) != json.loads(dati[campo])
                                       for campo in ("P", "direzioni", "s")):
                                    raise ValueError(f"Istanza nel CSV diversa da quella rigenerata per {chiave}")
                            writer.writerows(righe)
                            file.flush()
                            riutilizzate += 1
                            continue

                        if selezione and not selezionata:
                            continue

                        print(f"[Replica] {scenario}: n={n}, m={m}, replica={replica}/{args.repliche}", flush=True)
                        inizio = perf_counter()
                        stato, ottimo, piano = ilp(P, direzioni, s, limite_secondi=args.timeout)
                        durata_ilp = perf_counter() - inizio
                        if stato == "Optimal":
                            makespan = verifica_piano(
                                P, direzioni, s, piano, distinti,
                                partenza_dallo_slot_uno=scenario.startswith("dpsp_nn_"),
                            )
                            if makespan != ottimo:
                                raise ValueError(f"Makespan del piano ILP diverso dall'ottimo su {dati}")

                        righe = [{
                            **dati, "algoritmo": "ILP", "stato_ilp": stato,
                            "ottimo": ottimo, "makespan": ottimo,
                            "rho": 1 if stato == "Optimal" else None,
                            "secondi": durata_ilp,
                        }]

                        for nome, algoritmo in algoritmi.items():
                            input_algoritmo = [riga[:] for riga in P], direzioni[:], s[:]
                            inizio = perf_counter()
                            risultato = algoritmo(*input_algoritmo)
                            durata = perf_counter() - inizio
                            if isinstance(risultato, Integral):
                                makespan = int(risultato)
                                if makespan <= 0:
                                    raise ValueError(f"{nome}: makespan non positivo")
                            else:
                                makespan = verifica_piano(
                                    P, direzioni, s, risultato, distinti
                                )
                            if stato == "Optimal" and makespan < ottimo:
                                raise ValueError(
                                    f"{nome}: {makespan} < ottimo {ottimo} su {dati}"
                                )
                            righe.append({
                                **dati, "algoritmo": nome, "stato_ilp": stato,
                                "ottimo": ottimo, "makespan": makespan,
                                "rho": makespan / ottimo if stato == "Optimal" else None,
                                "secondi": durata,
                            })
                        writer.writerows(righe)
                        file.flush()
                        calcolate += 1

    print(f"[Fine] Istanze recuperate: {riutilizzate}, calcolate: {calcolate}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", nargs="+", type=int, default=[5, 10, 15])
    parser.add_argument("--m", nargs="+", type=int, default=[10, 20, 30, 40])
    parser.add_argument("--repliche", type=int, default=33)
    parser.add_argument("--seme", type=int, default=42)
    parser.add_argument("--timeout", type=float, default=None, help="Secondi per singolo ILP (predefinito: nessun limite)")
    parser.add_argument("--scenari", nargs="+", choices=SCENARI, default=list(SCENARI))
    parser.add_argument("--heap", default="algoritmi.Heap_based:heap_based_bidirezionale")
    parser.add_argument("--b1", default="algoritmi.B1_alg:B1_alg")
    parser.add_argument("--app-n", default="algoritmi.APP-N:APP_N")
    parser.add_argument("--app-n-bi", default="algoritmi.APP-N:APP_N_bi")
    parser.add_argument("--threads", type=int, default=12, help="Thread richiesti a HiGHS")
    parser.add_argument("--solo-replica", nargs=4, metavar=("SCENARIO", "N", "M", "REPLICA"),
                        help="Calcola solo l'istanza indicata e copia le repliche complete")
    parser.add_argument("--riprendi-da", type=Path, help="CSV da cui recuperare le repliche complete")
    parser.add_argument("--output", type=Path, default=Path("risultati_finali.csv"))
    parser.add_argument("--log-solver", action="store_true", help="Mostra il dettaglio di HiGHS")
    args = parser.parse_args()

    if min(*args.n, *args.m, args.repliche) < 1 or (
        args.timeout is not None and args.timeout <= 0
    ):
        parser.error("n, m, repliche e timeout devono essere positivi")

    if args.threads < 1:
        parser.error("Il numero di thread deve essere positivo")

    try:
        risolutore = pl.HiGHS(
            msg=args.log_solver, timeLimit=args.timeout, threads=args.threads, gapRel=0, gapAbs=0
        )
        if not risolutore.available():
            parser.error("HiGHS non disponibile. Installa highspy con python -m pip install highspy")
        print(f"[Risolutore] HiGHS, thread={args.threads}", flush=True)
        # Riusa la costruzione del modello condivisa senza modificare ilp.py.
        with patch.object(pl, "PULP_CBC_CMD", return_value=risolutore):
            esegui(args)
    except (ImportError, AttributeError, OSError, ValueError) as errore:
        parser.error(str(errore))


if __name__ == "__main__":
    main()
