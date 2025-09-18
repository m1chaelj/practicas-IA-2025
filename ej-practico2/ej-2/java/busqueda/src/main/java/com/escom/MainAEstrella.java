package com.escom;

import java.util.*;

public class MainAEstrella {

    private static int tamanioLaberinto;
    private static int[][] matrizLaberinto;

    private static final int[] DESPLAZAMIENTO_X = {-1, 1, 0, 0};
    private static final int[] DESPLAZAMIENTO_Y = {0, 0, -1, 1};

    private static Nodo inicio;
    private static Nodo meta;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        do {
            System.out.print("Ingresa el tamaño del laberinto (mínimo 20): ");
            tamanioLaberinto = sc.nextInt();
            if (tamanioLaberinto < 20) {
                System.out.println("El tamaño mínimo permitido es 20. Intenta de nuevo.");
            }
        } while (tamanioLaberinto < 20);

        matrizLaberinto = new int[tamanioLaberinto][tamanioLaberinto];

        System.out.print("Ingresa coordenadas de inicio (fila columna): ");
        inicio = new Nodo(sc.nextInt(), sc.nextInt());

        while (true) {
            System.out.print("Ingresa coordenadas de meta (fila columna): ");
            meta = new Nodo(sc.nextInt(), sc.nextInt());
            if (!inicio.equals(meta)) break;
            System.out.println("El inicio y la meta no pueden ser iguales. Ingresa otra vez.");
        }

        inicializarLaberinto();

        System.out.print("¿Cuántos obstáculos quieres colocar? ");
        int cantidadObstaculos = sc.nextInt();
        for (int i = 0; i < cantidadObstaculos; i++) {
            System.out.print("Obstáculo " + (i + 1) + " (fila columna): ");
            int filaObs = sc.nextInt();
            int columnaObs = sc.nextInt();
            if ((filaObs == inicio.x && columnaObs == inicio.y) ||
                (filaObs == meta.x && columnaObs == meta.y)) {
                System.out.println("No puedes poner obstáculo en inicio/meta.");
            } else if (filaObs >= 0 && filaObs < tamanioLaberinto && columnaObs >= 0 && columnaObs < tamanioLaberinto) {
                matrizLaberinto[filaObs][columnaObs] = 1;
            } else {
                System.out.println("Coordenadas inválidas, ignoradas.");
            }
        }

        System.out.println("\nLaberinto inicial:");
        imprimirLaberinto(Collections.emptyList());

        System.out.println("\nResolviendo con A*:");
        List<Nodo> caminoEncontrado = buscarConAEstrella();
        imprimirResultado(caminoEncontrado);
    }

    private static void inicializarLaberinto() {
        for (int fila = 0; fila < tamanioLaberinto; fila++) {
            for (int col = 0; col < tamanioLaberinto; col++) {
                matrizLaberinto[fila][col] = 0;
            }
        }
    }

    private static List<Nodo> buscarConAEstrella() {
        PriorityQueue<NodoAEstrella> open = new PriorityQueue<>(Comparator.comparingInt(n -> n.f));
        Map<Nodo, Nodo> predecesores = new HashMap<>();
        Map<Nodo, Integer> gScores = new HashMap<>();

        NodoAEstrella inicioNodo = new NodoAEstrella(inicio, 0, heuristica(inicio, meta));
        open.add(inicioNodo);
        gScores.put(inicio, 0);

        while (!open.isEmpty()) {
            NodoAEstrella actual = open.poll();
            if (actual.nodo.equals(meta)) {
                return reconstruirCamino(predecesores, actual.nodo);
            }

            for (Nodo vecino : obtenerVecinos(actual.nodo)) {
                int costoTentativo = gScores.get(actual.nodo) + 1;
                if (costoTentativo < gScores.getOrDefault(vecino, Integer.MAX_VALUE)) {
                    predecesores.put(vecino, actual.nodo);
                    gScores.put(vecino, costoTentativo);
                    int f = costoTentativo + heuristica(vecino, meta);
                    open.add(new NodoAEstrella(vecino, costoTentativo, f));
                }
            }
        }
        return Collections.emptyList();
    }

    private static int heuristica(Nodo a, Nodo b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y); // Manhattan
    }

    private static List<Nodo> obtenerVecinos(Nodo nodo) {
        List<Nodo> vecinos = new ArrayList<>();
        for (int i = 0; i < DESPLAZAMIENTO_X.length; i++) {
            int nuevaFila = nodo.x + DESPLAZAMIENTO_X[i];
            int nuevaColumna = nodo.y + DESPLAZAMIENTO_Y[i];
            if (nuevaFila >= 0 && nuevaColumna >= 0 && nuevaFila < tamanioLaberinto && nuevaColumna < tamanioLaberinto
                && matrizLaberinto[nuevaFila][nuevaColumna] == 0) {
                vecinos.add(new Nodo(nuevaFila, nuevaColumna));
            }
        }
        return vecinos;
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
            System.out.println("Camino encontrado (" + camino.size() + " pasos):");
            for (Nodo nodo : camino) {
                System.out.print("(" + nodo.x + "," + nodo.y + ") ");
            }
            System.out.println("\nLaberinto con camino:");
            imprimirLaberinto(camino);
        }
    }

    private static void imprimirLaberinto(List<Nodo> camino) {
        char[][] salida = new char[tamanioLaberinto][tamanioLaberinto];

        for (int fila = 0; fila < tamanioLaberinto; fila++) {
            for (int col = 0; col < tamanioLaberinto; col++) {
                salida[fila][col] = (matrizLaberinto[fila][col] == 1) ? '#' : '.';
            }
        }

        for (Nodo n : camino) {
            salida[n.x][n.y] = '*';
        }

        salida[inicio.x][inicio.y] = 'E';
        salida[meta.x][meta.y] = 'S';

        for (int fila = 0; fila < tamanioLaberinto; fila++) {
            for (int col = 0; col < tamanioLaberinto; col++) {
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

    static class NodoAEstrella {
        Nodo nodo;
        int g; // costo desde inicio
        int f; // g + heuristica
        NodoAEstrella(Nodo nodo, int g, int f) { this.nodo = nodo; this.g = g; this.f = f; }
    }
}
