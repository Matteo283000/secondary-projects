def somme_maximale(liste):
    somme_actuelle = 0
    intervalle_somme_actuelle = []
    somme_max = 0
    intervalle_somme_max = []
    
    for nombre in liste:

        somme_actuelle += nombre
        intervalle_somme_actuelle.append(nombre)

        if somme_actuelle > somme_max:
            somme_max, intervalle_somme_max = somme_actuelle, intervalle_somme_actuelle.copy()
        
        if somme_actuelle < 0:
            somme_actuelle = 0
            intervalle_somme_actuelle = []
        
    return f"Liste initiale --> {liste}\nSomme maximale --> {somme_max}\nSon intervalle --> {intervalle_somme_max}"


print(somme_maximale([3, -2, 5, -1, 6, -3, 2]))