import pandas as pd

class ModeloRegistro:
    def __init__(self):
        self.jogadorMao = 1
        self.cartaAltaRobo = 0
        self.cartaMediaRobo = 0
        self.cartaBaixaRobo = 0
        self.ganhadorPrimeiraRodada = 2
        self.ganhadorSegundaRodada = 2
        self.ganhadorTerceiraRodada = 2
        # Adicione outros campos necessários conforme o uso do bot/cbr

    def to_dict(self):
        return self.__dict__

    def to_dataframe(self):
        return pd.DataFrame([self.to_dict()])
