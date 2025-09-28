import time, random

N = 4                # Tamaño del tablero (4x4)
HUM = 'X'            # Símbolo del humano
AI = 'O'             # Símbolo de la IA

MAX_TIME_SEC = 1.5   # Tiempo máximo por jugada de la IA (segundos)
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

def mostrar_tablero(tablero):
    # Muestra el tablero en consola
    print("\n   " + " ".join(str(i) for i in range(N)))
    for i, fila in enumerate(tablero):
        print(f"{i}  " + " ".join(fila))
    print()

def movimientos_posibles(tablero):
    # Devuelve lista de casillas vacías
    movs = []
    for i in range(N):
        for j in range(N):
            if tablero[i][j] == ' ':
                movs.append((i, j))
    return movs

def tablero_lleno(tablero):
    # Verifica si el tablero está lleno
    for i in range(N):
        for j in range(N):
            if tablero[i][j] == ' ':
                return False
    return True

def hay_ganador(tablero, jugador):
    # Verifica si el jugador ha hecho 4 en línea
    for i in range(N):
        fila_gana = True
        for j in range(N):
            if tablero[i][j] != jugador:
                fila_gana = False
                break
        if fila_gana:
            return True
        col_gana = True
        for j in range(N):
            if tablero[j][i] != jugador:
                col_gana = False
                break
        if col_gana:
            return True
    diag1_gana = True
    for i in range(N):
        if tablero[i][i] != jugador:
            diag1_gana = False
            break
    if diag1_gana:
        return True
    diag2_gana = True
    for i in range(N):
        if tablero[i][N-1-i] != jugador:
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

CENTROS = set()
for i in [1,2]:
    for j in [1,2]:
        CENTROS.add((i,j))
ESQUINAS = set()
ESQUINAS.add((0,0))
ESQUINAS.add((0,N-1))
ESQUINAS.add((N-1,0))
ESQUINAS.add((N-1,N-1))

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

# Heurística de evaluación

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
