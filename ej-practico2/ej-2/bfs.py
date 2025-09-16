import random
import time
from collections import deque
from typing import Optional, Tuple, List, Dict

TAMANO_TABLERO: int = 4
ESTADO_OBJETIVO: Tuple[int, ...] = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS: Tuple[str, ...] = ('arriba', 'abajo', 'izquierda', 'derecha')  # orden determinista
DESPLAZAMIENTOS: Dict[str, int] = {
    'arriba': -TAMANO_TABLERO,
    'abajo': TAMANO_TABLERO,
    'izquierda': -1,
    'derecha': 1,
}

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
    # Evitar cruzar de fila con izquierda/derecha
    if movimiento in ('izquierda', 'derecha'):
        fila0, _ = indice_a_fila_columna(indice_cero)
        fila1, _ = indice_a_fila_columna(indice_cero + delta)
        if fila0 != fila1:
            return None
    lista = list(estado)
    indice_intercambio = indice_cero + delta
    lista[indice_cero], lista[indice_intercambio] = lista[indice_intercambio], lista[indice_cero]
    return tuple(lista)

def invertir_movimiento(movimiento: str) -> str:
    inverso = {'arriba': 'abajo', 'abajo': 'arriba', 'izquierda': 'derecha', 'derecha': 'izquierda'}
    return inverso[movimiento]

def imprimir_tablero(estado: Tuple[int, ...]) -> None:
    for fila in range(TAMANO_TABLERO):
        segmento = estado[fila * TAMANO_TABLERO:(fila + 1) * TAMANO_TABLERO]
        print(' '.join(f'{x:2d}' if x != 0 else '  .' for x in segmento))

def imprimir_tablero_resaltado(estado: Tuple[int, ...], indice_resaltado: Optional[int] = None) -> None:
    """Imprime el tablero y resalta (con corchetes) la casilla en indice_resaltado (donde estaba el 0 antes)."""
    for fila in range(TAMANO_TABLERO):
        celdas = []
        for columna in range(TAMANO_TABLERO):
            idx = fila_columna_a_indice(fila, columna)
            valor = estado[idx]
            celda = f'{valor:2d}' if valor != 0 else '  .'
            if indice_resaltado is not None and idx == indice_resaltado:
                celda = f'[{celda}]'
            celdas.append(celda)
        print(' '.join(celdas))

# Solvencia
def es_resoluble_4x4(estado: Tuple[int, ...]) -> bool:
    # Validación de contenido {0..15} sin duplicados
    if tuple(sorted(estado)) != tuple(range(TAMANO_TABLERO * TAMANO_TABLERO)):
        return False
    plano = [x for x in estado if x != 0]
    numero_inversiones = sum(1 for i in range(len(plano)) for j in range(i + 1, len(plano)) if plano[i] > plano[j])
    indice_cero = estado.index(0)
    fila_cero_desde_arriba = indice_cero // TAMANO_TABLERO
    fila_cero_desde_abajo = TAMANO_TABLERO - fila_cero_desde_arriba  # 1..4
    return (numero_inversiones + fila_cero_desde_abajo) % 2 == 1

# Generadores de instancias
def tablero_resoluble_aleatorio() -> Tuple[int, ...]:
    """Baraja al azar hasta obtener un estado resoluble (sin k)."""
    numeros = list(range(TAMANO_TABLERO * TAMANO_TABLERO))
    while True:
        random.shuffle(numeros)
        estado = tuple(numeros)
        if es_resoluble_4x4(estado):
            return estado

def mezclar_desde_objetivo(numero_mezclas: int, semilla: Optional[int] = None) -> Tuple[int, ...]:
    """Aplica 'numero_mezclas' movimientos aleatorios DESDE el objetivo (solvencia garantizada)."""
    if semilla is not None:
        random.seed(semilla)
    estado = ESTADO_OBJETIVO
    ultimo = None
    inverso = {'arriba': 'abajo', 'abajo': 'arriba', 'izquierda': 'derecha', 'derecha': 'izquierda'}
    for _ in range(max(0, numero_mezclas)):
        indice_cero = estado.index(0)
        posibles = [m for m in LISTA_MOVIMIENTOS if movimiento_valido(indice_cero, m)]
        if ultimo and inverso[ultimo] in posibles:
            posibles.remove(inverso[ultimo])  # evitar deshacer inmediato
        m = random.choice(posibles)
        estado = aplicar_movimiento(estado, m) or estado
        ultimo = m
    return estado

# Reconstrucción de camino 
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

