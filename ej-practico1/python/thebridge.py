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
        try:
            entrada = int(input("Ingrese el número de personas: "))
            if entrada <= 0:
                print("\nEl número de personas debe ser mayor que cero.")
                continue
            break
        except ValueError:
            print("\nDebe ingresar un número entero válido.")

    tiempos = []
    i = 0
    while i < entrada:
        try:
            tiempo = int(input(f"Ingrese el tiempo de la persona {chr(ord('A') + i)}: "))
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

    # Crea una lista con la letra y tiempo, tipo par: valor
    tiempos_map = {n: t for n, t in sujetos}

    # Orilla izquierda: todos al inicio, ordenados por tiempo ascendente
    izquierda = sorted(sujetos, key=lambda x: x[1])  
    pasos = []
    total = 0

    # Permite eliminar elementos de la lista original izquierda  con nonlocal
    def quitar_de_izquierda(*nombres_quitar):
        nonlocal izquierda
        nombres_quitar = set(nombres_quitar)
        izquierda = [p for p in izquierda if p[0] not in nombres_quitar]
    
    # Permite agregar elementos de la lista original izquierda con nonlocal
    def agregar_a_izquierda(*nombres_agregar):
        nonlocal izquierda
        izquierda.extend([(n, tiempos_map[n]) for n in nombres_agregar])
        izquierda.sort(key=lambda x: x[1])

    while len(izquierda) > 3:
        a, ta = izquierda[0][0], izquierda[0][1]      # más rápido
        b, tb = izquierda[1][0], izquierda[1][1]      # segundo más rápido
        y, ty = izquierda[-2][0], izquierda[-2][1]    # segundo más lento
        z, tz = izquierda[-1][0], izquierda[-1][1]    # más lento

        # Dos opciones clásicas:
        # Opción 1 (a+b cruzan, a regresa, y+z cruzan, b regresa)
        costo1 = tb + ta + tz + tb
        # Opción 2 (a+z cruzan, a regresa, a+y cruzan, a regresa)
        costo2 = tz + ta + ty + ta

        if costo1 <= costo2:
            # a y b cruzan
            pasos.append(f"{a} y {b} cruzan ({tb} min)")
            total += tb
            quitar_de_izquierda(a, b)

            # a regresa
            pasos.append(f"{a} regresa ({ta} min)")
            total += ta
            agregar_a_izquierda(a)

            # y y z cruzan
            # Releer extremos por si el orden cambió al reinsertar
            y, ty = izquierda[-2][0], izquierda[-2][1]
            z, tz = izquierda[-1][0], izquierda[-1][1]
            pasos.append(f"{y} y {z} cruzan ({tz} min)")
            total += tz
            quitar_de_izquierda(y, z)

            # b regresa
            pasos.append(f"{b} regresa ({tb} min)")
            total += tb
            agregar_a_izquierda(b)

        else:
            # a y z cruzan
            pasos.append(f"{a} y {z} cruzan ({tz} min)")
            total += tz
            quitar_de_izquierda(a, z)

            # a regresa
            pasos.append(f"{a} regresa ({ta} min)")
            total += ta
            agregar_a_izquierda(a)

            # a y y cruzan
            # Releer y (segundo más lento actual)
            y, ty = izquierda[-1][0], izquierda[-1][1]  # tras quitar z, y pasa a ser el más lento actual
            pasos.append(f"{a} y {y} cruzan ({ty} min)")
            total += ty
            quitar_de_izquierda(a, y)

            # a regresa
            pasos.append(f"{a} regresa ({ta} min)")
            total += ta
            agregar_a_izquierda(a)

    if len(izquierda) == 3:
        izquierda.sort(key=lambda x: x[1])
        p1, t1 = izquierda[0]
        p2, t2 = izquierda[1]
        p3, t3 = izquierda[2]

        # p1+p2 cruzan
        pasos.append(f"{p1} y {p2} cruzan ({max(t1, t2)} min)")
        total += max(t1, t2)

        # p1 regresa
        pasos.append(f"{p1} regresa ({t1} min)")
        total += t1

        # p1+p3 cruzan
        pasos.append(f"{p1} y {p3} cruzan ({max(t1, t3)} min)")
        total += max(t1, t3)

        izquierda.clear()  # ya cruzaron los 3

    elif len(izquierda) == 2:
        p1, t1 = izquierda[0]
        p2, t2 = izquierda[1]
        pasos.append(f"{p1} y {p2} cruzan ({max(t1, t2)} min)")
        total += max(t1, t2)
        izquierda.clear()

    elif len(izquierda) == 1:
        p1, t1 = izquierda[0]
        pasos.append(f"{p1} cruza solo ({t1} min)")
        total += t1
        izquierda.clear()

    for paso in pasos:
        print(paso)
    print(f"Tiempo total: {total} minutos")


cruzar_puente()
