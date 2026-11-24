from collections import defaultdict
from numbers import Integral
import heapq
import Funzioni_utili as utile



def heap_based_unidirezionale(P, n, m,slot_iniziale=1, s=None):
    droni = utile.crea_lista(P)

   
    S = [[0] * (m + 1) for _ in range(n)] #riga 1
    H = [[] for _ in range(m + 1)] #riga 2
    s = [slot_iniziale] * n if s is None else s
    if len(s) != n or any(not isinstance(slot, Integral) or slot < 1 for slot in s):
        raise ValueError("Serve uno slot intero positivo per ogni drone")
    partenze = defaultdict(list)
    t = min(s, default=1)

    for drone in droni:#riga 4
        i = drone["id"]
        primo = drone["first_edge"]
        ultimo = drone["last_edge"]
        rimanenti = ultimo - primo + 1

        partenze[s[i]].append((primo, (-rimanenti, s[i] - 1, i)))

    #rig 5
    while partenze or any(H):
        for arco, elemento in partenze.pop(t, []):
            heapq.heappush(H[arco], elemento)

        #riga 6
        for j in range(m, 0, -1):
            if H[j]:#riga 7
                priorita, slot_precedente, i = heapq.heappop(H[j])#riga 8
                S[i][j] = t

                #riga 9
                if j < droni[i]["last_edge"]:
                    nuova_priorita = priorita + 1
                    heapq.heappush(H[j + 1], (nuova_priorita, t, i))

        t += 1#riga 10

    return S

def heap_based_bidirezionale(P, n, m, direzioni, s=None):
    if len(direzioni) != n:
        raise ValueError("Serve una direzione per ogni drone")

    if any(direzione not in (1, -1) for direzione in direzioni):
        raise ValueError("le direzioni sono 1 e -1")

    droni = utile.crea_lista(P)

    S = [[0] * (m + 1) for _ in range(n)]


   
    H = [[] for _ in range(m + 1)]
    s = [1] * n if s is None else s
    if len(s) != n or any(not isinstance(slot, Integral) or slot < 1 for slot in s):
        raise ValueError("Serve uno slot intero positivo per ogni drone")
    partenze = defaultdict(list)
    t = min(s, default=1)

    for drone in droni:
        i = drone["id"]
        minimo = drone["first_edge"]
        massimo = drone["last_edge"]
        rimanenti = massimo - minimo + 1

        if direzioni[i] == 1:
            partenza = minimo
        else:
            partenza = massimo

        partenze[s[i]].append((partenza, (-rimanenti, s[i] - 1, i)))

    while partenze or any(H):
        for arco, elemento in partenze.pop(t, []):
            heapq.heappush(H[arco], elemento)
        inserimenti_successivi = []

        for j in range(m, 0, -1):
            if H[j]:
                priorita, slot_precedente, i = heapq.heappop(H[j])
                S[i][j] = t

                rimanenti_dopo = -priorita - 1

                if rimanenti_dopo > 0:
                    prossimo_arco = j + direzioni[i]
                    elemento = (-rimanenti_dopo, t, i)

                    inserimenti_successivi.append(
                        (prossimo_arco, elemento)
                    )

        
        for arco, elemento in inserimenti_successivi:
            heapq.heappush(H[arco], elemento)

        t += 1

    return S