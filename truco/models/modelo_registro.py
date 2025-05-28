import pandas as pd

class ModeloRegistro:
    def __init__(self):
        self.jogadorMao = 1
        self.cartaAltaRobo = 0
        self.cartaMediaRobo = 0
        self.cartaBaixaRobo = 0
        self.naipeCartaAltaRobo = 0
        self.naipeCartaMediaRobo = 0
        self.naipeCartaBaixaRobo = 0
        self.primeiraCartaRobo = 0
        self.primeiraCartaHumano = 0
        self.segundaCartaRobo = 0
        self.segundaCartaHumano = 0
        self.terceiraCartaRobo = 0
        self.terceiraCartaHumano = 0
        self.ganhadorPrimeiraRodada = 2
        self.ganhadorSegundaRodada = 2
        self.ganhadorTerceiraRodada = 2
        self.quemTruco = 0
        self.quemGanhouTruco = 0
        self.quemRetruco = 0
        self.quemGanhouRetruco = 0
        self.quemValeQuatro = 0
        self.quemGanhouValeQuatro = 0
        self.pontosEnvidoRobo = 0
        self.quemPediuEnvido = 0
        self.quemGanhouEnvido = 0
        self.quemPediuRealEnvido = 0
        self.quemPediuFaltaEnvido = 0
        self.quemFlor = 0
        self.quemGanhouFlor = 0
        self.quemContraFlor = 0
        self.quemContraFlorResto = 0

    def to_dict(self):
        return self.__dict__

    def to_dataframe(self):
        return pd.DataFrame([self.to_dict()])