# Búsqueda Bidireccional (con límites operativos)
def busqueda_bidireccional(
    estado_inicial: Tuple[int, ...],
    timeout_segundos: Optional[float],
    limite_expansiones: int
) -> Optional[List[str]]:
    """
    BFS desde el inicio y desde el objetivo a la vez.
    * Óptimo en # de movimientos.
    * Respeta timeout y límite de expansiones (sin imprimir métricas).
    """
    if estado_inicial == ESTADO_OBJETIVO:
        return []

    instante_inicio = time.time()
    expandidos_total = 0  # sumado entre ambos frentes

    cola_izq: deque = deque([estado_inicial])   # desde inicio
    cola_der: deque = deque([ESTADO_OBJETIVO])  # desde objetivo

    visitado_izq: Dict[Tuple[int, ...], int] = {estado_inicial: 0}
    visitado_der: Dict[Tuple[int, ...], int] = {ESTADO_OBJETIVO: 0}

    prede_izq: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {estado_inicial: (None, None)}
    prede_der: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {ESTADO_OBJETIVO: (None, None)}

    def tiempo_excedido() -> bool:
        return timeout_segundos is not None and (time.time() - instante_inicio) >= timeout_segundos

    def expandir_desde_izq() -> Optional[Tuple[int, ...]]:
        nonlocal expandidos_total
        if not cola_izq:
            return None
        estado = cola_izq.popleft()
        profundidad = visitado_izq[estado]
        for movimiento in LISTA_MOVIMIENTOS:
            sucesor = aplicar_movimiento(estado, movimiento)
            if sucesor is None or sucesor in visitado_izq:
                continue
            visitado_izq[sucesor] = profundidad + 1
            prede_izq[sucesor] = (estado, movimiento)
            expandidos_total += 1
            if sucesor in visitado_der:
                return sucesor
            cola_izq.append(sucesor)
            if expandidos_total >= limite_expansiones or tiempo_excedido():
                return None
        return None

    def expandir_desde_der() -> Optional[Tuple[int, ...]]:
        nonlocal expandidos_total
        if not cola_der:
            return None
        estado = cola_der.popleft()
        profundidad = visitado_der[estado]
        for movimiento in LISTA_MOVIMIENTOS:
            sucesor = aplicar_movimiento(estado, movimiento)
            if sucesor is None or sucesor in visitado_der:
                continue
            visitado_der[sucesor] = profundidad + 1
            prede_der[sucesor] = (estado, movimiento)
            expandidos_total += 1
            if sucesor in visitado_izq:
                return sucesor
            cola_der.append(sucesor)
            if expandidos_total >= limite_expansiones or tiempo_excedido():
                return None
        return None

    while cola_izq and cola_der:
        if tiempo_excedido() or expandidos_total >= limite_expansiones:
            return None
        # expandir siempre la cola más pequeña (balance)
        expandir_izq = len(cola_izq) <= len(cola_der)
        encuentro = expandir_desde_izq() if expandir_izq else expandir_desde_der()
        if encuentro is not None:
            # inicio -> encuentro
            camino_izq = reconstruir_camino(prede_izq, encuentro)
            # objetivo -> encuentro (desde el lado derecho)
            camino_der_obj_a_enc = reconstruir_camino(prede_der, encuentro)
            # encuentro -> objetivo (invertir orden y movimientos)
            camino_enc_a_obj = [invertir_movimiento(m) for m in reversed(camino_der_obj_a_enc)]
            return camino_izq + camino_enc_a_obj

    return None  # sin solución dentro de límites (o fronteras vacías)

# Reproducción paso a paso
def reproducir_movimientos(estado_inicial: Tuple[int, ...], lista_movimientos: List[str], pausa_segundos: float = 0.25) -> None:
    estado = estado_inicial
    print("\nEstado inicial:")
    imprimir_tablero(estado)
    for paso, movimiento in enumerate(lista_movimientos, start=1):
        indice_cero_antes = estado.index(0)
        nuevo = aplicar_movimiento(estado, movimiento)
        if nuevo is None:
            raise RuntimeError(f"Movimiento inválido durante reproducción: {movimiento}")
        estado = nuevo
        print(f"\nPaso {paso}: mover {movimiento}")
        imprimir_tablero_resaltado(estado, indice_resaltado=indice_cero_antes)
        time.sleep(pausa_segundos)
    print("\nEstado completo finalizado.")


if __name__ == "__main__":
    print("Generación del tablero inicial:")
    print("  1) Mezclar desde objetivo con k (control de dificultad)")
    print("  2) Aleatorio resoluble")
    opcion = input("Elige la opcion 1 o 2, default=1]: ").strip() or "1"

    if opcion == "1":
        try:
            k = int(input("k (0–200; 25 fácil, 40 medio, 60+ difícil) [40]: ").strip() or "40")
        except ValueError:
            k = 40
        k = max(0, min(200, k))
        sem = input("Semilla (opcional, Enter para ninguna): ").strip()
        semilla = int(sem) if sem.isdigit() else None
        estado_inicial = mezclar_desde_objetivo(k, semilla=semilla)
    else:
        sem = input("Semilla (opcional, Enter para ninguna): ").strip()
        if sem.isdigit():
            random.seed(int(sem))
        estado_inicial = tablero_resoluble_aleatorio()

    print("\nTablero inicial:")
    imprimir_tablero(estado_inicial)
    print("\nEstado objetivo (tablero ordenado):")
    imprimir_tablero(ESTADO_OBJETIVO)

    # Límites operativos
    # RECOMENDADO:
    #   TIMEOUT_SEGUNDOS = 30.0   # 15–60 s suele ir bien para k <= ~60
    #   LIMITE_EXPANSIONES = 10_000_000  # 2–20 M según tu memoria/tiempo
    try:
        TIMEOUT_SEGUNDOS = input("Timeout en segundos (Enter=30): ").strip()
        TIMEOUT_SEGUNDOS = float(TIMEOUT_SEGUNDOS) if TIMEOUT_SEGUNDOS else 30.0
    except ValueError:
        TIMEOUT_SEGUNDOS = 30.0

    try:
        LIMITE_EXPANSIONES = input("Límite de expansiones (Enter=10000000): ").strip()
        LIMITE_EXPANSIONES = int(LIMITE_EXPANSIONES) if LIMITE_EXPANSIONES else 10_000_000
    except ValueError:
        LIMITE_EXPANSIONES = 10_000_000

    print("\nResolviendo con BDS...")
    camino = busqueda_bidireccional(
        estado_inicial=estado_inicial,
        timeout_segundos=TIMEOUT_SEGUNDOS,
        limite_expansiones=LIMITE_EXPANSIONES
    )

    if camino is None:
        print("\nNo se encontró solución dentro de los límites (tiempo/expansiones).")
    else:
        print(f"\nSolución en {len(camino)} movimientos (óptima).")
        print("Secuencia:", camino)
        # Reproducción paso a paso automática
        reproducir_movimientos(estado_inicial, camino, pausa_segundos=0.25)
