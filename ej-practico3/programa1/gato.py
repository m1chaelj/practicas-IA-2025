import time, random

N = 4                # Tamaño del tablero (4x4)
HUM = 'X'            # Símbolo del humano
AI = 'O'             # Símbolo de la IA

MAX_TIME_SEC = 4.5   # Tiempo máximo por jugada de la IA (segundos)
MAX_DEPTH = 8        # Profundidad máxima de búsqueda en minimax
INF = 10**9          # Valor infinito para comparación

# Tablero y utilidades

def crear_tablero():
    # Crea un tablero vacío de NxN
    tablero = []
    for i in range(N):
        fila = []
        for j in range(N):
            fila.append(' ')
        tablero.append(fila)
    return tablero

'''
n = 4
i = 0 hasta n-1
    i=0
    j = 0 hasta n-1

    j=0
    fila = []
    fila.append(' ')
    fila = [' ']

    j = 1
    fila.append(' ')
    fila = [' ',' ']
    .
    .
    .
    j = 3
    fila.append('')
    fila = [' ',' ',' ',' ']
    
tablero.append(fila)
tablero = [[' ',' ',' ',' ']]

    i=1
    j = 0 hasta n-1

    j=0
    fila = []
    fila.append(' ')
    fila = [' ']

    j = 1
    fila.append(' ')
    fila = [' ',' ']
    .
    .
    .
    j = 3
    fila.append('')
    fila = [' ',' ',' ',' ']
    fila    
tablero = [[' ',' ',' ',' '], [' ',' ',' ',' ']]
.
.
.
'''

def mostrar_tablero(tablero):
    # Muestra el tablero en consola
    print("\n   " + " ".join(str(i) for i in range(N)))
    for i, fila in enumerate(tablero): # enumerate(), regresa indice y valor.
        print(f"{i}  " + " ".join(fila)) # join() une los elementos de un iterable en una única cadena.
    print()

def movimientos_posibles(tablero):
    # Devuelve lista de casillas vacías
    movs = []
    for i in range(N):
        for j in range(N):
            if tablero[i][j] == ' ': # Si la celda [i][j] esta vacia
                movs.append((i, j))  # Guarda ese valor en movs.
    return movs                      # Regresa en una lista de tuplas los espacios vacios, indicando la fil y columna.
'''
Recordando que crear tablero, returna un tablero que es una lista de listas
tablero = [
    ['X',' ','O',' '],
    [' ','X',' ',' '],
    [' ',' ','O',' '],
    [' ',' ',' ',' '],
]
Con esto devuelve: [(0,1),(0,3),(1,0),(1,2),(1,3),(2,0),(2,1),(2,3),(3,0),(3,1),(3,2),(3,3)]

'''
def tablero_lleno(tablero):
    # Verifica si el tablero está lleno
    for i in range(N):
        for j in range(N):
            if tablero[i][j] == ' ':
                return False        # Si encuentra un espacio el tablero_lleno es falso.
    return True                     # Si recorre cada fila(i) y columna(j), 

def hay_ganador(tablero, jugador):
    # Recibe: tablero que es una lista de listas (matriz N×N) con los símbolos 'X', 'O' o ' '.
    # Recibe: jugador con su carácter, 'X' o 'O', que indica a quién le queremos verificar la victoria
    # Recorre cada fila i
    for i in range(N):
        # ------- Comprueba por filas -------
        # Supone al inicio (fila_gana = True) que toda la fila es del jugador.
        fila_gana = True
        # Recorre las columnas j de esa fila
        for j in range(N):
            # Si encuentra una celda distinta, pone fila_gana = False y hace break
            if tablero[i][j] != jugador:
                fila_gana = False
                break
        if fila_gana:
            return True
        
        # ------- Comprueba por columnas -------
        col_gana = True
        for j in range(N):
            if tablero[j][i] != jugador:
                col_gana = False
                break
        if col_gana:
            return True
        
    '''
    columnas→ 0    1    2    3
    filas
        0   (0,0)(0,1)(0,2)(0,3)
        1   (1,0)(1,1)(1,2)(1,3)
        2   (2,0)(2,1)(2,2)(2,3)
        3   (3,0)(3,1)(3,2)(3,3)
    
        Diagonal principal: De esquina superior izquierda (0,0) hasta la esquina inferior derecha (3,3).
                            En cada casilla, fila = columna → (i, i)
        Diagonal secundaria: De esquina superior derecha (0,3) hasta la esquina inferior izquierda (3,0)
    '''
    # ------- Comprueba por diagonal (de arriba-izquierda a abajo-derecha): posiciones (0,0), (1,1), (2,2), (3,3) -------
    diag1_gana = True
    for i in range(N):
        if tablero[i][i] != jugador:
            diag1_gana = False
            break
    if diag1_gana:
        return True
    
    # ------- Comprueba por diagonal (de arriba-derecha a abajo-izquierda): posiciones (0,N-1), (1,N-2), (2,N-3), (3,0) -------
    diag2_gana = True
    for i in range(N):
        # La fila (i) va subiendo: 0, 1, 2, 3.
        # La columna va bajando: 3, 2, 1, 0.
        if tablero[i][N-1-i] != jugador: # La última columna siempre es N-1
            diag2_gana = False
            break
    if diag2_gana:
        return True
    return False

