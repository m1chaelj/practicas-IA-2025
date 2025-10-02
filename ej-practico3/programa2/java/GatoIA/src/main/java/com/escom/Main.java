package com.escom;

import java.util.*;

public class Main {
    static final int N = 4;
    static final char JUGADOR = 'X';
    static final char IA = 'O';
    static final char VACIO = '.';

    public static void main(String[] args) {
        char[][] tablero = new char[N][N];
        for (int i = 0; i < N; i++) Arrays.fill(tablero[i], VACIO);

        Scanner sc = new Scanner(System.in);
        Random random = new Random();

        System.out.println("¿Quién empieza primero? (1 = Tú, 2 = IA): ");
        int opcion = sc.nextInt();
        boolean turnoJugador = opcion == 1;

        while (true) {
            imprimir(tablero);
            if (evaluar(tablero) != 0 || !quedanMovimientos(tablero)) break;

            if (turnoJugador) {
                System.out.println("Tu turno (fila columna): ");
                int f = sc.nextInt();
                int c = sc.nextInt();
                if (f >= 0 && f < N && c >= 0 && c < N && tablero[f][c] == VACIO) {
                    tablero[f][c] = JUGADOR;
                } else {
                    System.out.println("Movimiento inválido.");
                    continue;
                }
            } else {
                System.out.println("Turno de la IA...");

                if (tableroVacio(tablero)) {
                    movimientoAleatorio(tablero, random);
                } else {
                    int[] mejor = mejorMovimiento(tablero);
                    tablero[mejor[0]][mejor[1]] = IA;
                }
            }

            turnoJugador = !turnoJugador;
        }

        imprimir(tablero);
        int resultado = evaluar(tablero);
        if (resultado == 10) System.out.println("¡Ganó la IA!");
        else if (resultado == -10) System.out.println("¡Ganaste!");
        else System.out.println("Empate.");
    }

    static void movimientoAleatorio(char[][] t, Random rand) {
        List<int[]> vacios = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (t[i][j] == VACIO) {
                    vacios.add(new int[]{i, j});
                }
            }
        }
        if (!vacios.isEmpty()) {
            int[] mov = vacios.get(rand.nextInt(vacios.size()));
            t[mov[0]][mov[1]] = IA;
        }
    }

    static boolean tableroVacio(char[][] t) {
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                if (t[i][j] != VACIO) return false;
        return true;
    }

    static int evaluar(char[][] t) {
        for (int i = 0; i < N; i++) {
            if (t[i][0] != VACIO && iguales(t[i]))
                return (t[i][0] == IA) ? 10 : -10;

            char[] col = {t[0][i], t[1][i], t[2][i], t[3][i]};
            if (col[0] != VACIO && iguales(col))
                return (col[0] == IA) ? 10 : -10;
        }

        char[] d1 = {t[0][0], t[1][1], t[2][2], t[3][3]};
        if (d1[0] != VACIO && iguales(d1))
            return (d1[0] == IA) ? 10 : -10;

        char[] d2 = {t[0][3], t[1][2], t[2][1], t[3][0]};
        if (d2[0] != VACIO && iguales(d2))
            return (d2[0] == IA) ? 10 : -10;

        return 0;
    }

    static boolean iguales(char[] arr) {
        for (int i = 1; i < arr.length; i++)
            if (arr[i] != arr[0]) return false;
        return true;
    }

    static boolean quedanMovimientos(char[][] t) {
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                if (t[i][j] == VACIO) return true;
        return false;
    }

    static int minimax(char[][] t, int profundidad, boolean max, int alpha, int beta) {
        int score = evaluar(t);

        if (score == 10 || score == -10) return score;
        if (!quedanMovimientos(t)) return 0;

        if (max) {
            int mejor = Integer.MIN_VALUE;
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) {
                    if (t[i][j] == VACIO) {
                        t[i][j] = IA;
                        mejor = Math.max(mejor, minimax(t, profundidad + 1, false, alpha, beta));
                        t[i][j] = VACIO;
                        alpha = Math.max(alpha, mejor);
                        if (beta <= alpha) return mejor;
                    }
                }
            }
            return mejor;
        } else {
            int mejor = Integer.MAX_VALUE;
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) {
                    if (t[i][j] == VACIO) {
                        t[i][j] = JUGADOR;
                        mejor = Math.min(mejor, minimax(t, profundidad + 1, true, alpha, beta));
                        t[i][j] = VACIO;
                        beta = Math.min(beta, mejor);
                        if (beta <= alpha) return mejor;
                    }
                }
            }
            return mejor;
        }
    }

    static int[] mejorMovimiento(char[][] t) {
        int mejorVal = Integer.MIN_VALUE;
        int[] mejorMov = {-1, -1};

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (t[i][j] == VACIO) {
                    t[i][j] = IA;
                    int movVal = minimax(t, 0, false, Integer.MIN_VALUE, Integer.MAX_VALUE);
                    t[i][j] = VACIO;

                    if (movVal > mejorVal) {
                        mejorMov[0] = i;
                        mejorMov[1] = j;
                        mejorVal = movVal;
                    }
                }
            }
        }
        return mejorMov;
    }

    static void imprimir(char[][] t) {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) System.out.print(t[i][j] + " ");
            System.out.println();
        }
        System.out.println();
    }
}
