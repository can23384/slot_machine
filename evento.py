class Evento:

    def __init__(self, numero, exitos, premio, costo):
        self.numero = numero
        self.exitos = exitos
        self.premio = premio
        self.ganancia = premio - costo
