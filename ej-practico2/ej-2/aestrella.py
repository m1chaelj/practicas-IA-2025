# resolver_15puzzle_astar.py
import heapq
import time
from typing import Optional, Tuple, List, Dict, Set

# ==================== Configuración base ====================
TAMANO_TABLERO: int = 4
ESTADO_OBJETIVO: Tuple[int, ...] = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS: Tuple[str, ...] = ('arriba', 'abajo', 'izquierda', 'derecha')
DESPLAZAMIENTOS: Dict[str, int] = {'arriba': -TAMANO_TABLERO, 'abajo': TAMANO_TABLERO, 'izquierda': -1, 'derecha': 1}
POSICION_OBJETIVO: Dict[int, Tuple[int, int]] = {v: (i // TAMANO_TABLERO, i % TAMANO_TABLERO)
                                                for i, v in enumerate(ESTADO_OBJETIVO)}

# Visualización paso a paso
LIMPIAR_PANTALLA: bool = False
PAUSA_SEGUNDOS: float = 0.35
MOSTRAR_METRICAS: bool = True

# Límite operativo para A*
LIMITE_EXPANSIONES: int = 1_000_000

# ==================== Utilidades de tablero ====================
def indice_a_fila_columna(indice: int) -> Tuple[int, int]:
    return divmod(indice, TAMANO_TABLERO)

def fila_columna_a_indice(fila: int, columna: int) -> int:
    return fila * TAMANO_TABLERO + columna

def movimiento_valido(indice_cero: int, movimiento: str) -> bool:
    fila, columna = indice_a_fila_columna(indice_cero)
    if movimiento == 'arriba':    return fila > 0
    if movimiento == 'abajo':     return fila < TAMANO_TABLERO - 1
    if movimiento == 'izquierda': return columna > 0
    if movimiento == 'derecha':   return columna < TAMANO_TABLERO - 1
    return False

def aplicar_movimiento(estado: Tuple[int, ...], movimiento: str) -> Optional[Tuple[int, ...]]:
    indice_cero = estado.index(0)
    if not movimiento_valido(indice_cero, movimiento):
        return None
    delta = DESPLAZAMIENTOS[movimiento]
    # Evitar "wrap" lateral en izquierda/derecha (no cruzar de fila)
    if movimiento in ('izquierda', 'derecha'):
        fila0, _ = indice_a_fila_columna(indice_cero)
        fila1, _ = indice_a_fila_columna(indice_cero + delta)
        if fila0 != fila1:
            return None
    lista = list(estado)
    j = indice_cero + delta
    lista[indice_cero], lista[j] = lista[j], lista[indice_cero]
    return tuple(lista)

def imprimir_tablero(estado: Tuple[int, ...]) -> None:
    for fila in range(TAMANO_TABLERO):
        segmento = estado[fila * TAMANO_TABLERO:(fila + 1) * TAMANO_TABLERO]
        print(' '.join(f'{x:2d}' if x != 0 else '  .' for x in segmento))

def imprimir_tablero_resaltado(estado: Tuple[int, ...], indice_resaltado: Optional[int] = None) -> None:
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

def limpiar_consola() -> None:
    import os, sys
    os.system('cls' if sys.platform.startswith('win') else 'clear')

# ==================== Solvencia (4x4) ====================
def calcular_inversiones_y_R(estado: Tuple[int, ...]) -> Tuple[int, int]:
    plano = [x for x in estado if x != 0]
    inversiones = sum(1 for i in range(len(plano)) for j in range(i+1, len(plano)) if plano[i] > plano[j])
    idx0 = estado.index(0)
    fila_desde_arriba = idx0 // TAMANO_TABLERO
    R = TAMANO_TABLERO - fila_desde_arriba  # 1..4
    return inversiones, R

def es_resoluble_4x4(estado: Tuple[int, ...]) -> bool:
    if tuple(sorted(estado)) != tuple(range(TAMANO_TABLERO*TAMANO_TABLERO)):
        return False
    I, R = calcular_inversiones_y_R(estado)
    return (I + R) % 2 == 1

def explicar_paridad(estado: Tuple[int, ...]) -> None:
    I, R = calcular_inversiones_y_R(estado)
    plano = [x for x in estado if x != 0]
    print("\n[Chequeo de solvencia 4x4]")
    print("Secuencia (sin 0):", plano)
    print(f"Inversiones (I) = {I}")
    print(f"Fila del 0 desde abajo (R) = {R}")
    print(f"(I + R) = {I + R}  →  {'IMPAR (RESOLUBLE)' if (I+R)%2==1 else 'PAR (NO RESOLUBLE)'}")

# ==================== Heurística: Manhattan + Conflicto Lineal ====================
def distancia_manhattan(estado: Tuple[int, ...]) -> int:
    total = 0
    for i, v in enumerate(estado):
        if v == 0: continue
        f, c = indice_a_fila_columna(i)
        fo, co = POSICION_OBJETIVO[v]
        total += abs(f-fo) + abs(c-co)
    return total

def conflicto_lineal(estado: Tuple[int, ...]) -> int:
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
                if cols_obj[i] > cols_obj[j]: conf += 1
    # Columnas
    for c in range(TAMANO_TABLERO):
        filas_obj = []
        for f in range(TAMANO_TABLERO):
            v = estado[f*TAMANO_TABLERO + c]
            if v != 0 and POSICION_OBJETIVO[v][1] == c:
                filas_obj.append(POSICION_OBJETIVO[v][0])
        for i in range(len(filas_obj)):
            for j in range(i+1, len(filas_obj)):
                if filas_obj[i] > filas_obj[j]: conf += 1
    return 2*conf

def heuristica_mc(estado: Tuple[int, ...]) -> int:
    return distancia_manhattan(estado) + conflicto_lineal(estado)

# ==================== A* (h = Manhattan + Conflicto Lineal) ====================
def a_estrella(
    estado_inicial: Tuple[int, ...],
    imprimir_progreso: bool = True,
    frecuencia_progreso: int = 10000,
    limite_expansiones: int = LIMITE_EXPANSIONES
) -> Tuple[Optional[List[str]], int]:
    h = heuristica_mc
    if estado_inicial == ESTADO_OBJETIVO:
        return [], 0

    costo_desde_inicio: Dict[Tuple[int, ...], int] = {estado_inicial: 0}
    predecesor: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {estado_inicial: (None, None)}
    cerrados: Set[Tuple[int, ...]] = set()
    abiertos_heap: List[Tuple[int, int, int, Tuple[int, ...]]] = []
    contador_orden = 0
    expandidos = 0

    f0 = h(estado_inicial)
    heapq.heappush(abiertos_heap, (f0, f0, contador_orden, estado_inicial))

    while abiertos_heap:
        f_actual, h_actual, _, estado = heapq.heappop(abiertos_heap)
        if estado in cerrados:
            continue

        if estado == ESTADO_OBJETIVO:
            camino: List[str] = []
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

# ==================== Parser estricto e input interactivo ====================
def parsear_tablero_estricto(texto: str) -> Optional[Tuple[int, ...]]:
    # Acepta espacios y/o comas como separadores
    tokens = texto.replace(",", " ").split()
    # ¿Exactamente 16 tokens?
    if len(tokens) != TAMANO_TABLERO * TAMANO_TABLERO:
        print(f"\nEntrada inválida: se leyeron {len(tokens)} valores, se requieren {TAMANO_TABLERO*TAMANO_TABLERO}.")
        return None
    # ¿Todos numéricos?
    valores: List[int] = []
    for t in tokens:
        try:
            valores.append(int(t))
        except ValueError:
            print(f"\nEntrada inválida: '{t}' no es un número entero.")
            return None
    # Rango permitido
    fuera_de_rango = [x for x in valores if not (0 <= x <= 15)]
    if fuera_de_rango:
        print("Valores fuera de rango [0..15]:", sorted(fuera_de_rango))
        return None
    # Duplicados y faltantes
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

def pedir_tablero_interactivo() -> Optional[Tuple[int, ...]]:
    """
    Pide un tablero al usuario. Permite pegar en varias líneas; línea vacía finaliza la captura.
    Si la entrada es inválida, explica el error y vuelve a pedir.
    Devuelve None si el usuario envía inmediatamente una línea vacía (cancelar).
    """
    print("Pega 16 números (0..15), 0 es el hueco. Puedes usar espacios o comas. ")
    print("Ejemplo: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0")
    print("Deja una línea vacía para validar. Línea vacía inmediata = cancelar.\n")
    while True:
        lineas: List[str] = []
        while True:
            linea = input()
            if not linea.strip():
                break
            lineas.append(linea)
        if not lineas:
            # canceló
            return None
        tablero = parsear_tablero_estricto("\n".join(lineas))
        if tablero is not None:
            return tablero
        print("\nEntrada inválida. Intenta de nuevo (o presiona Enter inmediatamente para cancelar).\n")

# ==================== Reproducción paso a paso ====================
def reproducir_movimientos(
    estado_inicial: Tuple[int, ...],
    lista_movimientos: List[str],
    pausa_segundos: float = PAUSA_SEGUNDOS,
    limpiar_pantalla: bool = LIMPIAR_PANTALLA,
    mostrar_metricas: bool = MOSTRAR_METRICAS
) -> None:
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
        imprimir_tablero_resaltado(estado, indice_resaltado=idx0_antes)  # resalta la ficha movida
        if mostrar_metricas:
            h = heuristica_mc(estado)
            print(f"g={paso}  h={h}  f={paso + h}")
        time.sleep(pausa_segundos)
    print("\nEstado completo finalizado.")

# ==================== Main ====================
if __name__ == "__main__":
    print("           15-puzzle — A* (Manhattan + Conflicto Lineal)          \n")
    tablero = pedir_tablero_interactivo()
    if tablero is None:
        print("No se ingresó ningún tablero. Saliendo.")
        raise SystemExit(0)

    print("\nTablero inicial (manual):")
    imprimir_tablero(tablero)

    # Mostrar solvencia y decidir
    explicar_paridad(tablero)
    if not es_resoluble_4x4(tablero):
        print("\nSolvencia: NO RESOLUBLE. No se ejecuta A*.")
        raise SystemExit(0)
    else:
        print("\nSolvencia: RESOLUBLE. Procediendo con A*.")

    # Info inicial de heurística (cota inferior)
    h_ini = heuristica_mc(tablero)
    print(f"\nh_MC(inicio) = {h_ini}  (cota inferior de pasos restantes)")

    # Resolver con A*
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