# Precalcular las 10 líneas ganadoras en 4x4
LINEAS = []
for i in range(N):
    fila = []
    for j in range(N):
        fila.append((i, j))
    LINEAS.append(fila)  # filas
    columna = []
    for j in range(N):
        columna.append((j, i))
    LINEAS.append(columna)  # columnas
diag_principal = []
for i in range(N):
    diag_principal.append((i, i))
LINEAS.append(diag_principal)      # diagonal principal
diag_secundaria = []
for i in range(N):
    diag_secundaria.append((i, N-1-i))
LINEAS.append(diag_secundaria)     # diagonal secundaria

'''

Al pre-calcular las 10 líneas ganadoras, la función evaluar no tiene 
que calcular las coordenadas en cada llamada. Simplemente itera sobre 
la lista fija de 10 patrones.
LINEAS = [
    # Filas
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(1, 0), (1, 1), (1, 2), (1, 3)],
    [(2, 0), (2, 1), (2, 2), (2, 3)],
    [(3, 0), (3, 1), (3, 2), (3, 3)],

    # Columnas
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 1), (1, 1), (2, 1), (3, 1)],
    [(0, 2), (1, 2), (2, 2), (3, 2)],
    [(0, 3), (1, 3), (2, 3), (3, 3)],

    # Diagonales
    [(0, 0), (1, 1), (2, 2), (3, 3)],
    [(0, 3), (1, 2), (2, 1), (3, 0)]
]
'''
CENTROS = set() # Devuelve al final CENTROS={(1,1),(1,2),(2,1),(2,2)}
for i in [1,2]:
    for j in [1,2]:
        CENTROS.add((i,j))

ESQUINAS = set() # Devuelve al final ESQUINAS={(0,0),(0,3),(3,0),(3,3)}
ESQUINAS.add((0,0))
ESQUINAS.add((0,N-1))
ESQUINAS.add((N-1,0))
ESQUINAS.add((N-1,N-1))

'''
Definir estas zonas como conjuntos (set) hace que la verificación de 
si un movimiento es central o de esquina sea casi instantánea (O(1))
'''

def ordenar_movimientos(movs):
    # Ordena los movimientos priorizando centro y esquinas
    def key(m):
        if m in CENTROS: return 0
        if m in ESQUINAS: return 1
        # Bonus por estar cerca del centro
        i, j = m
        return 2 + abs(i-1.5) + abs(j-1.5)
    movs_ordenados = sorted(movs, key=key)
    return movs_ordenados


# Ponderaciones según cantidad de fichas propias en una línea abierta
PESO = {0:0, 1:1, 2:4, 3:9}

def evaluar(tablero):
    # Evalúa el tablero para posiciones no terminales
    puntaje = 0
    for linea in LINEAS:
        xs = 0
        os = 0
        for pos in linea:
            i, j = pos
            if tablero[i][j] == AI:
                os += 1
            elif tablero[i][j] == HUM:
                xs += 1
        if xs and os:
            continue  # Línea bloqueada, no suma
        if os:
            puntaje += PESO[os]
        elif xs:
            puntaje -= PESO[xs]
    return puntaje

# Transposición (memoización)

def clave_estado(tablero, turno_max, profundidad):
    # Genera una clave única para el estado actual del tablero
    filas = []
    for i in range(N):
        fila = ""
        for j in range(N):
            fila += tablero[i][j]
        filas.append(fila)
    clave = "|".join(filas) + f"|T{1 if turno_max else 0}|D{profundidad}"
    return clave

TT = {}  # Diccionario de transposición para guardar valores ya calculados

# Minimax con alfa-beta, tope de tiempo y memorización 

