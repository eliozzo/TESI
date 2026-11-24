def crea_lista(P):
    droni = []
    for drone_id,row in enumerate(P):
        edges = [j for j,value in enumerate(row,start=1) if value == 1]

        if not edges:
            raise ValueError(f"il drone {drone_id} ha un percorso vuoto")

        droni.append({
            "id":drone_id,
            "first_edge":edges[0],
            "last_edge":edges[-1]
        })
            
        
    return droni