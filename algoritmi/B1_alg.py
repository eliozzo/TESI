import progetto_tesi.algoritmi.Heap_based as Heap_based 
#LR -> 1
#RL -> -1
def B1_alg(P,n,m,direzioni,s=None):
    s = [1] * n if s is None else s
    if len(s) != n:
        raise ValueError("Serve uno slot per ogni drone")
    
    if len(direzioni) != n or any(d not in (1,-1) for d in direzioni):
        raise ValueError("le direzioni sono 1 e -1")

    #riga 1 divido in RL e LR
    D_LR = []
    D_RL = []

    for i,direzione in enumerate(direzioni):
        if direzione == 1:
            D_LR.append(i)
        else:# == -1
            D_RL.append(i)

    #riga 2
    P_LR = [P[i] for i in D_LR]#creo la p left->right
    n_LR = len(P_LR)#n LR

    S_LR = Heap_based.heap_based_unidirezionale(P_LR,n_LR,m,s=[s[i] for i in D_LR])

    #riga 3

    T_LR = max((S_LR[i][j] for i in range(n_LR) for j in range(m+1)),default=0,)#default 0 nel caso S_LR sia vuoto,perche max poi non avrebbe cosa confrontare e da errore

    #riga 4
    s_RL = [s[i] + T_LR for i in D_RL]
    #riga 5
    P_RL = [P[i][::-1] for i in D_RL]
    n_RL = len(P_RL)

    S_RL = Heap_based.heap_based_unidirezionale(P_RL,n_RL,m,s=s_RL)

    S_RL = [[riga[0]] + riga[1:][::-1] for riga in S_RL]
    #riga 6
    S = [[0] * (m+1) for _ in range(n)]

    for indice_locale,id_originale in enumerate(D_LR):
        S[id_originale] = S_LR[indice_locale]

    for indice_locale,id_originale in enumerate(D_RL):
        S[id_originale] = S_RL[indice_locale]

    
    
    return S