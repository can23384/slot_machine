import csv
import json
import statistics
from pathlib import Path

from simulador import simulador_tragamonedas
from analisis import resumir, guardar_grafica


def main():

    n = 5
    p = 0.25
    cantidad_tiradas = 100_000
    repeticiones = 5
    semilla = 42
    costo_tirada = 1.0


    premios = {0: 0, 1: 0, 2: 1, 3: 3, 4: 10, 5: 50}

    carpeta = Path(__file__).resolve().parent / "resultados"
    carpeta.mkdir(exist_ok=True)

    simulador = simulador_tragamonedas(n, p, premios, costo_tirada, semilla)
    resumenes = {}
    tiempos = {"bernoulli": [], "inversa": []}

    # Calentamiento fuera de las mediciones que se reportan.
    for metodo in tiempos:
        simulador.ejecutar(1000, metodo)

    for repeticion in range(repeticiones):
        # Alternar el orden reduce el sesgo por ejecutar siempre uno primero.
        metodos = ["bernoulli", "inversa"]
        if repeticion % 2 == 1:
            metodos.reverse()

        for metodo in metodos:
            frecuencias, tiempo = simulador.ejecutar(cantidad_tiradas, metodo, repeticion)
            tiempos[metodo].append(tiempo)

            # Se conserva la primera corrida de cada metodo para el analisis.
            # Las demas sirven para medir la variacion del tiempo de ejecucion.
            if repeticion == 0:
                resumenes[metodo] = resumir(frecuencias, simulador.probabilidades, premios, costo_tirada)
                simulador.guardar_tiradas(carpeta / f"tiradas_{metodo}.csv")

    print(f"Binomial(n={n}, p={p}) | {cantidad_tiradas:,} tiradas por corrida")
    print(f"Media teorica: {n*p:.6f} | Varianza teorica: {n*p*(1-p):.6f}")
    print(f"Preparacion de probabilidades y acumuladas: {simulador.tiempo_preparacion:.8f} s")

    for metodo, resumen in resumenes.items():
        resumen["tiempos_segundos"] = tiempos[metodo]
        resumen["tiempo_mediano_segundos"] = statistics.median(tiempos[metodo])
        print(f"\nMetodo: {metodo}")
        print(f"Media: {resumen['media']:.6f} | Varianza: {resumen['varianza']:.6f}")
        print(f"Tiempo mediano ({repeticiones} corridas): {resumen['tiempo_mediano_segundos']:.6f} s")
        print(f"Premio promedio: {resumen['premio_promedio']:.6f}")
        print(f"Ganancia neta promedio del jugador: {resumen['ganancia_promedio_jugador']:.6f}")
        prueba = resumen["chi_cuadrado"]
        if prueba["aplicable"]:
            conclusion = "Se rechaza H0" if prueba["rechaza_al_5_por_ciento"] else "No se rechaza H0"
            print(f"Chi-cuadrado: {prueba['estadistico']:.4f} | gl={prueba['grados_libertad']} | p-valor={prueba['valor_p']:.6f}")
            print(f"{conclusion} al 5% (H0: X sigue la binomial especificada).")
        else:
            print("Chi-cuadrado no aplicable: " + prueba["motivo"])

    with open(carpeta / "frecuencias.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["x", "probabilidad_teorica", "esperados", "bernoulli", "inversa"])
        for x, probabilidad in enumerate(simulador.probabilidades):
            escritor.writerow([x, probabilidad, cantidad_tiradas * probabilidad,
                               resumenes["bernoulli"]["frecuencias"][x],
                               resumenes["inversa"]["frecuencias"][x]])

    informe = {
        "parametros": {"n": n, "p": p, "tiradas": cantidad_tiradas, "semilla": semilla,
                       "repeticiones": repeticiones, "costo": costo_tirada, "premios": premios},
        "media_teorica": n * p,
        "varianza_teorica": n * p * (1 - p),
        "tiempo_preparacion_segundos": simulador.tiempo_preparacion,
        "metodos": resumenes,
    }
    (carpeta / "resumen.json").write_text(json.dumps(informe, indent=4, ensure_ascii=False), encoding="utf-8")
    guardar_grafica(carpeta / "comparacion.svg", simulador.probabilidades, resumenes)
    print(f"\nResultados guardados en: {carpeta}")


if __name__ == "__main__":
    main()
