Las técnicas que se usaran entraran en la categoría de búsqueda, ya que busca encontrar una solución valida.

Solución de problemas por fuerza bruta:
- Datos
- Información

Propuestas: Estructuras de datos.
Mejor solución: Grafos y arboles.

/////////// Busqueda en profundidad ////////////
pop(A)
visitados = {A}
frontera = [D,C,B]

pop(B)
visitados = {A,B}
Hijos de B: E y F
push inverso: F y E
frontera = [D,C,F,E]

nodo_inicial = estado inicial
nodo_frontera = Pila FIFO
nodos_visitados = Lista
almacenar nodo_inicial en nodos_frontera
mientras nodos_frontera no vacio:
    nodo_actual = extraer un nodo de nodos_frontera
    si nodo_actual == solucion:
        salir con solucion

introducir nodo_actual en nodos_visitados por cada operador:
    nodo_hijo = operador(nodo_actual)
    si nodo_hijo no en nodos_visitados ni nodos_frontera:
        introducir nodo_hijo en nodos_frontera


      A
    / | \
   B  C  D
  / \    / \
 E   F  G   H
 |          |
 I          J

 Complejidad: Temporal O(b^d)


/////////// Busqueda primero en Amplitud (BFS) ////////////
Primero se visita el nodo raiz.
Seguidamente se visitan todos sus hijos.
Para cada hijo en el paso anterior se visitan todos sus hijos, y asi sucesivamente.

Se implementa usando una cola en vez de una pila.
Pila -> LIFO. Last In, First out.
Cola -> FIFO. First In, First out.


nodo_inicial = estado inicial
nodo_frontera = Pila LIFO
nodos_visitados = Lista
almacenar nodo_inicial en nodos_frontera
mientras nodos_frontera no vacio:
    nodo_actual = extraer un nodo de nodos_frontera
    si nodo_actual == solucion:
        salir con solucion

introducir nodo_actual en nodos_visitados por cada operador:
    nodo_hijo = operador(nodo_actual)
    si nodo_hijo no en nodos_visitados ni nodos_frontera:
        introducir nodo_hijo en nodos_frontera


Complejidad: Espacial O(b^d)
Requiere mas memoria.


      A
    / | \
   B  C  D
  / \    / \
 E   F  G   H
 |          |
 I          J

Estado inicial es A
frontera = [A]
visitados = []

it 1:
dequeue A de frontera = []
visitados = [A]
Hijos de A: B, C y D (se agregan en orden normal)
frontera = [B, C, D]

it 2:
dequeue B de frontera = [C, D]
visitados = [A, B]
Hijos de B: E y F (orden normal)
frontera = [C, D, E, F]

it 3:
dequeue C de frontera = [D, E, F]
visitados = [A, B, C]
C no tiene hijos

it 4:
dequeue D de frontera = [E, F]
visitados = [A, B, C, D]
Hijos de D: G y H (orden normal)
frontera = [E, F, G, H]

it 5:
dequeue E de frontera = [F, G, H]
visitados = [A, B, C, D, E]
Hijo de E: I
frontera = [F, G, H, I]