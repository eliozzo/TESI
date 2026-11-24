

from importlib import import_module
from inspect import signature


def carica_algoritmo(riferimento, usa_direzioni=True):
    #Carica una funzione modulo:funzione
    modulo, separatore, nome = riferimento.partition(":")
    if not separatore or not modulo or not nome:
        raise ValueError(f"Usa modulo:funzione per {riferimento!r}")

    funzione = getattr(import_module(modulo), nome)

    def argomenti(direzioni, s):
        if usa_direzioni:
            return {"direzioni": direzioni, "s": s}
        return {"s": s}

    try:
        signature(funzione).bind([[1]], 1, 1, **argomenti([1], [1]))
    except TypeError as errore:
        parametri = "s e direzioni" if usa_direzioni else "s"
        raise ValueError(
            f"{riferimento} deve accettare {parametri} come parametri con nome"
        ) from errore

    def esegui(P, direzioni, s):
        return funzione(P, len(P), len(P[0]), **argomenti(direzioni, s))

    return esegui