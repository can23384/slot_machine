import math


def validar_parametros(n, p):

    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n debe ser un entero positivo.")

    if not math.isfinite(p) or p < 0 or p > 1:
        raise ValueError("p debe estar entre 0 y 1.")


def probabilidades_binomiales(n, p):

    validar_parametros(n, p)

    if p == 0:
        return [1.0] + [0.0] * n

    if p == 1:
        return [0.0] * n + [1.0]

    probabilidades = []

    for x in range(n + 1):
        # Equivale a C(n,x) * p**x * (1-p)**(n-x).
        # Los logaritmos evitan calcular factoriales enormes.
        log_probabilidad = (
            math.lgamma(n + 1)
            - math.lgamma(x + 1)
            - math.lgamma(n - x + 1)
            + x * math.log(p)
            + (n - x) * math.log1p(-p)
        )
        probabilidades.append(math.exp(log_probabilidad))

    total = sum(probabilidades)
    return [valor / total for valor in probabilidades]


def crear_acumuladas(probabilidades):

    acumuladas = []
    total = 0.0

    for probabilidad in probabilidades:
        total += probabilidad
        acumuladas.append(total)

    acumuladas[-1] = 1.0
    return acumuladas


def generar_binomial_bernoulli(n, p, rango):

    exitos = 0

    for rodillo in range(n):
        u = rango.random()

        if u < p:
            exitos += 1

    return exitos


def generar_binomial_inversa(acumuladas, rango):

    u = rango.random()

    for x, probabilidad_acumulada in enumerate(acumuladas):
        if u < probabilidad_acumulada:
            return x

    raise ValueError("La tabla acumulada debe terminar en 1.")
