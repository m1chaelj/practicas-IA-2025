# 4 personas llegan a un rio de noche
''''
- Cada que se cruza el puente debe usarse la antorcha ya que es de noche.
- Si cruzan dos personas, uno debe volver atrás llevando la antorcha para que puedan cruzar los demás.
- Individuo A puede cruzar en -> 1 minuto
- Individuo B puede cruzar en -> 2 minutos
- Individuo C puede cruzar en -> 5 minutos
- Individuo D puede cruzar en -> 8 minutos
- Cuando dos individuos cruzan el puente juntos, tardan lo que tarda el mas lento de ellos. 

# Recibe una lista, con el tiempo que tarda cada sujeto en cruzar el fuente. 
# La salida consiste en generar todos los movimientos de los sujetos. De forma que TODOS lo cruzen en el menor tiempo posible. n 
# Tamaño de la lista debe ser n
'''

def cruzar_puente():
    while True:
        entrada = int(input("Ingrese el número de personas: "))
        try:
            if entrada <= 0:
                print("\nEl número de personas debe ser mayor que cero.")
                continue
            break
        except ValueError:
            print("\nDebe ingresar un número entero válido.")

    tiempos = []
    i = 0
    while i < entrada:
        tiempo = int(input(f"Ingrese el tiempo de la persona {chr(ord('A') + i)}: "))
        try:
            if tiempo <= 0:
                print("\nEl tiempo debe ser un número positivo mayor que cero.")
                continue
            tiempos.append(tiempo)
            i += 1
        except ValueError:
            print("\nDebe ingresar un número entero válido.")
            continue

    # Genera una lista de nombres: ['A', 'B', 'C', ...] usando código ASCII
    # chr(ord('A') + i) convierte 0 en 'A', 1 en 'B', etc.
    nombres = [chr(ord('A') + i) for i in range(entrada)]

    # Une cada nombre con su tiempo usando zip, formando tuplas (nombre, tiempo)
    # Ejemplo: [('A', 1), ('B', 2), ('C', 5), ('D', 8)]
    sujetos = list(zip(nombres, tiempos))
    sujetos.sort(key=lambda x: x[1])  # Ordenar por tiempo (de menor a mayor)

    # 'pasos' almacenará los movimientos realizados en el cruce, para mostrarlos al final
    pasos = []
    total = 0

    # 'izquierda' representa las personas que aún no han cruzado el puente (inician todos aquí)
    izquierda = sujetos.copy()
    # 'derecha' representa las personas que ya cruzaron el puente (inicia vacío)
    derecha = []

    # Este ciclo while implementa la estrategia óptima para el cruce:
    # Mientras queden más de 3 personas en la izquierda, se realizan movimientos en grupos,
    # comparando dos estrategias posibles y eligiendo la de menor tiempo.
    while len(izquierda) > 3:
        # Estrategia: comparar dos opciones y elegir la mejorno e
        # Opción 1: Los dos más rápidos cruzan, el más rápido regresa, los dos más lentos cruzan, el segundo más rápido regresa
        t1 = izquierda[0][1]
        t2 = izquierda[1][1]
        tn_1 = izquierda[-2][1]
        tn = izquierda[-1][1]

        # Caso 1: (t2 + t1 + tn + t2)
        costo1 = t2 + t1 + tn + t2 
        # Caso 2: (tn + t1 + tn_1 + t1)
        costo2 = tn + t1 + tn_1 + t1

        if costo1 < costo2:
            pasos.append(f"{izquierda[0][0]} y {izquierda[1][0]} cruzan ({t2} min)")
            total += t2
            derecha.extend([izquierda[0], izquierda[1]])
            izquierda = izquierda[2:]

            pasos.append(f"{derecha[0][0]} regresa ({t1} min)")
            total += t1
            izquierda.insert(0, derecha[0])
            derecha = derecha[1:]

            pasos.append(f"{izquierda[-2][0]} y {izquierda[-1][0]} cruzan ({tn} min)")
            total += tn
            derecha.extend([izquierda[-2], izquierda[-1]])
            izquierda = izquierda[:-2]

            pasos.append(f"{derecha[0][0]} regresa ({t2} min)")
            total += t2
            izquierda.insert(0, derecha[0])
            derecha = derecha[1:]
        else:
            pasos.append(f"{izquierda[0][0]} y {izquierda[-1][0]} cruzan ({tn} min)")
            total += tn
            derecha.extend([izquierda[0], izquierda[-1]])
            izquierda = izquierda[1:-1]

            pasos.append(f"{derecha[0][0]} regresa ({t1} min)")
            total += t1
            izquierda.insert(0, derecha[0])
            derecha = derecha[1:]

            pasos.append(f"{izquierda[0][0]} y {izquierda[-1][0]} cruzan ({tn_1} min)")
            total += tn_1
            derecha.extend([izquierda[0], izquierda[-1]])
            izquierda = izquierda[1:-1]

            pasos.append(f"{derecha[0][0]} regresa ({t1} min)")
            total += t1
            izquierda.insert(0, derecha[0])
            derecha = derecha[1:]

    # Resolver los últimos 3 o menos
    if len(izquierda) == 3:
        pasos.append(f"{izquierda[0][0]} y {izquierda[1][0]} cruzan ({izquierda[1][1]} min)")
        total += izquierda[1][1]
        pasos.append(f"{izquierda[0][0]} regresa ({izquierda[0][1]} min)")
        total += izquierda[0][1]
        pasos.append(f"{izquierda[0][0]} y {izquierda[2][0]} cruzan ({izquierda[2][1]} min)")
        total += izquierda[2][1]
    elif len(izquierda) == 2:
        pasos.append(f"{izquierda[0][0]} y {izquierda[1][0]} cruzan ({izquierda[1][1]} min)")
        total += izquierda[1][1]
    elif len(izquierda) == 1:
        pasos.append(f"{izquierda[0][0]} cruza solo ({izquierda[0][1]} min)")
        total += izquierda[0][1]

    for paso in pasos:
        print(paso)
    print(f"Tiempo total: {total} minutos")

cruzar_puente()
