import re
import time
from collections import deque

# ------------------------------ Configuración base ------------------------------
TAMANO_TABLERO = 4
ESTADO_OBJETIVO = tuple(list(range(1, TAMANO_TABLERO * TAMANO_TABLERO)) + [0])
LISTA_MOVIMIENTOS = ('arriba', 'abajo', 'izquierda', 'derecha')
DESPLAZAMIENTOS = {'arriba': -TAMANO_TABLERO, 'abajo': TAMANO_TABLERO, 'izquierda': -1, 'derecha': 1}
POSICION_OBJETIVO = {v: (i // TAMANO_TABLERO, i % TAMANO_TABLERO) for i, v in enumerate(ESTADO_OBJETIVO)}

# Reproducción visual
LIMPIAR_PANTALLA = False   # True => limpia pantalla en cada paso
PAUSA_SEGUNDOS = 0.25      # pausa entre pasos

# Límites operativos BFS (puedes ajustar estas constantes si quieres)
LIMITE_EXPANSIONES_BFS = 1_000_000
TIMEOUT_SEGUNDOS_BFS = 30.0  # None para desactivar timeout

# ------------------------------ Utilidades de tablero ------------------------------
def indice_a_fila_columna(indice):
    return divmod(indice, TAMANO_TABLERO)

def fila_columna_a_indice(fila, columna):
    return fila * TAMANO_TABLERO + columna

def movimiento_valido(indice_cero, movimiento):
    fila, columna = indice_a_fila_columna(indice_cero)
    if movimiento == 'arriba':    return fila > 0
    if movimiento == 'abajo':     return fila < TAMANO_TABLERO - 1
    if movimiento == 'izquierda': return columna > 0
    if movimiento == 'derecha':   return columna < TAMANO_TABLERO - 1
    return False

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
    if tuple(sorted(estado)) != tuple(range(TAMANO_TABLERO*TAMANO_TABLERO)):
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

# ------------------------------ BFS (Búsqueda en anchura) ------------------------------
def bfs(estado_inicial, limite_expansiones=LIMITE_EXPANSIONES_BFS, timeout_segundos=TIMEOUT_SEGUNDOS_BFS):
    """Devuelve (lista_de_movimientos, nodos_expandidos) o (None, nodos_expandidos) si alcanza límite/timeout."""
    if estado_inicial == ESTADO_OBJETIVO:
        return [], 0

    t0 = time.time()
    expandidos = 0

    cola = deque([estado_inicial])
    visitados = {estado_inicial}
    predecesor = {estado_inicial: (None, None)}  # estado -> (anterior, movimiento)

    while cola:
        if timeout_segundos is not None and (time.time() - t0) >= timeout_segundos:
            return None, expandidos
        if expandidos >= limite_expansiones:
            return None, expandidos

        estado = cola.popleft()
        expandidos += 1

        for mov in LISTA_MOVIMIENTOS:  # orden determinista
            sucesor = aplicar_movimiento(estado, mov)
            if sucesor is None or sucesor in visitados:
                continue
            predecesor[sucesor] = (estado, mov)
            if sucesor == ESTADO_OBJETIVO:
                # reconstruir camino
                camino = []
                cur = sucesor
                while predecesor[cur][0] is not None:
                    ant, m = predecesor[cur]
                    camino.append(m or "")
                    cur = ant or ESTADO_OBJETIVO
                camino.reverse()
                return camino, expandidos
            visitados.add(sucesor)
            cola.append(sucesor)

    return None, expandidos  # no debería pasar si hay solución y sin límites

# ------------------------------ Parser estricto e input ------------------------------
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
                        limpiar_pantalla=LIMPIAR_PANTALLA):
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

# ------------------------------ Main ------------------------------
if __name__ == "__main__":
    print("           15-puzzle — BFS (Búsqueda en anchura)          \n")

    tablero = pedir_tablero_interactivo()
    if tablero is None:
        print("No se ingresó ningún tablero. Saliendo.")
        raise SystemExit(0)

    print("\nTablero inicial (manual):")
    imprimir_tablero(tablero)

    explicar_paridad(tablero)
    if not es_resoluble_4x4(tablero):
        print("\nSolvencia: NO RESOLUBLE. No se ejecuta BFS.")
        raise SystemExit(0)
    else:
        print("\nSolvencia: RESOLUBLE. Procediendo con BFS...")

    # Ejecutar BFS con límites por defecto (puedes editar las constantes arriba si necesitas)
    camino, expandidos = bfs(
        tablero,
        limite_expansiones=LIMITE_EXPANSIONES_BFS,
        timeout_segundos=TIMEOUT_SEGUNDOS_BFS
    )

    if camino is None:
        print(f"\nNo se encontró solución dentro del límite "
            f"(expansiones={LIMITE_EXPANSIONES_BFS:,}, timeout={TIMEOUT_SEGUNDOS_BFS}s).")
    else:
        print(f"\nSolución en {len(camino)} movimientos (óptima en # de movimientos).")
        print("Secuencia:", camino)
        reproducir_movimientos(tablero, camino)
