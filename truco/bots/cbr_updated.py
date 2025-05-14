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

class CbrUpdated():
    def __init__(self):
        self.indice = 0
        # Define o diretório base do projeto
        self.base_dir = Path(__file__).parent.parent.parent
        self.csv_maos = self.base_dir / 'dbtrucoimitacao_maos.csv'
        self.csv_maos_cbrkit = self.base_dir / 'dbtrucoimitacao_maos_cbrkit.csv'
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
        if not self.csv_maos.exists():
            raise FileNotFoundError(f"Arquivo CSV de mãos não encontrado: {self.csv_maos}")
        df = pd.read_csv(self.csv_maos, index_col='idMao').fillna(0)
        # Filtra apenas rodadas onde todas as rodadas foram ganhas pelo jogador 2
        df = df[(df['ganhadorPrimeiraRodada'] == 2) & (df['ganhadorSegundaRodada'] == 2) & (df['ganhadorTerceiraRodada'] == 2)]
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
        
        df.to_csv(self.csv_maos_cbrkit)

    def atualizarDataframe(self):
        self.gerar_novo_CSV()
        if not self.csv_maos_cbrkit.exists():
            raise FileNotFoundError(f"Arquivo CSV para CBRKit não encontrado: {self.csv_maos_cbrkit}")
        casebase = cbrkit.loaders.file(self.csv_maos_cbrkit)
        return casebase
    
    def montar_query_do_registro(self, registro):
        # Lista reduzida de campos essenciais
        campos = [
            'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo',
            'primeiraCartaRobo', 'primeiraCartaHumano',
            'segundaCartaRobo', 'segundaCartaHumano',
            'terceiraCartaRobo', 'terceiraCartaHumano',
            'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada',
            'quemTruco', 'quemGanhouTruco', 'quemEnvidoEnvido', 'quemGanhouEnvido'
        ]
        if hasattr(registro, 'to_dict'):
            if hasattr(registro, 'iloc'):
                registro_dict = registro.iloc[0].to_dict()
            else:
                registro_dict = registro.to_dict()
        else:
            registro_dict = dict(registro)
        query = {campo: registro_dict.get(campo, 0) for campo in campos}
        return query

    def retornarSimilares(self, registro):
        global_sim = self.global_similarity()
        retriever = cbrkit.retrieval.build(global_sim, limit=100)
        query = self.montar_query_do_registro(registro)
        try:
            result = cbrkit.retrieval.apply(self.casebase, query, retriever)
        except IndexError as e:
            print("ERRO: IndexError ao chamar o retrieval. O casebase está vazio ou a query não bate com os dados.")
            print("Detalhes:", e)
            return pd.DataFrame()

        # Lista reduzida de colunas essenciais
        casebase_columns = [
            'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo',
            'primeiraCartaRobo', 'primeiraCartaHumano',
            'segundaCartaRobo', 'segundaCartaHumano',
            'terceiraCartaRobo', 'terceiraCartaHumano',
            'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada',
            'quemTruco', 'quemGanhouTruco', 'quemEnvidoEnvido', 'quemGanhouEnvido'
        ]

        if isinstance(result.casebase, dict):
            if all(isinstance(v, list) for v in result.casebase.values()):
                jogadas_similares_df = pd.DataFrame(result.casebase)
            else:
                jogadas_similares_df = pd.DataFrame([result.casebase])
            valid_indices = [i for i in result.ranking if i < len(jogadas_similares_df)]
            jogadas_similares_df = jogadas_similares_df.iloc[valid_indices]
        else:
            valid_indices = [i for i in result.ranking if i < len(result.casebase)]
            jogadas_similares_df = result.casebase.iloc[valid_indices]
        for col in casebase_columns:
            if col not in jogadas_similares_df.columns:
                jogadas_similares_df[col] = 0
        jogadas_similares_df = jogadas_similares_df[casebase_columns]
        return jogadas_similares_df

    def global_similarity(self):
        # Função de similaridade global baseada apenas nos atributos essenciais
        sim_fn = cbrkit.sim.attribute_value(
            attributes={
                'cartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'primeiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'primeiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'segundaCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'segundaCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'terceiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'terceiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'ganhadorPrimeiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorSegundaRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorTerceiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemEnvidoEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
            },
            aggregator=cbrkit.sim.aggregator("mean"),
        )
        return sim_fn