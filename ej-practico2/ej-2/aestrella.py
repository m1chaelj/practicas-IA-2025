import heapq
import time
import re

# ------------------------------ Configuración base ------------------------------
TAMANO_TABLERO = 4
ESTADO_OBJETIVO = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS = ('arriba', 'abajo', 'izquierda', 'derecha')
# Si se dibuja el cuadrado de 4x4, y se realiza las operaciones abajo y arriba, se llega justamente a la posicion buscada.
DESPLAZAMIENTOS = {'arriba': -TAMANO_TABLERO, 'abajo': TAMANO_TABLERO, 'izquierda': -1, 'derecha': 1}
POSICION_OBJETIVO = {v: (i // TAMANO_TABLERO, i % TAMANO_TABLERO) for i, v in enumerate(ESTADO_OBJETIVO)}

"""
Ejemplo posicion objetivo.
15
v : fila, columna
i = 14, v = 15
15 : (14//4, 14%4)
15 : (fila: 3, columna: 2)
15 : (3,2)
"""
"""
    Col0   Col1    Col2    Col3
    (1,     2,      3,      4,     Fila0
    5,      6,      7,      8,     Fila1
    9,      10,     11,     12,    Fila2
    13,     14,     15,     0)     Fila3

"""
# Visualización paso a paso
LIMPIAR_PANTALLA = False   # True => limpia pantalla en cada paso
PAUSA_SEGUNDOS = 0.35      # pausa entre pasos
MOSTRAR_METRICAS = True    # muestra g, h, f en cada estado

# Límite operativo para A*
LIMITE_EXPANSIONES = 1_000_000

# ------------------------------ Utilidades de tablero ------------------------------
def indice_a_fila_columna(indice):
    return divmod(indice, TAMANO_TABLERO) # divmod(indice, 4) -> regresa dos valores divmod(a,b) eso es igual a (a//b,a%b)
                                        # return (indice//TAMANO_TABLERO,indice%TAMANO_TABLERO) 
                                        # en realidad return (fila, columna)

def fila_columna_a_indice(fila, columna): # recibe (fila, columna)
                                            # ejemplo (2,2) -> 2 * 4 + 2 = 10
                                            # indice = 10
    return fila * TAMANO_TABLERO + columna

def movimiento_valido(indice_cero, movimiento):
    fila, columna = indice_a_fila_columna(indice_cero)
    if movimiento == 'arriba':    return fila > 0
    if movimiento == 'abajo':     return fila < TAMANO_TABLERO - 1
    if movimiento == 'izquierda': return columna > 0
    if movimiento == 'derecha':   return columna < TAMANO_TABLERO - 1
    return False

"""
indice_cero = 10 
emplea indice_a_fila_columna(indice_cero) -> indice_a_fila_columna(10) 
indice_a_fila_columna(10) -> return (10//4,10%4) -> return(2,2)
fila = 2, columna = 2
VALIDA:
arriba    ->  2 > 0    -> TRUE
abajo     ->  2 < 4-1  -> TRUE
izquierda ->  2 > 0    -> TRUE
derecha   ->  2 < 4-1  -> TRUE


"""
def aplicar_movimiento(estado, movimiento):
    """Devuelve el nuevo estado al mover el 0; None si no es válido."""
    indice_cero = estado.index(0)
    if not movimiento_valido(indice_cero, movimiento):
        return None
    delta = DESPLAZAMIENTOS[movimiento]
    # Evitar cruzar de fila en izquierda/derecha
    if movimiento in ('izquierda', 'derecha'):
        f0, _ = indice_a_fila_columna(indice_cero)
        f1, _ = indice_a_fila_columna(indice_cero + delta)
        if f0 != f1:
            return None
    lista = list(estado)
    j = indice_cero + delta
    lista[indice_cero], lista[j] = lista[j], lista[indice_cero]
    return tuple(lista)

def imprimir_tablero(estado):
    for fila in range(TAMANO_TABLERO):
        segmento = estado[fila * TAMANO_TABLERO:(fila + 1) * TAMANO_TABLERO]
        print(' '.join(f'{x:2d}' if x != 0 else '  .' for x in segmento))

def imprimir_tablero_resaltado(estado, indice_resaltado=None):
    for fila in range(TAMANO_TABLERO):
        celdas = []
        for columna in range(TAMANO_TABLERO):
            idx = fila_columna_a_indice(fila, columna)
            val = estado[idx]
            celda = f'{val:2d}' if val != 0 else '  .'
            if indice_resaltado is not None and idx == indice_resaltado:
                celda = f'[{celda}]'
            celdas.append(celda)
        print(' '.join(celdas))

def limpiar_consola():
    import os, sys
    os.system('cls' if sys.platform.startswith('win') else 'clear')

# ------------------------------ Solvencia (4x4) ------------------------------
def calcular_inversiones_y_R(estado):
    plano = [x for x in estado if x != 0]
    inversiones = sum(1 for i in range(len(plano)) for j in range(i+1, len(plano)) if plano[i] > plano[j])
    idx0 = estado.index(0)
    fila_desde_arriba = idx0 // TAMANO_TABLERO
    R = TAMANO_TABLERO - fila_desde_arriba  # 1..4
    return inversiones, R

def es_resoluble_4x4(estado):
    if tuple(sorted(estado)) != tuple(range(TAMANO_TABLERO * TAMANO_TABLERO)):
        return False
    I, R = calcular_inversiones_y_R(estado)
    return (I + R) % 2 == 1

def explicar_paridad(estado):
    I, R = calcular_inversiones_y_R(estado)
    plano = [x for x in estado if x != 0]
    print("\n[Chequeo de solvencia 4x4]")
    print("Secuencia (sin 0):", plano)
    print(f"Inversiones (I) = {I}")
    print(f"Fila del 0 desde abajo (R) = {R}")
    print(f"(I + R) = {I + R}  →  {'IMPAR (RESOLUBLE)' if (I+R)%2==1 else 'PAR (NO RESOLUBLE)'}")

# ------------------------------ Heurística: Manhattan + Conflicto Lineal ------------------------------
def distancia_manhattan(estado):
    total = 0
    for i, v in enumerate(estado):
        if v == 0:
            continue
        f, c = indice_a_fila_columna(i)
        fo, co = POSICION_OBJETIVO[v]
        total += abs(f - fo) + abs(c - co)
    return total

def conflicto_lineal(estado):
    conf = 0
    # Filas
    for f in range(TAMANO_TABLERO):
        cols_obj = []
        for c in range(TAMANO_TABLERO):
            v = estado[f*TAMANO_TABLERO + c]
            if v != 0 and POSICION_OBJETIVO[v][0] == f:
                cols_obj.append(POSICION_OBJETIVO[v][1])
        for i in range(len(cols_obj)):
            for j in range(i+1, len(cols_obj)):
                if cols_obj[i] > cols_obj[j]:
                    conf += 1
    # Columnas
    for c in range(TAMANO_TABLERO):
        filas_obj = []
        for f in range(TAMANO_TABLERO):
            v = estado[f*TAMANO_TABLERO + c]
            if v != 0 and POSICION_OBJETIVO[v][1] == c:
                filas_obj.append(POSICION_OBJETIVO[v][0])
        for i in range(len(filas_obj)):
            for j in range(i+1, len(filas_obj)):
                if filas_obj[i] > filas_obj[j]:
                    conf += 1
    return 2 * conf

def heuristica_mc(estado):
    return distancia_manhattan(estado) + conflicto_lineal(estado)

# ------------------------------ A* (h = Manhattan + Conflicto Lineal) ------------------------------
def a_estrella(estado_inicial, imprimir_progreso=True, frecuencia_progreso=10000, limite_expansiones=LIMITE_EXPANSIONES):
    """Devuelve (lista_de_movimientos, nodos_expandidos) o (None, nodos_expandidos) si se alcanza el límite."""
    h = heuristica_mc
    if estado_inicial == ESTADO_OBJETIVO:
        return [], 0

    costo_desde_inicio = {estado_inicial: 0}  # g
    predecesor = {estado_inicial: (None, None)}  # estado -> (anterior, movimiento)
    cerrados = set()
    abiertos_heap = []  # (f, h, tie, estado)
    contador_orden = 0
    expandidos = 0

    f0 = h(estado_inicial)
    heapq.heappush(abiertos_heap, (f0, f0, contador_orden, estado_inicial))

    while abiertos_heap:
        f_actual, h_actual, _, estado = heapq.heappop(abiertos_heap)
        if estado in cerrados:
            continue

        if estado == ESTADO_OBJETIVO:
            # reconstruir camino
            camino = []
            cur = estado
            while predecesor[cur][0] is not None:
                ant, mov = predecesor[cur]
                camino.append(mov or "")
                cur = ant or ESTADO_OBJETIVO
            camino.reverse()
            return camino, expandidos

        cerrados.add(estado)
        expandidos += 1

        if imprimir_progreso and expandidos % frecuencia_progreso == 0:
            print(f"[A*] Expandidos: {expandidos:,}  f={f_actual}  h={h_actual}  g={costo_desde_inicio[estado]}")

        if expandidos >= limite_expansiones:
            return None, expandidos

        g_s = costo_desde_inicio[estado]
        for mov in LISTA_MOVIMIENTOS:  # orden determinista
            vecino = aplicar_movimiento(estado, mov)
            if vecino is None:
                continue
            tent = g_s + 1
            if vecino in cerrados and tent >= costo_desde_inicio.get(vecino, float('inf')):
                continue
            if tent < costo_desde_inicio.get(vecino, float('inf')):
                costo_desde_inicio[vecino] = tent
                predecesor[vecino] = (estado, mov)
                hv = h(vecino)
                fv = tent + hv
                contador_orden += 1
                heapq.heappush(abiertos_heap, (fv, hv, contador_orden, vecino))
    return None, expandidos

# ------------------------------ Parser estricto e input interactivo ------------------------------
def parsear_tablero_estricto(texto):
    """Devuelve tupla de 16 ints (0..15) si es válido; si no, imprime error y devuelve None."""
    tokens = re.split(r"[,\s]+", texto.strip())
    tokens = [t for t in tokens if t != ""]
    if len(tokens) != TAMANO_TABLERO * TAMANO_TABLERO:
        print(f"\nEntrada inválida: se leyeron {len(tokens)} valores, se requieren {TAMANO_TABLERO*TAMANO_TABLERO}.")
        return None

    valores = []
    for t in tokens:
        try:
            valores.append(int(t))
        except ValueError:
            print(f"\nEntrada inválida: '{t}' no es un número entero.")
            return None

    fuera_de_rango = [x for x in valores if not (0 <= x <= 15)]
    if fuera_de_rango:
        print("Valores fuera de rango [0..15]:", sorted(set(fuera_de_rango)))
        return None

    esperados = set(range(16))
    s = set(valores)
    duplicados = sorted([x for x in s if valores.count(x) > 1])
    faltantes = sorted(list(esperados - s))
    if duplicados or faltantes:
        if duplicados:
            print("Duplicados:", duplicados)
        if faltantes:
            print("Faltan:", faltantes)
        return None

    return tuple(valores)

def pedir_tablero_interactivo():
    """Pide el tablero en una o varias líneas. Repite hasta que sea válido o Enter inmediato para cancelar."""
    print("Pega 16 números (0..15), 0 es el hueco. Puedes usar espacios o comas.")
    print("Ejemplo: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0")
    print("Deja una línea vacía para validar. Línea vacía inmediata = cancelar.\n")
    while True:
        lineas = []
        while True:
            linea = input()
            if not linea.strip():
                break
            lineas.append(linea)
        if not lineas:
            return None
        tablero = parsear_tablero_estricto("\n".join(lineas))
        if tablero is not None:
            return tablero
        print("\nEntrada inválida. Intenta de nuevo (o presiona Enter inmediatamente para cancelar).\n")

# ------------------------------ Reproducción paso a paso ------------------------------
def reproducir_movimientos(estado_inicial, lista_movimientos, pausa_segundos=PAUSA_SEGUNDOS,
                        limpiar_pantalla=LIMPIAR_PANTALLA, mostrar_metricas=MOSTRAR_METRICAS):
    estado = estado_inicial
    print("\nEstado inicial:")
    imprimir_tablero(estado)
    if mostrar_metricas:
        h0 = heuristica_mc(estado)
        print(f"g=0  h={h0}  f={0 + h0}")

    for paso, movimiento in enumerate(lista_movimientos, start=1):
        idx0_antes = estado.index(0)
        nuevo = aplicar_movimiento(estado, movimiento)
        if nuevo is None:
            raise RuntimeError(f"Movimiento inválido durante reproducción: {movimiento}")
        estado = nuevo
        if limpiar_pantalla:
            limpiar_consola()
        print(f"\nPaso {paso}: mover {movimiento}")
        imprimir_tablero_resaltado(estado, indice_resaltado=idx0_antes)
        if mostrar_metricas:
            h = heuristica_mc(estado)
            print(f"g={paso}  h={h}  f={paso + h}")
        time.sleep(pausa_segundos)
    print("\nEstado completo finalizado.")

# ------------------------------ Main ------------------------------
if __name__ == "__main__":
    print("           15-puzzle — A* (Manhattan + Conflicto Lineal)          \n")
    tablero = pedir_tablero_interactivo()
    if tablero is None:
        print("No se ingresó ningún tablero. Saliendo.")
        raise SystemExit(0)

    print("\nTablero inicial (manual):")
    imprimir_tablero(tablero)

    explicar_paridad(tablero)
    if not es_resoluble_4x4(tablero):
        print("\nSolvencia: NO RESOLUBLE. No se ejecuta A*.")
        raise SystemExit(0)
    else:
        print("\nSolvencia: RESOLUBLE. Procediendo con A*.")

    h_ini = heuristica_mc(tablero)
    print(f"\nh_MC(inicio) = {h_ini}  (cota inferior de pasos restantes)")

    solucion, expandidos = a_estrella(
        tablero,
        imprimir_progreso=True,
        frecuencia_progreso=10000,
        limite_expansiones=LIMITE_EXPANSIONES
    )

    if solucion is None:
        print(f"\nNo se encontró solución dentro del límite. Nodos expandidos: {expandidos:,}")
    else:
        print(f"\nSolución en {len(solucion)} movimientos. \nNodos expandidos: {expandidos:,}")
        print("Secuencia:", solucion)
        reproducir_movimientos(tablero, solucion)
