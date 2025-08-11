import numpy as np

#symulacja danych z 3 czujników (wiersze-> czujniki, kolumny-> wartości - pomiary w czasie)
data = np.array([
    [4.5,5.2,5.0,4.8],
    [3.1,3.5,3.6,3.3],
    [7.0,6.9,7.1,7.2]
])

print(f"średnia artymetyczna każdego czujnika: {np.mean(data, axis=1)}")
print(f"odchylenie standardowe: {np.std(data, axis=1)}")

#macierz kowariancji
cov_matrix = np.cov(data)
print(f"macierz kowariancji:\n {cov_matrix}")

#rozwiązanie ukłądu równań  liniowych: y=Ax+b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)
print(f"rozwiązanie układu równań: {x}")
