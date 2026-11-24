
import Funzioni_utili as utile


def REC(P,n,m):
    droni = utile.crea_lista(P)
    #riga1 ordinamento
    droni.sort(key=lambda drone:(drone["last_edge"],drone["first_edge"]),reverse = True)

    #riga2 alpha[0][j] è 0 per gli archi da j da 1 a m
    alpha = [[0] *(m+1) for _ in range(n)]
    #riga 3
    for i in range(1,n):
        drone = droni[i]
        ultimo = drone["last_edge"]

        for j in range(drone["first_edge"],ultimo + 1):
            rimanenti = ultimo - j + 1

            for altro in droni:
                if altro["first_edge"] == j:
                    lunghezza = altro["last_edge"] - j + 1
                    if lunghezza > rimanenti:
                        alpha[i][j] += 1
    #riga 4
    S = [[0] * (m+1) for _ in range(n)]

    # La colonna 0 è fittizia e resta a zero

    #riga 5
    for j in range(1,m + 1):
        occupati = set()
        #riga 6
        for i,drone in enumerate(droni):
            #riga 7
            if drone["first_edge"] <= j <= drone["last_edge"]:
                #dato che ho già salvato il primo e ultimo arco di ogni drone uso direttamente quei valori
                if j == drone["first_edge"]:
                    precedente = 0
                else:
                    precedente = S[i][j - 1]

                t = max(precedente + 1,alpha[i][j] + 1)#riga 8

                while t in occupati:#riga 9
                    t += 1

                S[i][j] = t
                occupati.add(t)



                            
    risultato = [None] * n
    for i, drone in enumerate(droni):
        risultato[drone["id"]] = S[i]
    return risultato

