import Funzioni_utili as utile

#s lista slot disponibilità droni
# es s = [1,2,3] il drone 0 è disponibile dallo slot 1 etc
def APP_N(P,n,m,s):
    t = max(s)#riga 1

    droni = utile.crea_lista(P)
    posizioni = [drone["first_edge"] for drone in droni]
    destinazioni = [drone["last_edge"] + 1 for drone in droni]

    #riga 2
    ordine = sorted(range(n),key=lambda i:posizioni[i],reverse=True)

    while any(posizioni[i] < destinazioni[i] for i in range(n)):
        #riga 3

        for i in ordine:
            if posizioni[i] < destinazioni[i]:
                posizioni[i] += 1

        t += 1
    return t





def APP_N_bi(P,n,m,s,direzioni):
    if len(direzioni) != n or any (d not in (1,-1) for d in direzioni):
            raise ValueError("le direzioni sono 1 e -1")
    D_LR = [i for i in range(n) if direzioni[i] == 1]
    D_RL = [i for i in range(n) if direzioni[i] == -1]

    T_LR = 0

    if D_LR:
        P_LR = [P[i] for i in D_LR]
        s_LR = [s[i] for i in D_LR]
        T_LR = APP_N(P_LR,len(D_LR),m,s_LR)

    if not D_RL:
        return T_LR

    P_RL = [P[i][::-1] for i in D_RL]#inverto le colonne di P cosi gli archi hanno indici crescenti
    s_RL = [s[i] + T_LR for i in D_RL]

    return APP_N(P_RL,len(D_RL),m,s_RL)