

def OPT_NN(P,n,m):
    s =[1]*n
    T = 1 + m

    #riga 1
    X = [[[0] * (T+1) for _ in range(m+1)] for _ in range(n)]
    B = [[0] * (m+1) for _ in range(n)]
    #riga 2
    for i in range(n):
        #riga 3
        v_j = P[i].index(1)
        #riga 4
        for tau in range(1,s[i] + 1):
            X[i][v_j][tau] = 1#riga 5

        B[i][v_j] = s[i]#riga 6

    attivi = set(range(n))

    destinazioni = [ max(j+1 for j,arco in enumerate(riga) if arco == 1) for riga in P]

    for t in range(1,T):#riga 7
        droni_da_elaborare = []

        #riga 8
        for i in attivi:
            ultimo_slot = max(B[i])

            if ultimo_slot == t:
                vertice_corrente = B[i].index(ultimo_slot)
                droni_da_elaborare.append((i,vertice_corrente))

        droni_da_elaborare.sort(key=lambda coppia: coppia[1],reverse=True)

        #riga 9
        for i,vertice_corrente in droni_da_elaborare:
            prossimo_vertice = vertice_corrente + 1
            #riga 10
            if vertice_corrente != destinazioni[i] and not any(X[altro][prossimo_vertice][t+1] for altro in range(n)):
                #riga 11
                B[i][prossimo_vertice] = t + 1
                X[i][prossimo_vertice][t+1] = 1

            else:#riga 12
                #riga 13
                B[i][vertice_corrente] = t + 1
                X[i][vertice_corrente][t + 1] = 1
        #riga 14
        for i,_ in droni_da_elaborare:
            if B[i][destinazioni[i]] == t + 1:
                attivi.remove(i)
        #riga 15
    return max((slot for riga in B for slot in riga),default=0)




        
