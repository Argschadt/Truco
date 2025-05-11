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
        try:
            if isinstance(registro, pd.DataFrame):
                query = registro
            elif hasattr(registro, 'shape') and len(registro.shape) == 3:
                query = pd.DataFrame(registro.reshape(registro.shape[0], -1))
            elif hasattr(registro, 'shape') or hasattr(registro, '__len__'):
                try:
                    flat_registro = np.array(registro).flatten()
                    query = pd.DataFrame([flat_registro])
                except:
                    query = pd.DataFrame([registro])
            else:
                query = pd.DataFrame([registro])
        except Exception as e:
            print(f"Error converting registro to DataFrame: {e}")
            print(f"Registro type: {type(registro)}, shape (if applicable): {getattr(registro, 'shape', 'N/A')}")
            return pd.DataFrame()
        
        try:
            distancias, indices = self.model.kneighbors(query)
            indices = indices[0]
            
            jogadas_similares = self.casos.iloc[indices]
            
            jogadas_vencidas = jogadas_similares[
                ((jogadas_similares.ganhadorPrimeiraRodada == 2) & (jogadas_similares.ganhadorSegundaRodada == 2)) | 
                ((jogadas_similares.ganhadorPrimeiraRodada == 2) & (jogadas_similares.ganhadorTerceiraRodada == 2)) | 
                ((jogadas_similares.ganhadorSegundaRodada == 2) & (jogadas_similares.ganhadorTerceiraRodada == 2))
            ]
            
            return jogadas_vencidas
        except Exception as e:
            print(f"Error in finding similar cases: {e}")
            print(f"Query shape: {query.shape}")
            return pd.DataFrame()