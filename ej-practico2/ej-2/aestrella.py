import random
import heapq
import time
from typing import Optional, Tuple, List, Dict, Set

TAMANO_TABLERO: int = 4
ESTADO_OBJETIVO: Tuple[int, ...] = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS: Tuple[str, ...] = ('arriba', 'abajo', 'izquierda', 'derecha')
DESPLAZAMIENTOS: Dict[str, int] = {'arriba': -TAMANO_TABLERO, 'abajo': TAMANO_TABLERO, 'izquierda': -1, 'derecha': 1}
POSICION_OBJETIVO: Dict[int, Tuple[int, int]] = {valor: (i // TAMANO_TABLERO, i % TAMANO_TABLERO) for i, valor in enumerate(ESTADO_OBJETIVO)}

"""
Este solver usa A* con heurística ADMISIBLE:
- h(n) = Distancia Manhattan + Conflicto Lineal (MC).
- Admisible: no sobreestima el costo real óptimo c*(n); garantiza solución óptima.
- Consistente: entre vecinos, h no cambia más de 1 (coste de arista = 1); evita reabrir nodos.

Acerca de numero_mezclas:
- numero_mezclas = número de movimientos aleatorios aplicados DESDE el objetivo para mezclar.
- Controla la dificultad promedio: valores altos => típicamente más difícil.
- Importante: por ciclos, la distancia óptima real de regreso NO tiene por qué ser exactamente numero_mezclas.
"""

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
    # Evitar "wrap" lateral (no cruzar de fila con izquierda/derecha)
    if movimiento in ('izquierda', 'derecha'):
        fila0, _ = indice_a_fila_columna(indice_cero)
        fila1, _ = indice_a_fila_columna(indice_cero + delta)
        if fila0 != fila1:
            return None
    lista = list(estado)
    indice_intercambio = indice_cero + delta
    lista[indice_cero], lista[indice_intercambio] = lista[indice_intercambio], lista[indice_cero]
    return tuple(lista)

def imprimir_tablero(estado: Tuple[int, ...]) -> None:
    for fila in range(TAMANO_TABLERO):
        segmento = estado[fila * TAMANO_TABLERO:(fila + 1) * TAMANO_TABLERO]
        print(' '.join(f'{x:2d}' if x != 0 else '  .' for x in segmento))

# Animación en consola 
def imprimir_tablero_resaltado(estado: Tuple[int, ...], indice_resaltado: Optional[int] = None) -> None:
    """Imprime el tablero y resalta (con corchetes) la casilla en indice_resaltado."""
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

def limpiar_consola() -> None:
    """Limpia la consola en Windows/Unix."""
    import os, sys
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

def reproducir_movimientos(
    estado_inicial: Tuple[int, ...],
    lista_movimientos: List[str],
    pausa_segundos: float = 0.35,
    limpiar_pantalla: bool = False,
    mostrar_metricas: bool = True
) -> None:
    """
    Reproduce la solución movimiento a movimiento.
    - Resalta la ficha que se acaba de mover (la que intercambió con el 0).
    - Si limpiar_pantalla=True, va “animando” en la consola.
    - Si mostrar_metricas=True, muestra g, h y f en cada paso.
    """
    estado = estado_inicial
    print("\nEstado inicial:")
    imprimir_tablero(estado)
    if mostrar_metricas:
        h0 = heuristica_mc(estado)
        print(f"g=0  h={h0}  f={0 + h0}")

    for paso, movimiento in enumerate(lista_movimientos, start=1):
        indice_cero_antes = estado.index(0)
        estado_nuevo = aplicar_movimiento(estado, movimiento)
        if estado_nuevo is None:
            raise RuntimeError(f"Movimiento inválido durante reproducción: {movimiento}")

        # La ficha movida queda en la posición donde estaba el 0
        indice_ficha_movida_en_nuevo = indice_cero_antes

        g = paso
        h = heuristica_mc(estado_nuevo) if mostrar_metricas else 0
        f = g + h

        if limpiar_pantalla:
            limpiar_consola()

        print(f"\nPaso {paso}: mover {movimiento}")
        imprimir_tablero_resaltado(estado_nuevo, indice_resaltado=indice_ficha_movida_en_nuevo)
        if mostrar_metricas:
            print(f"g={g}  h={h}  f={f}")

        time.sleep(pausa_segundos)
        estado = estado_nuevo

    print("\nEstado completo finalizado.")

# Solvencia 
def es_resoluble_4x4(estado: Tuple[int, ...]) -> bool:
    # Validación de contenido {0..15} sin duplicados
    if tuple(sorted(estado)) != tuple(range(TAMANO_TABLERO * TAMANO_TABLERO)):
        return False
    lista_sin_cero: List[int] = [x for x in estado if x != 0]
    numero_inversiones = 0
    for i in range(len(lista_sin_cero)):
        for j in range(i + 1, len(lista_sin_cero)):
            if lista_sin_cero[i] > lista_sin_cero[j]:
                numero_inversiones += 1
    indice_cero = estado.index(0)
    fila_desde_arriba = indice_cero // TAMANO_TABLERO
    fila_hueco_desde_abajo = TAMANO_TABLERO - fila_desde_arriba  # 1..T
    # Regla 4x4: resoluble ssi (inversiones + fila_hueco_desde_abajo) es impar
    return (numero_inversiones + fila_hueco_desde_abajo) % 2 == 1

# Heurística: Manhattan + Conflicto Lineal
def distancia_manhattan(estado: Tuple[int, ...]) -> int:
    distancia_total = 0
    for indice, valor in enumerate(estado):
        if valor == 0:
            continue
        fila_act, col_act = indice_a_fila_columna(indice)
        fila_obj, col_obj = POSICION_OBJETIVO[valor]
        distancia_total += abs(fila_act - fila_obj) + abs(col_act - col_obj)
    return distancia_total

def conflicto_lineal(estado: Tuple[int, ...]) -> int:
    conflictos = 0
    # Filas
    for fila in range(TAMANO_TABLERO):
        columnas_objetivo_en_fila: List[int] = []
        for columna in range(TAMANO_TABLERO):
            valor = estado[fila_columna_a_indice(fila, columna)]
            if valor != 0 and POSICION_OBJETIVO[valor][0] == fila:
                columnas_objetivo_en_fila.append(POSICION_OBJETIVO[valor][1])
        # contar pares invertidos (inversiones) en columnas_objetivo_en_fila
        for i in range(len(columnas_objetivo_en_fila)):
            for j in range(i + 1, len(columnas_objetivo_en_fila)):
                if columnas_objetivo_en_fila[i] > columnas_objetivo_en_fila[j]:
                    conflictos += 1
    # Columnas
    for columna in range(TAMANO_TABLERO):
        filas_objetivo_en_columna: List[int] = []
        for fila in range(TAMANO_TABLERO):
            valor = estado[fila_columna_a_indice(fila, columna)]
            if valor != 0 and POSICION_OBJETIVO[valor][1] == columna:
                filas_objetivo_en_columna.append(POSICION_OBJETIVO[valor][0])
        for i in range(len(filas_objetivo_en_columna)):
            for j in range(i + 1, len(filas_objetivo_en_columna)):
                if filas_objetivo_en_columna[i] > filas_objetivo_en_columna[j]:
                    conflictos += 1
    return 2 * conflictos

def heuristica_mc(estado: Tuple[int, ...]) -> int:
    # Heurística MC (admisible y consistente)
    return distancia_manhattan(estado) + conflicto_lineal(estado)

# Generar instancia a N movimientos del objetivo 
def mezclar_desde_objetivo(numero_mezclas: int, semilla: Optional[int] = None) -> Tuple[int, ...]:
    if semilla is not None:
        random.seed(semilla)
    estado: Tuple[int, ...] = ESTADO_OBJETIVO
    ultimo_movimiento: Optional[str] = None
    movimiento_inverso: Dict[str, str] = {'arriba': 'abajo', 'abajo': 'arriba', 'izquierda': 'derecha', 'derecha': 'izquierda'}
    for _ in range(numero_mezclas):
        indice_cero = estado.index(0)
        movimientos_posibles: List[str] = [m for m in LISTA_MOVIMIENTOS if movimiento_valido(indice_cero, m)]
        if ultimo_movimiento and movimiento_inverso[ultimo_movimiento] in movimientos_posibles:
            movimientos_posibles.remove(movimiento_inverso[ultimo_movimiento])  # evita deshacer inmediato
        movimiento_elegido = random.choice(movimientos_posibles)
        estado = aplicar_movimiento(estado, movimiento_elegido)  # type: ignore[assignment]
        ultimo_movimiento = movimiento_elegido
    # Solvencia garantizada por construcción
    return estado

# A* con progreso, MC fija y límite 
def a_estrella(
    estado_inicial: Tuple[int, ...],
    imprimir_progreso: bool = True,
    frecuencia_progreso: int = 10000,
    limite_expansiones: int = 1_000_000
) -> Tuple[Optional[List[str]], int]:
    h = heuristica_mc  # Usamos SIEMPRE Manhattan + Conflicto Lineal
    if estado_inicial == ESTADO_OBJETIVO:
        return [], 0

    costo_desde_inicio: Dict[Tuple[int, ...], int] = {estado_inicial: 0}
    predecesor: Dict[Tuple[int, ...], Tuple[Optional[Tuple[int, ...]], Optional[str]]] = {estado_inicial: (None, None)}
    cerrados: Set[Tuple[int, ...]] = set()
    abiertos_heap: List[Tuple[int, int, int, Tuple[int, ...]]] = []
    contador_orden = 0
    expandidos = 0

    f_inicial = h(estado_inicial)  # g=0
    heapq.heappush(abiertos_heap, (f_inicial, h(estado_inicial), contador_orden, estado_inicial))

    instante_inicio = time.time()
    while abiertos_heap:
        f_actual, h_del_estado_actual, _, estado_actual = heapq.heappop(abiertos_heap)
        if estado_actual in cerrados:
            continue

        if estado_actual == ESTADO_OBJETIVO:
            # reconstruir camino
            camino: List[str] = []
            cursor: Tuple[int, ...] = estado_actual
            while predecesor[cursor][0] is not None:
                anterior, movimiento = predecesor[cursor]
                camino.append(movimiento or "")
                cursor = anterior or ESTADO_OBJETIVO
            camino.reverse()
            # duracion = time.time() - instante_inicio
            return camino, expandidos

        cerrados.add(estado_actual)
        expandidos += 1
        if imprimir_progreso and expandidos % frecuencia_progreso == 0:
            print(f"[A*] Expandidos: {expandidos:,}  f={f_actual}  h={h_del_estado_actual}  g={costo_desde_inicio[estado_actual]}")

        if expandidos >= limite_expansiones:
            return None, expandidos

        g_estado_actual = costo_desde_inicio[estado_actual]
        for movimiento in LISTA_MOVIMIENTOS:  # orden determinista
            vecino = aplicar_movimiento(estado_actual, movimiento)
            if vecino is None:
                continue
            costo_g_tentativo = g_estado_actual + 1

            # Si ya se cerró con un g mejor o igual, ignoro
            if vecino in cerrados and costo_g_tentativo >= costo_desde_inicio.get(vecino, float('inf')):
                continue

            # Si mejora el mejor g conocido, actualizo y REINSERTO en heap SIEMPRE (permitir duplicados)
            if costo_g_tentativo < costo_desde_inicio.get(vecino, float('inf')):
                costo_desde_inicio[vecino] = costo_g_tentativo
                predecesor[vecino] = (estado_actual, movimiento)
                h_vecino = h(vecino)
                f_vecino = costo_g_tentativo + h_vecino
                contador_orden += 1
                heapq.heappush(abiertos_heap, (f_vecino, h_vecino, contador_orden, vecino))
            # Si no mejora, no hago nada

    return None, expandidos


if __name__ == "__main__":
    print("Generando tablero a N movimientos del objetivo (numero_mezclas).")
    try:
        numero_mezclas = int(input("\nElige numero_mezclas (0–200; p.ej. 25 fácil, 40 medio, 50+ difícil): ").strip() or "25")
    except ValueError:
        numero_mezclas = 25
    numero_mezclas = max(0, min(200, numero_mezclas))  # limitar a rango razonable

    entrada_semilla = input("\nSemilla (opcional, enter para ninguna): ").strip()
    semilla = int(entrada_semilla) if entrada_semilla.isdigit() else None

    estado_inicial = mezclar_desde_objetivo(numero_mezclas, semilla=semilla)

    print("\nTablero inicial:")
    imprimir_tablero(estado_inicial)

    print("\nEstado objetivo (tablero ordenado):")
    imprimir_tablero(ESTADO_OBJETIVO)
    print(f"\nh_MC(objetivo) = {heuristica_mc(ESTADO_OBJETIVO)}  (debe ser 0)")

    # Solvencia (siempre True al mezclar desde objetivo, pero lo mostramos)
    print("\nSolvencia (4x4):", "RESOLUBLE" if es_resoluble_4x4(estado_inicial) else "NO RESOLUBLE")

    # Mostrar heurística estimada al inicio (cota inferior del costo real)
    h_inicial = heuristica_mc(estado_inicial)
    print(f"h_MC(inicio) = {h_inicial}  (estimación mínima de pasos restantes)")

    solucion, nodos_expandidos = a_estrella(
        estado_inicial,
        imprimir_progreso=True,
        frecuencia_progreso=10000,
        limite_expansiones=1_000_000
    )

    if solucion is None:
        print(f"\nNo se encontró solución dentro del límite. Nodos expandidos: {nodos_expandidos:,}")
    else:
        print(f"\nSolución en {len(solucion)} movimientos. \n Nodos expandidos: {nodos_expandidos:,}")
        print("\nSecuencia:", solucion)

        # ===== Reproducción paso a paso =====
        LIMPIAR_PANTALLA = False   # True para “animación” que limpia la consola en cada paso
        PAUSA_SEGUNDOS = 0.35      # tiempo entre pasos
        MOSTRAR_METRICAS = True    # muestra g/h/f en cada estado

        reproducir_movimientos(
            estado_inicial=estado_inicial,
            lista_movimientos=solucion,
            pausa_segundos=PAUSA_SEGUNDOS,
            limpiar_pantalla=LIMPIAR_PANTALLA,
            mostrar_metricas=MOSTRAR_METRICAS
        )
