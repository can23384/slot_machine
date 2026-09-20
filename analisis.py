import math


def supervivencia_chi_cuadrado(valor, grados):
    """P(Chi^2 >= valor), para grados de libertad enteros positivos.

    Usa Q(a+1,z) = Q(a,z) + z**a * exp(-z) / Gamma(a+1).
    Las bases son Q(1,z)=exp(-z) y Q(1/2,z)=erfc(sqrt(z)).
    """
    if grados < 1 or valor < 0:
        raise ValueError("Estadistico o grados de libertad invalidos.")
    if valor == 0:
        return 1.0

    z = valor / 2

    if grados % 2 == 0:
        a = 1.0
        resultado = math.exp(-z)
    else:
        a = 0.5
        resultado = math.erfc(math.sqrt(z))

    while a < grados / 2:
        resultado += math.exp(a * math.log(z) - z - math.lgamma(a + 1))
        a += 1

    return min(1.0, max(0.0, resultado))


def validar_chi_cuadrado(frecuencias, probabilidades):

    cantidad = sum(frecuencias)
    grupos = []
    observados = 0
    esperados = 0.0
    valores = []

    for x, probabilidad in enumerate(probabilidades):
        if probabilidad == 0:
            if frecuencias[x] > 0:
                return {"aplicable": False, "motivo": "Se observo un resultado de probabilidad cero."}
            continue

        valores.append(x)
        observados += frecuencias[x]
        esperados += cantidad * probabilidad

        if esperados >= 5:
            grupos.append([valores, observados, esperados])
            valores, observados, esperados = [], 0, 0.0

    if valores:
        if grupos:
            grupos[-1][0].extend(valores)
            grupos[-1][1] += observados
            grupos[-1][2] += esperados
        else:
            grupos.append([valores, observados, esperados])

    if len(grupos) < 2:
        return {"aplicable": False, "motivo": "No hay dos grupos con frecuencia esperada >= 5."}

    estadistico = sum((o - e) ** 2 / e for valores, o, e in grupos)
    # n y p son fijados previamente, no estimados con estas muestras.
    grados = len(grupos) - 1
    valor_p = supervivencia_chi_cuadrado(estadistico, grados)

    return {
        "aplicable": True,
        "grupos": grupos,
        "estadistico": estadistico,
        "grados_libertad": grados,
        "valor_p": valor_p,
        "rechaza_al_5_por_ciento": valor_p < 0.05,
    }


def resumir(frecuencias, probabilidades, premios, costo):

    cantidad = sum(frecuencias)
    relativas = [f / cantidad for f in frecuencias]
    media = sum(x * f for x, f in enumerate(relativas))
    # Varianza empirica con divisor N; no es el estimador insesgado N-1.
    varianza = sum((x - media) ** 2 * f for x, f in enumerate(relativas))
    premio_medio = sum(premios.get(x, 0) * f for x, f in enumerate(relativas))
    premio_teorico = sum(premios.get(x, 0) * p for x, p in enumerate(probabilidades))

    return {
        "tiradas": cantidad,
        "frecuencias": frecuencias,
        "frecuencias_relativas": relativas,
        "media": media,
        "varianza": varianza,
        "error_maximo_frecuencias": max(abs(f - p) for f, p in zip(relativas, probabilidades)),
        "premio_promedio": premio_medio,
        "premio_teorico": premio_teorico,
        "ganancia_promedio_jugador": premio_medio - costo,
        "ganancia_teorica_jugador": premio_teorico - costo,
        "retorno_jugador": premio_medio / costo,
        "chi_cuadrado": validar_chi_cuadrado(frecuencias, probabilidades),
    }


def guardar_grafica(ruta, probabilidades, resumenes):
    """Grafica SVG que puede abrirse directamente en un navegador."""
    series = [probabilidades] + [resumenes[m]["frecuencias_relativas"] for m in ("bernoulli", "inversa")]
    colores = ["#475569", "#2563eb", "#ea580c"]
    ancho = max(800, len(probabilidades) * 100 + 100)
    escala = max(max(serie) for serie in series) * 1.15
    paso = (ancho - 100) / len(probabilidades)
    barras = []

    for i in range(6):
        y = 420 - i * 60
        barras.append(f'<path d="M70 {y} H{ancho-30}" stroke="#e2e8f0"/>')
        barras.append(f'<text x="60" y="{y+4}" text-anchor="end">{escala*i/5:.2f}</text>')

    for x in range(len(probabilidades)):
        centro = 70 + paso * (x + 0.5)
        for indice, serie in enumerate(series):
            alto = 300 * serie[x] / escala
            izquierda = centro + (indice - 1.5) * paso * 0.22
            barras.append(f'<rect x="{izquierda}" y="{420-alto}" width="{paso*0.2}" height="{alto}" fill="{colores[indice]}"/>')
        barras.append(f'<text x="{centro}" y="445" text-anchor="middle">{x}</text>')

    for indice, nombre in enumerate(["Binomial teorica", "Suma de Bernoulli", "Transformada inversa"]):
        x = 70 + indice * 240
        barras.append(f'<rect x="{x}" y="65" width="14" height="14" fill="{colores[indice]}"/>')
        barras.append(f'<text x="{x+22}" y="77">{nombre}</text>')

    contenido = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="500" viewBox="0 0 {ancho} 500">'
        '<rect width="100%" height="100%" fill="white"/>'
        '<g font-family="Arial, sans-serif" font-size="13" fill="#0f172a">'
        '<text x="70" y="35" font-size="22">Frecuencias relativas de simbolos ganadores</text>'
        + ''.join(barras)
        + f'<text x="{ancho/2}" y="480" text-anchor="middle">Cantidad de simbolos ganadores (X)</text></g></svg>'
    )
    ruta.write_text(contenido, encoding="utf-8")
