import csv
import math
import random
import time

from evento import Evento
from generadores import (
    validar_parametros,
    probabilidades_binomiales,
    crear_acumuladas,
    generar_binomial_bernoulli,
    generar_binomial_inversa,
)


class simulador_tragamonedas:

    def __init__(self, n, p, premios, costo=1.0, semilla=42):
        validar_parametros(n, p)

        if not math.isfinite(costo) or costo <= 0:
            raise ValueError("El costo debe ser positivo y finito.")

        for exitos, premio in premios.items():
            if not isinstance(exitos, int) or not 0 <= exitos <= n:
                raise ValueError("Las claves de premios deben estar entre 0 y n.")
            if not math.isfinite(premio) or premio < 0:
                raise ValueError("Los premios deben ser finitos y no negativos.")

        self.n = n
        self.p = p
        self.premios = dict(premios)
        self.costo = costo
        self.semilla = semilla
        self.eventos = []

        inicio = time.perf_counter()
        self.probabilidades = probabilidades_binomiales(n, p)
        self.acumuladas = crear_acumuladas(self.probabilidades)
        self.tiempo_preparacion = time.perf_counter() - inicio

    def ejecutar(self, cantidad, metodo, repeticion=0):

        if not isinstance(cantidad, int) or cantidad < 1:
            raise ValueError("La cantidad de tiradas debe ser un entero positivo.")
        if metodo not in ("bernoulli", "inversa"):
            raise ValueError("Metodo desconocido.")

        # Semillas distintas por metodo y repeticion, pero reproducibles.
        desplazamiento = 0 if metodo == "bernoulli" else 1
        rango = random.Random(self.semilla + 2 * repeticion + desplazamiento)

        if metodo == "bernoulli":
            generar = lambda: generar_binomial_bernoulli(self.n, self.p, rango)
        else:
            generar = lambda: generar_binomial_inversa(self.acumuladas, rango)

        # Solo se cronometra la generacion y el almacenamiento de X.
        # CSV, premios, pruebas y graficas quedan fuera de esta medicion.
        inicio = time.perf_counter()
        resultados = [generar() for tirada in range(cantidad)]
        tiempo_generacion = time.perf_counter() - inicio

        self.eventos = []
        frecuencias = [0] * (self.n + 1)

        for numero, exitos in enumerate(resultados, start=1):
            premio = self.premios.get(exitos, 0.0)
            self.eventos.append(Evento(numero, exitos, premio, self.costo))
            frecuencias[exitos] += 1

        return frecuencias, tiempo_generacion

    def guardar_tiradas(self, ruta):

        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["tirada", "simbolos_ganadores", "premio", "ganancia_jugador"])

            for evento in self.eventos:
                escritor.writerow([
                    evento.numero, evento.exitos, evento.premio, evento.ganancia
                ])
