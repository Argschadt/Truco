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
                        'quemTruco', 'quemGanhouTruco', 'quemNegouTruco',
                        'quemRetruco',
                        'quemValeQuatro',
                        'pontosEnvidoRobo',
                        'quemPediuEnvido', 'quemGanhouEnvido', 'quemNegouEnvido',
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
        self.dataframe = self.gerar_novo_CSV()
        self.casebase_mao1 = self.gerarCaseBase_mao1()
        self.casebase_mao2 = self.gerarCaseBase_mao2()

    def codificarNaipe(self, naipe):
        if naipe == 'ESPADAS':
            return 1
        
        if naipe == 'OUROS':
            return 2
        
        if naipe == 'BASTOS':
            return 3
        
        if naipe == 'COPAS':
            return 4

    def montar_query_do_registro(self, registro):
        registro_dict = registro.to_dict()
        # Só adiciona campo se valor for diferente de 0
        query = {campo: valor for campo, valor in ((campo, registro_dict.get(campo, 0)) for campo in CAMPOS_NECESSARIOS) if valor != 0}
        #print("\nQuery montada:", query, "\n")
        return query
    
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
        
        return df

    def gerarCaseBase_mao1(self, jogadorMao=None):
        """Atualiza o casebase para conter apenas casos com jogadorMao igual ao informado."""
        # Carrega o DataFrame completo
        df = self.dataframe
        # Filtra pelo jogadorMao
        df = df[df['jogadorMao'] == 1]
        # Salva em um arquivo temporário
        temp_path = self.base_dir / f'dbtrucoimitacao_maos_cbrkit_jogadorMao_1.csv'
        df.to_csv(temp_path, index=False)
        # Atualiza o casebase para usar apenas o filtrado
        return cbrkit.loaders.file(temp_path)
        
    def gerarCaseBase_mao2(self, jogadorMao=None):
        """Atualiza o casebase para conter apenas casos com jogadorMao igual ao informado."""
        # Carrega o DataFrame completo
        df = self.dataframe
        # Filtra pelo jogadorMao
        df = df[df['jogadorMao'] == 2]
        # Salva em um arquivo temporário
        temp_path = self.base_dir / f'dbtrucoimitacao_maos_cbrkit_jogadorMao_2.csv'
        df.to_csv(temp_path, index=False)
        # Atualiza o casebase para usar apenas o filtrado
        return cbrkit.loaders.file(temp_path)

    def retornarSimilares(self, registro):
        global_sim = self.global_similarity()
        retriever = cbrkit.retrieval.build(global_sim, limit=20)
        query = self.montar_query_do_registro(registro)
        if registro.jogadorMao == 1:
            self.gerarCaseBase_mao1()
            result = cbrkit.retrieval.apply(self.casebase_mao1, query, retriever)
        elif registro.jogadorMao == 2:
            self.gerarCaseBase_mao2()
            result = cbrkit.retrieval.apply(self.casebase_mao2, query, retriever)
        jogadas_similares_df = pd.DataFrame([result.casebase])
        df_trad = jogadas_similares_df.transpose()
        casos = [row[0] for _, row in df_trad.iterrows()]
        df_final = pd.DataFrame(casos)
        return df_final

    def global_similarity(self):
        # Função de similaridade global baseada nos atributos essenciais e novos campos
        sim_fn = cbrkit.sim.attribute_value(
            attributes={
                'jogadorMao': cbrkit.sim.generic.equality(),
                'cartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'cartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'cartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'naipeCartaAltaRobo': cbrkit.sim.generic.equality(),
                'naipeCartaMediaRobo': cbrkit.sim.generic.equality(),
                'naipeCartaBaixaRobo': cbrkit.sim.generic.equality(),
                'primeiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'primeiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'segundaCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'segundaCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'terceiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=52),
                'terceiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=52),
                'ganhadorPrimeiraRodada': cbrkit.sim.generic.equality(),
                'ganhadorSegundaRodada': cbrkit.sim.generic.equality(),
                'ganhadorTerceiraRodada': cbrkit.sim.generic.equality(),
                'quemTruco': cbrkit.sim.generic.equality(),
                'quemNegouTruco': cbrkit.sim.generic.equality(),
                'quemGanhouTruco': cbrkit.sim.generic.equality(),
                'quemRetruco': cbrkit.sim.generic.equality(),
                'quemValeQuatro': cbrkit.sim.generic.equality(),
                'pontosEnvidoRobo': cbrkit.sim.numbers.linear(min=0, max=33),
                'quemPediuEnvido': cbrkit.sim.generic.equality(),
                'quemNegouEnvido': cbrkit.sim.generic.equality(),
                'quemGanhouEnvido': cbrkit.sim.generic.equality(),
                'quemPediuRealEnvido': cbrkit.sim.generic.equality(),
                'quemPediuFaltaEnvido': cbrkit.sim.generic.equality(),
                'quemFlor': cbrkit.sim.generic.equality(),
                'quemGanhouFlor': cbrkit.sim.generic.equality(),
                'quemContraFlor': cbrkit.sim.generic.equality(),
                'quemContraFlorResto': cbrkit.sim.generic.equality(),
            },
            aggregator=cbrkit.sim.aggregator("mean"),
        )
        return sim_fn