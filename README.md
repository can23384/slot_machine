# Proyecto 1

Requiere Python 3.9 o superior. No necesita instalar paquetes externos.

Desde esta carpeta ejecutar:

```console
python main.py
```

## Archivos

- `main.py`: parametros, ejecucion de ambos metodos y comparacion.
- `generadores.py`: suma de Bernoulli, transformada inversa y probabilidades teoricas.
- `evento.py`: guarda el resultado de una tirada.
- `simulador.py`: clase de la maquina y exportacion de tiradas.
- `analisis.py`: estadisticas, prueba chi-cuadrado y grafica SVG.

En `main.py` pueden cambiar n, p, cantidad de tiradas, repeticiones, semilla, costo y premios. Si cambian n, adapten las claves de premios: deben estar entre 0 y n. Las cantidades sin premio definido pagan cero.

## Modelo y supuestos

Cada tirada tiene n rodillos independientes, con igual probabilidad p de exito. Las tiradas tambien se modelan independientes. X cuenta exitos: X ~ Binomial(n,p), E[X]=np, Var(X)=np(1-p). La simulacion representa una maquina simplificada; los premios dependen solamente del numero de exitos, no de sus posiciones. No representa rodillos comerciales ni incluye animacion.

Bernoulli consume n uniformes por tirada. Inversa consume uno y recorre la tabla acumulada hasta encontrar el primer F(x)>U. Ambos algoritmos se implementan explicitamente; `random.Random` solo suministra uniformes seudoaleatorios. En este codigo ambos recorridos tienen costo O(n) en el peor caso. La inversa ademas necesita preparar una tabla O(n), que se reutiliza. Usar un uniforme no implica automaticamente que toda la operacion tenga costo constante.

Se usan semillas reproducibles diferentes por metodo y repeticion. Esto no demuestra independencia de los flujos seudoaleatorios. No se requiere un proceso de Poisson porque el modelo no incluye llegadas ni tiempos entre eventos.

## Validacion

Se comparan frecuencias relativas, media, varianza empirica (divisor N) y error maximo de las frecuencias frente a las probabilidades teoricas. La prueba chi-cuadrado agrupa categorias consecutivas hasta reunir al menos cinco observaciones esperadas por grupo y fusiona el remanente con el grupo anterior. Los grupos quedan registrados en `resumen.json`.

Los grados de libertad son numero de grupos menos uno porque n y p se fijan antes de simular. Si quedan menos de dos grupos, la prueba no se aplica. Para p=0 o p=1 la distribucion es determinista y no corresponde esta prueba. El p-valor se calcula con la funcion de supervivencia chi-cuadrado mediante recurrencias de la gamma incompleta, sin bibliotecas externas.

Un p-valor >= 0.05 significa que no hay evidencia suficiente para rechazar el ajuste; no prueba que el generador sea perfecto. Incluso un generador correcto puede producir un rechazo ocasional. La prueba de frecuencias tampoco demuestra independencia entre tiradas. No deben elegir semillas para obtener resultados favorables.

## Comparacion de rendimiento

Se hace un calentamiento y cinco corridas por metodo, alternando su orden. Se reportan los tiempos individuales y la mediana. La medicion incluye generacion y creacion de la lista de X; excluye premios, CSV, validacion y graficas. La preparacion de probabilidades y acumuladas se reporta por separado. Los tiempos dependen del equipo y su carga.

Las estadisticas y CSV usan solamente la primera corrida de cada metodo, no una mezcla de las cinco. Las otras cuatro sirven para comparar tiempos.

## Resultados

La carpeta `resultados` se crea al ejecutar. Una nueva ejecucion reemplaza los archivos anteriores:

- `tiradas_bernoulli.csv` y `tiradas_inversa.csv`: cada tirada, exitos, premio bruto y ganancia neta del jugador.
- `frecuencias.csv`: frecuencias observadas y teoricas.
- `resumen.json`: configuracion, estadisticas, tiempos y prueba de ajuste.
- `comparacion.svg`: grafica de ambas distribuciones empiricas y la teorica; abrir en un navegador.

Los premios y costos son creditos ficticios. Con la configuracion de ejemplo, el premio esperado es 0.72265625 creditos y la ganancia neta esperada del jugador es -0.27734375 por tirada. La tabla es ilustrativa, no un requisito del proyecto.

Este codigo cubre implementacion, validacion y resultados visuales. El grupo debe desarrollar el informe y la presentacion, justificar sus supuestos y explicar los resultados.

## Integrantes

- Ingrid Nina Alessandra Nájera Marakovits, 231088
- Eliazar José Pablo Canastuj Matías, 23384
- Diego Alejandro Ramírez Velásquez, 23601
- Nelson Estuardo Escalante Sánchez, 22046
