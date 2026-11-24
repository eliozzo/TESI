"""Traccia la media di rho per cella della griglia, usando solo ottimi certificati."""

import argparse
import csv
from collections import defaultdict
from math import ceil, nan
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def grafici(percorso_csv, output):
    celle = defaultdict(lambda: defaultdict(list))
    with percorso_csv.open(encoding="utf-8", newline="") as file:
        for riga in csv.DictReader(file):
            if riga["rho"]:
                chiave = int(riga["n"]), int(riga["m"]), riga["algoritmo"]
                celle[riga["scenario"]][chiave].append(float(riga["rho"]))

    output.mkdir(parents=True, exist_ok=True)
    for scenario, risultati in celle.items():
        algoritmi = sorted({nome for _, _, nome in risultati} - {"ILP"})
        if not algoritmi:
            continue
        for asse_x in (0, 1):
            salva_figura(scenario, risultati, algoritmi, asse_x, output)


def salva_figura(scenario, risultati, algoritmi, asse_x, output):
    nomi_assi = ("n", "m")
    asse_fisso = 1 - asse_x
    punti = sorted({chiave[asse_x] for chiave in risultati})
    pannelli = sorted({chiave[asse_fisso] for chiave in risultati})

    fig, assi = plt.subplots(
        ceil(len(pannelli) / 2), 2, squeeze=False, sharey=True,
        figsize=(10, 3.6 * ceil(len(pannelli) / 2)),
    )

    for ax, fisso in zip(assi.flat, pannelli):
        for nome in algoritmi:
            medie = []
            conteggi = []
            for punto in punti:
                n, m = (punto, fisso) if asse_x == 0 else (fisso, punto)
                campioni = risultati.get((n, m, nome), [])
                medie.append(mean(campioni) if campioni else nan)
                conteggi.append(len(campioni))

            ax.plot(punti, medie, marker="o", label=nome)
            if nome == algoritmi[0]:
                ax.set_xticks(punti, [
                    f"{punto}\n({count})" for punto, count in zip(punti, conteggi)
                ])

        ax.axhline(1, color="0.5", linestyle="--", label="Ottimo ILP")
        ax.set(title=f"{nomi_assi[asse_fisso]} = {fisso}",
               xlabel=nomi_assi[asse_x], ylabel="ρ medio")
        ax.grid(axis="y", alpha=0.25)
        ax.legend()

    for ax in list(assi.flat)[len(pannelli):]:
        ax.set_visible(False)

    fig.suptitle(f"{scenario.upper()}  |  Tra parentesi: istanze con ottimo certificato")
    fig.tight_layout()
    fig.savefig(output / f"{scenario}_per_{nomi_assi[asse_x]}.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output", type=Path, default=Path("grafici"))
    args = parser.parse_args()
    grafici(args.csv, args.output)
