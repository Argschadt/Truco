import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

class CbrUpdated():
    def __init__(self):
        self.indice = 0
        self.casos = self.atualizarDataframe()
        self.model = self.criarModelo()

    def codificarNaipe(self, naipe):
        if naipe == 'ESPADAS':
            return 1
        
        if naipe == 'OUROS':
            return 2
        
        if naipe == 'BASTOS':
            return 3
        
        if naipe == 'COPAS':
            return 4

    def atualizarDataframe(self):
        df = pd.read_csv('../dbtrucoimitacao_maos.csv', index_col='idMao').fillna(0)
        colunas_string = [
            'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 
            'naipeCartaAltaHumano', 'naipeCartaMediaHumano', 'naipeCartaBaixaHumano',
            'naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano', 'naipeSegundaCartaRobo', 
            'naipeSegundaCartaHumano', 'naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano',
        ]
        colunas_int = [col for col in df.columns if col not in colunas_string]
        df[colunas_int] = df[colunas_int].astype('int').apply(abs)
        df.replace('ESPADAS', '1', inplace=True)
        df.replace('OURO', '2', inplace=True)
        df.replace('BASTOS', '3', inplace=True)
        df.replace('COPAS', '4', inplace=True)
        df[colunas_string] = df[colunas_string].astype('int')
        df = df[(df >= 0).all(axis=1)]
        
        return df

    def criarModelo(self):
        model = NearestNeighbors(n_neighbors=100, algorithm='auto', metric='euclidean')
        model.fit(self.casos)
        return model
    
    def retornarSimilares(self, registro):
        distancias, indices = self.model.kneighbors(registro)
        indices = indices[0]
        jogadas_similares = self.casos.iloc[indices]

        # Novo filtro: apenas mãos com o mesmo número de vitórias para o robô ou jogador
        jogadas_similares = jogadas_similares[
            (jogadas_similares[['ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']].apply(lambda x: (x == 1).sum(), axis=1) ==
             registro[['ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']].apply(lambda x: (x == 1).sum(), axis=1).iloc[0]) |
            (jogadas_similares[['ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']].apply(lambda x: (x == 2).sum(), axis=1) ==
             registro[['ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']].apply(lambda x: (x == 2).sum(), axis=1).iloc[0])
        ]
        
        return jogadas_similares