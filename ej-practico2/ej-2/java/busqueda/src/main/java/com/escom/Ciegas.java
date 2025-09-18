package com.escom;

import java.util.*;

public class Ciegas {

    private static int TAMANIO;
    private static int[][] laberinto;

    private static final int[] MOV_X = {-1, 1, 0, 0};
    private static final int[] MOV_Y = {0, 0, -1, 1};

    private static Nodo puntoInicio;
    private static Nodo puntoMeta;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        do {
            System.out.print("Ingresa el tamaño del laberinto (mínimo 20): ");
            TAMANIO = sc.nextInt();
            if (TAMANIO < 20) {
                System.out.println("El tamaño mínimo permitido es 20. Intenta de nuevo.");
            }
        } while (TAMANIO < 20);

        laberinto = new int[TAMANIO][TAMANIO];

        System.out.println("Ingresa coordenadas de inicio (fila columna): ");
        puntoInicio = new Nodo(sc.nextInt(), sc.nextInt());

        while (true) {
            System.out.println("Ingresa coordenadas de meta (fila columna): ");
            puntoMeta = new Nodo(sc.nextInt(), sc.nextInt());
            if (!puntoInicio.equals(puntoMeta)) break;
            System.out.println("El inicio y la meta no pueden ser iguales. Ingresa otra vez.");
        }

        inicializarLaberinto();

        System.out.println("¿Cuántos obstáculos quieres colocar?");
        int numObs = sc.nextInt();
        for (int i = 0; i < numObs; i++) {
            System.out.print("Obstáculo " + (i + 1) + " (fila columna): ");
            int fx = sc.nextInt();
            int fy = sc.nextInt();
            if ((fx == puntoInicio.x && fy == puntoInicio.y) ||
                (fx == puntoMeta.x && fy == puntoMeta.y)) {
                System.out.println("No puedes poner obstáculo en inicio/meta.");
            } else if (fx >= 0 && fx < TAMANIO && fy >= 0 && fy < TAMANIO) {
                laberinto[fx][fy] = 1;
            } else {
                System.out.println("Coordenadas inválidas, ignoradas.");
            }
        }

        System.out.println("\n--- Laberinto inicial ---");
        imprimirLaberinto(Collections.emptyList());

        System.out.println("\n--- Resolviendo con BFS ---");
        List<Nodo> caminoBFS = buscarConBFS();
        imprimirResultado(caminoBFS);

        System.out.println("\n--- Resolviendo con DFS ---");
        List<Nodo> caminoDFS = buscarConDFS();
        imprimirResultado(caminoDFS);
    }

    private static void inicializarLaberinto() {
        for (int fila = 0; fila < TAMANIO; fila++) {
            for (int col = 0; col < TAMANIO; col++) {
                laberinto[fila][col] = 0;
            }
        }
    }

    private static List<Nodo> buscarConBFS() {
        Queue<Nodo> cola = new LinkedList<>();
        Map<Nodo, Nodo> predecesores = new HashMap<>();
        Set<Nodo> visitados = new HashSet<>();

        cola.add(puntoInicio);
        visitados.add(puntoInicio);

        while (!cola.isEmpty()) {
            Nodo actual = cola.poll();
            if (actual.equals(puntoMeta)) {
                return reconstruirCamino(predecesores, actual);
            }
            for (Nodo vecino : obtenerVecinos(actual)) {
                if (!visitados.contains(vecino)) {
                    visitados.add(vecino);
                    predecesores.put(vecino, actual);
                    cola.add(vecino);
                }
            }
        }
        return Collections.emptyList();
    }

    private static List<Nodo> buscarConDFS() {
        Stack<Nodo> pila = new Stack<>();
        Map<Nodo, Nodo> predecesores = new HashMap<>();
        Set<Nodo> visitados = new HashSet<>();

        pila.push(puntoInicio);
        visitados.add(puntoInicio);

        while (!pila.isEmpty()) {
            Nodo actual = pila.pop();
            if (actual.equals(puntoMeta)) {
                return reconstruirCamino(predecesores, actual);
            }
            for (Nodo vecino : obtenerVecinos(actual)) {
                if (!visitados.contains(vecino)) {
                    visitados.add(vecino);
                    predecesores.put(vecino, actual);
                    pila.push(vecino);
                }
            }
        }
        return Collections.emptyList();
    }

    private static List<Nodo> obtenerVecinos(Nodo nodo) {
        List<Nodo> listaVecinos = new ArrayList<>();
        for (int i = 0; i < MOV_X.length; i++) {
            int nx = nodo.x + MOV_X[i];
            int ny = nodo.y + MOV_Y[i];
            if (nx >= 0 && ny >= 0 && nx < TAMANIO && ny < TAMANIO && laberinto[nx][ny] == 0) {
                listaVecinos.add(new Nodo(nx, ny));
            }
        }
        return listaVecinos;
    }

    private static List<Nodo> reconstruirCamino(Map<Nodo, Nodo> predecesores, Nodo actual) {
        List<Nodo> camino = new ArrayList<>();
        while (actual != null) {
            camino.add(actual);
            actual = predecesores.get(actual);
        }
        Collections.reverse(camino);
        return camino;
    }

    private static void imprimirResultado(List<Nodo> camino) {
        if (camino.isEmpty()) {
            System.out.println("No se encontró camino.");
        } else {
            System.out.println(" Camino encontrado (" + camino.size() + " pasos):");
            for (Nodo nodo : camino) {
                System.out.print("(" + nodo.x + "," + nodo.y + ") ");
            }
            System.out.println("\n--- Laberinto con camino ---");
            imprimirLaberinto(camino);
        }
    }

    private static void imprimirLaberinto(List<Nodo> camino) {
        char[][] salida = new char[TAMANIO][TAMANIO];

        for (int fila = 0; fila < TAMANIO; fila++) {
            for (int col = 0; col < TAMANIO; col++) {
                salida[fila][col] = (laberinto[fila][col] == 1) ? '#' : '.';
            }
        }

        for (Nodo n : camino) {
            salida[n.x][n.y] = '*';
        }

        salida[puntoInicio.x][puntoInicio.y] = 'E';
        salida[puntoMeta.x][puntoMeta.y] = 'S';

        for (int fila = 0; fila < TAMANIO; fila++) {
            for (int col = 0; col < TAMANIO; col++) {
                System.out.print(salida[fila][col] + " ");
            }
            System.out.println();
        }
    }

    static class Nodo {
        int x, y;
        Nodo(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object obj) {
            if (!(obj instanceof Nodo)) return false;
            Nodo otro = (Nodo) obj;
            return this.x == otro.x && this.y == otro.y;
        }
        @Override public int hashCode() { return Objects.hash(x, y); }
    }
}
