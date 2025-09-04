package com.escom;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Scanner;
import java.util.logging.Logger;

public class Main {
    private static final Logger log = Logger.getLogger(Main.class.getName());

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        List<Integer> tiemposPersonas = new ArrayList<>();
        System.out.println("Ingrese los tiempos de cada persona:");

        while (scanner.hasNextInt()) {
            int tiempo = scanner.nextInt();
            if (tiempo <= 0) {
                log.warning("El tiempo debe ser positivo.");
                continue;
            }
            tiemposPersonas.add(tiempo);
        }

        if (tiemposPersonas.isEmpty()) {
            log.warning("No se ingresaron tiempos.");
            return;
        }

        Collections.sort(tiemposPersonas);

        int totalTiempo = resolverPuente(tiemposPersonas);
        System.out.println("Tiempo total mínimo: " + totalTiempo + " minutos");
    }

    private static int resolverPuente(List<Integer> tiempos) {
        List<String> pasos = new ArrayList<>();
        int total = 0;

        boolean todosIguales = tiempos.getFirst().equals(tiempos.getLast());
        if (todosIguales) {
            int cantidadPersonas = tiempos.size();
            int tiempoComun = tiempos.getFirst();

            if (cantidadPersonas == 1) {
                total = tiempoComun;
            } else if (cantidadPersonas == 2) {
                total = tiempoComun;
            } else {
                total = (2 * cantidadPersonas - 3) * tiempoComun;
            }

            log.info("Todos los tiempos son iguales, se usa fórmula directa");
            return total;
        }

        while (tiempos.size() > 3) {
            int masRapido = tiempos.getFirst();
            int segundoMasRapido = tiempos.get(1);
            int segundoMasLento = tiempos.get(tiempos.size() - 2);
            int masLento = tiempos.getLast();

            int tiempoEstrategiaA = segundoMasRapido + masRapido + masLento + segundoMasRapido;
            int tiempoEstrategiaB = masLento + masRapido + segundoMasLento + masRapido;

            if (tiempoEstrategiaA < tiempoEstrategiaB) {
                total += tiempoEstrategiaA;
                pasos.add(masRapido + " y " + segundoMasRapido + " cruzan -> (" + segundoMasRapido + ")");
                pasos.add(masRapido + " regresa <- (" + masRapido + ")");
                pasos.add(segundoMasLento + " y " + masLento + " cruzan -> (" + masLento + ")");
                pasos.add(segundoMasRapido + " regresa <- (" + segundoMasRapido + ")");
            } else {
                total += tiempoEstrategiaB;
                pasos.add(masRapido + " y " + masLento + " cruzan -> (" + masLento + ")");
                pasos.add(masRapido + " regresa <- (" + masRapido + ")");
                pasos.add(masRapido + " y " + segundoMasLento + " cruzan -> (" + segundoMasLento + ")");
                pasos.add(masRapido + " regresa <- (" + masRapido + ")");
            }

            tiempos.removeLast();
            tiempos.removeLast();
        }

        if (tiempos.size() == 3) {
            total += tiempos.getFirst() + tiempos.get(1) + tiempos.get(2);
            pasos.add(tiempos.getFirst() + " y " + tiempos.get(1) + " cruzan -> (" + tiempos.get(1) + ")");
            pasos.add(tiempos.getFirst() + " regresa <- (" + tiempos.getFirst() + ")");
            pasos.add(tiempos.getFirst() + " y " + tiempos.get(2) + " cruzan -> (" + tiempos.get(2) + ")");
        } else if (tiempos.size() == 2) {
            total += tiempos.get(1);
            pasos.add(tiempos.getFirst() + " y " + tiempos.get(1) + " cruzan -> (" + tiempos.get(1) + ")");
        } else if (tiempos.size() == 1) {
            total += tiempos.getFirst();
            pasos.add(tiempos.getFirst() + " cruza solo.");
        }

        System.out.println("Estrategia de cruces:");
        for (String paso : pasos) {
            System.out.println(paso);
        }

        return total;
    }
}
