import pandas as pd
import numpy as np
import cbrkit
from pathlib import Path
from truco.models.carta import Carta
from truco.models.baralho import Baralho
from truco.models.jogador import Jogador
from truco.core.jogo import Jogo
from truco.bots.bot import Bot
from truco.utils.pontos import MANILHA, CARTAS_VALORES

CAMPOS_NECESSARIOS = [
                        'jogadorMao',
                        'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo',
                        'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo',
                        'primeiraCartaRobo', 'primeiraCartaHumano',
                        'segundaCartaRobo', 'segundaCartaHumano',
                        'terceiraCartaRobo', 'terceiraCartaHumano',
                        'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada',
                        'quemTruco', 'quemGanhouTruco',
                        'quemRetruco',
                        'quemValeQuatro',
                        'pontosEnvidoRobo',
                        'quemPediuEnvido', 'quemGanhouEnvido',
                        'quemPediuRealEnvido',
                        'quemPediuFaltaEnvido',
                        'quemFlor',
                        'quemContraFlor',
                        'quemContraFlorResto', 'quemGanhouFlor',
]   

class CbrUpdated():
    def __init__(self):
        self.indice = 0
        # Define o diretório base do projeto
        self.base_dir = Path(__file__).parent.parent.parent
        self.dbtrucoimitacao_maos = self.base_dir / 'dbtrucoimitacao_maos.csv'
        self.dbtrucoimitacao_maos_cbrkit = self.base_dir / 'dbtrucoimitacao_maos_cbrkit.csv'
        self.casebase = self.atualizarDataframe()

    def codificarNaipe(self, naipe):
        if naipe == 'ESPADAS':
            return 1
        
        if naipe == 'OUROS':
            return 2
        
        if naipe == 'BASTOS':
            return 3
        
        if naipe == 'COPAS':
            return 4

    def gerar_novo_CSV(self):
        if not self.dbtrucoimitacao_maos.exists():
            raise FileNotFoundError(f"Arquivo CSV de mãos não encontrado: {self.dbtrucoimitacao_maos}")
        df = pd.read_csv(self.dbtrucoimitacao_maos, index_col='idMao').fillna(0)
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
        
        for column in df.columns:
            if column not in CAMPOS_NECESSARIOS:
                df = df.drop(column, axis=1)
        
        df.to_csv(self.dbtrucoimitacao_maos_cbrkit)

    def atualizarDataframe(self):
        self.gerar_novo_CSV()
        if not self.dbtrucoimitacao_maos_cbrkit.exists():
            raise FileNotFoundError(f"Arquivo CSV para CBRKit não encontrado: {self.dbtrucoimitacao_maos_cbrkit}")
        df = pd.read_csv(self.dbtrucoimitacao_maos_cbrkit)
        df.to_csv(self.dbtrucoimitacao_maos_cbrkit, index=False)
        casebase = cbrkit.loaders.file(self.dbtrucoimitacao_maos_cbrkit)
        return casebase
    
    def montar_query_do_registro(self, registro):
        registro_dict = registro.to_dict()
        # Só adiciona campo se valor for diferente de 0
        query = {campo: valor for campo, valor in ((campo, registro_dict.get(campo, 0)) for campo in CAMPOS_NECESSARIOS) if valor != 0}
        #print("\nQuery montada:", query, "\n")
        return query

    def retornarSimilares(self, registro):
        global_sim = self.global_similarity()
        retriever = cbrkit.retrieval.build(global_sim, limit=10)
        query = self.montar_query_do_registro(registro)
        result = cbrkit.retrieval.apply(self.casebase, query, retriever)        
        jogadas_similares_df = pd.DataFrame([result.casebase])
        df_trad = jogadas_similares_df.transpose()
        casos = [row[0] for _, row in df_trad.iterrows()]
        df_final = pd.DataFrame(casos)
        return df_final

    def global_similarity(self):
        # Função de similaridade global baseada nos atributos essenciais e novos campos
        sim_fn = cbrkit.sim.attribute_value(
            attributes={
                'jogadorMao': cbrkit.sim.numbers.linear(min=1, max=2),
                'cartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'cartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'cartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'naipeCartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'primeiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'primeiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'segundaCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'segundaCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'terceiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'terceiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'ganhadorPrimeiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorSegundaRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorTerceiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemRetruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemValeQuatro': cbrkit.sim.numbers.linear(min=0, max=2),
                'pontosEnvidoRobo': cbrkit.sim.numbers.linear(min=0, max=33),
                'quemPediuEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuRealEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuFaltaEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlorResto': cbrkit.sim.numbers.linear(min=0, max=2),
            },
            aggregator=cbrkit.sim.aggregator("mean"),
        )
        return sim_fn