def minimax(tablero, profundidad, turno_max, alpha, beta, t0, tlim):
    # Algoritmo minimax con poda alfa-beta y límite de tiempo
    if time.time() - t0 > tlim:
        raise TimeoutError

    if hay_ganador(tablero, AI):
        return 100000 - profundidad
    if hay_ganador(tablero, HUM):
        return -100000 + profundidad
    if tablero_lleno(tablero) or profundidad == 0:
        return evaluar(tablero)

    clave = clave_estado(tablero, turno_max, profundidad)
    if clave in TT:
        return TT[clave]

    movs = ordenar_movimientos(movimientos_posibles(tablero))

    if turno_max:
        mejor = -INF
        # Busca jugadas ganadoras inmediatas
        for mov in movs:
            i, j = mov
            tablero[i][j] = AI
            if hay_ganador(tablero, AI):
                tablero[i][j] = ' '
                TT[clave] = 100000 - (MAX_DEPTH - profundidad)
                return TT[clave]
            tablero[i][j] = ' '
        for mov in movs:
            i, j = mov
            tablero[i][j] = AI
            try:
                valor = minimax(tablero, profundidad-1, False, alpha, beta, t0, tlim)
            finally:
                tablero[i][j] = ' '
            if valor > mejor:
                mejor = valor
            if mejor > alpha:
                alpha = mejor
            if beta <= alpha:
                break
        TT[clave] = mejor
        return mejor
    else:
        peor = INF
        # Busca bloqueos inmediatos si el humano puede ganar
        for mov in movs:
            i, j = mov
            tablero[i][j] = HUM
            if hay_ganador(tablero, HUM):
                tablero[i][j] = ' '
                TT[clave] = -100000 + (MAX_DEPTH - profundidad)
                return TT[clave]
            tablero[i][j] = ' '
        for mov in movs:
            i, j = mov
            tablero[i][j] = HUM
            try:
                valor = minimax(tablero, profundidad-1, True, alpha, beta, t0, tlim)
            finally:
                tablero[i][j] = ' '
            if valor < peor:
                peor = valor
            if peor < beta:
                beta = peor
            if beta <= alpha:
                break
        TT[clave] = peor
        return peor

def mejor_movimiento(tablero):
    # Busca el mejor movimiento para la IA usando minimax con iterative deepening
    t0 = time.time()
    limite = MAX_TIME_SEC
    movs = ordenar_movimientos(movimientos_posibles(tablero))
    if not movs:
        return None

    mejor_mov = random.choice(movs)
    mejor_val = -INF

    # Búsqueda iterativa por profundidad creciente
    for d in range(1, MAX_DEPTH + 1):
        if time.time() - t0 > limite:
            break
        TT.clear()
        mov_local = mejor_mov
        val_local = -INF
        for mov in movs:
            i, j = mov
            if time.time() - t0 > limite:
                break
            tablero[i][j] = AI
            try:
                valor = minimax(tablero, d-1, False, -INF, INF, t0, limite)
            except TimeoutError:
                tablero[i][j] = ' '
                break
            tablero[i][j] = ' '
            if valor > val_local:
                val_local = valor
                mov_local = (i, j)
        # Si terminamos bien esta profundidad, actualizamos mejor global
        if time.time() - t0 <= limite and val_local > -INF:
            mejor_val = val_local
            mejor_mov = mov_local
        else:
            break

    return mejor_mov

# Entrada/Salida

def leer_par_coordenadas():
    # Lee dos números de la entrada como coordenadas
    entrada = input().strip().replace(',', ' ').split()
    if len(entrada) != 2:
        raise ValueError("Escribe dos números: fila y columna (0-3).")
    fila = int(entrada[0])
    col = int(entrada[1])
    if not (0 <= fila < N and 0 <= col < N):
        raise ValueError("Fuera de rango. Usa 0-3.")
    return fila, col

def jugar():
    # Bucle principal del juego
    print("Gato con un tablero 4x4")
    print("Tú eres 'X', IA es 'O'.")
    tablero = crear_tablero()
    mostrar_tablero(tablero)
    turno = HUM  # El humano siempre empieza

    while True:
        if turno == HUM:
            print("Tu turno (X). Ingresa fila y columna.")
            try:
                fila, col = leer_par_coordenadas()
            except Exception as e:
                print(f"Entrada inválida: {e}")
                continue
            if tablero[fila][col] != ' ':
                print("Casilla ya ocupada.")
                continue
            tablero[fila][col] = HUM
            mostrar_tablero(tablero)
            if hay_ganador(tablero, HUM):
                print("¡Ganaste!")
                break
            if tablero_lleno(tablero):
                print("Empate.")
                break
            turno = AI
        else:
            print("Turno de la IA (O)...")
            mov = mejor_movimiento(tablero)
            if mov is None:
                print("Empate.")
                break
            i, j = mov
            tablero[i][j] = AI
            mostrar_tablero(tablero)
            if hay_ganador(tablero, AI):
                print("La IA gana.")
                break
            if tablero_lleno(tablero):
                print("Empate.")
                break
            turno = HUM

jugar()
