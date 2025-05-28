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
        
        df.to_csv(self.dbtrucoimitacao_maos_cbrkit)

    def atualizarDataframe(self):
        self.gerar_novo_CSV()
        if not self.dbtrucoimitacao_maos_cbrkit.exists():
            raise FileNotFoundError(f"Arquivo CSV para CBRKit não encontrado: {self.dbtrucoimitacao_maos_cbrkit}")
        # Garante que todos os campos usados na query estejam presentes no DataFrame
        campos_necessarios = [
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
            'quemPediuRealEnvido', 'quemGanhouRealEnvido',
            'quemPediuFaltaEnvido', 'quemGanhouFaltaEnvido',
            'quemFlor',
            'quemContraFlor',
            'quemContraFlorResto', 'quemGanhouFlor',
        ]
        df = pd.read_csv(self.dbtrucoimitacao_maos_cbrkit)
        for campo in campos_necessarios:
            if campo not in df.columns:
                df[campo] = 0
        df.to_csv(self.dbtrucoimitacao_maos_cbrkit, index=False)
        casebase = cbrkit.loaders.file(self.dbtrucoimitacao_maos_cbrkit)
        return casebase
    
    def montar_query_do_registro(self, registro):
        # Lista reduzida de campos essenciais
        campos = [
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
            'quemPediuRealEnvido', 'quemGanhouRealEnvido',
            'quemPediuFaltaEnvido', 'quemGanhouFaltaEnvido',
            'quemFlor',
            'quemContraFlor',
            'quemContraFlorResto', 'quemGanhouFlor',
        ]
        if hasattr(registro, 'to_dict'):
            if hasattr(registro, 'iloc'):
                registro_dict = registro.iloc[0].to_dict()
            else:
                registro_dict = registro.to_dict()
        else:
            registro_dict = dict(registro)
        query = {campo: registro_dict.get(campo, 0) for campo in campos}
        print("\nQuery montada:", query, "\n")
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
        # Lista reduzida de colunas essenciais
        casebase_columns = [
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
            'quemPediuRealEnvido', 'quemGanhouRealEnvido',
            'quemPediuFaltaEnvido', 'quemGanhouFaltaEnvido',
            'quemFlor',
            'quemContraFlor',
            'quemContraFlorResto', 'quemGanhouFlor',
        ]
        for col in casebase_columns:
            if col not in jogadas_similares_df.columns:
                jogadas_similares_df[col] = 0
        jogadas_similares_df = jogadas_similares_df[casebase_columns]
        return jogadas_similares_df

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
                'quemGanhouRealEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuFaltaEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouFaltaEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlorResto': cbrkit.sim.numbers.linear(min=0, max=2),
            },
            aggregator=cbrkit.sim.aggregator("mean"),
        )
        return sim_fn