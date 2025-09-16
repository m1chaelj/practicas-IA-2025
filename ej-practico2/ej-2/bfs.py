import time
from collections import deque
from typing import Optional, Tuple, List, Dict, Set

# ------------------------------ Configuración base ------------------------------
TAMANO_TABLERO: int = 4
ESTADO_OBJETIVO: Tuple[int, ...] = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS: Tuple[str, ...] = ('arriba', 'abajo', 'izquierda', 'derecha')  # orden determinista
DESPLAZAMIENTOS: Dict[str, int] = {'arriba': -TAMANO_TABLERO, 'abajo': TAMANO_TABLERO, 'izquierda': -1, 'derecha': 1}

# Visualización paso a paso
LIMPIAR_PANTALLA: bool = False  # True para limpiar consola en cada paso
PAUSA_SEGUNDOS: float = 0.25    # pausa entre pasos al reproducir

# Seguridad para BFS (evitar cuelgues): puedes subir/bajar este número
LIMITE_EXPANSIONES_BFS: int = 1_000_000

# ------------------------------ Utilidades de tablero ------------------------------
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
    # Evitar “wrap” lateral (no cruzar de fila) en izquierda/derecha
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
    # Imprime el tablero y resalta (con corchetes) la casilla donde estaba el 0 antes (la ficha que se movió).
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

# ------------------------------ Solvencia (4x4) ------------------------------
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

# ------------------------------ Reconstrucción de camino ------------------------------
def reconstruir_camino(predecesor: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]],
                    estado_meta: Tuple[int, ...]) -> List[str]:
    camino: List[str] = []
    cursor: Tuple[int, ...] = estado_meta
    while predecesor[cursor][0] is not None:
        anterior, movimiento = predecesor[cursor]
        camino.append(movimiento or "")
        cursor = anterior or ESTADO_OBJETIVO
    camino.reverse()
    return camino

# ------------------------------ BFS (Búsqueda en anchura) ------------------------------
def bfs(estado_inicial: Tuple[int, ...],
        limite_expansiones: int = LIMITE_EXPANSIONES_BFS) -> Optional[List[str]]:
    # BFS clásico: óptimo en número de movimientos (coste uniforme).
    # Usa cola FIFO y 'visitados' para no repetir estados.
    # Si supera 'limite_expansiones', devuelve None.
    if estado_inicial == ESTADO_OBJETIVO:
        # Si ya está resuelto, retorna lista vacía
        return []

    visitados: Set[Tuple[int, ...]] = {estado_inicial}  # Conjunto de estados ya visitados
    cola: deque = deque([estado_inicial])  # Cola FIFO para estados a expandir
    predecesor: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {estado_inicial: (None, None)}

    expandidos = 0  # Contador de nodos expandidos
    while cola:
        estado = cola.popleft()  # Saca el siguiente estado de la cola
        expandidos += 1
        if expandidos >= limite_expansiones:
            # Si se supera el límite de expansiones, termina sin solución
            return None

        for movimiento in LISTA_MOVIMIENTOS:  # Intenta todos los movimientos posibles
            sucesor = aplicar_movimiento(estado, movimiento)
            if sucesor is None or sucesor in visitados:
                # Si el movimiento no es válido o ya se visitó, lo ignora
                continue
            visitados.add(sucesor)  # Marca el estado como visitado
            predecesor[sucesor] = (estado, movimiento)  # Guarda el predecesor y el movimiento
            if sucesor == ESTADO_OBJETIVO:
                # Si se alcanza el objetivo, reconstruye y retorna el camino
                return reconstruir_camino(predecesor, sucesor)
            cola.append(sucesor)  # Agrega el sucesor a la cola para expandirlo después

    return None  # No se encontró solución (no debería ocurrir en 15-puzzle, pero por completitud)

# ------------------------------ Parser estricto e input interactivo ------------------------------
def parsear_tablero_estricto(texto: str) -> Optional[Tuple[int, ...]]:
    # Acepta espacios y/o comas como separadores
    tokens = texto.replace(",", " ").split()
    # Espera que se ocupen bien los espacios para los 16
    if len(tokens) != TAMANO_TABLERO * TAMANO_TABLERO:
        print(f"\nEntrada inválida: se leyeron {len(tokens)} valores, se requieren {TAMANO_TABLERO*TAMANO_TABLERO}.")
        return None
    # Espera que se ocupen bien los espacios para los 16
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
    print("Pega 16 números (0..15), 0 es el hueco. Puedes usar espacios o comas.")
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
            return None
        tablero = parsear_tablero_estricto("\n".join(lineas))
        if tablero is not None:
            return tablero
        print("\nEntrada inválida. Intenta de nuevo (o presiona Enter inmediatamente para cancelar).\n")

# ------------------------------ Reproducción paso a paso ------------------------------
def reproducir_movimientos(estado_inicial: Tuple[int, ...],
                        lista_movimientos: List[str],
                        pausa_segundos: float = PAUSA_SEGUNDOS,
                        limpiar_pantalla: bool = LIMPIAR_PANTALLA) -> None:
    estado = estado_inicial
    print("\nEstado inicial:")
    imprimir_tablero(estado)
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
        time.sleep(pausa_segundos)
    print("\nEstado completo finalizado.")


if __name__ == "__main__":
    print("           15-puzzle — BFS (Búsqueda en anchura)          \n")
    tablero = pedir_tablero_interactivo()
    if tablero is None:
        print("No se ingresó ningún tablero. Saliendo.")
        raise SystemExit(0)

    print("\nTablero inicial (manual):")
    imprimir_tablero(tablero)

    # Mostrar solvencia y decidir
    explicar_paridad(tablero)
    if not es_resoluble_4x4(tablero):
        print("\nSolvencia: NO RESOLUBLE. No se ejecuta BFS.")
        raise SystemExit(0)
    else:
        print("\nSolvencia: RESOLUBLE. Procediendo con BFS...")

    # Ejecutar BFS (con límite de expansiones para evitar cuelgues)
    camino = bfs(tablero, limite_expansiones=LIMITE_EXPANSIONES_BFS)

    if camino is None:
        print("\nNo se encontró solución dentro del límite de expansiones "
            f"({LIMITE_EXPANSIONES_BFS:,}). Considera usar A* o bajar la dificultad.")
    else:
        print(f"\nSolución en {len(camino)} movimientos (óptima).")
        print("Secuencia:", camino)
        reproducir_movimientos(tablero, camino)
