import pandas as pd
import numpy as np
import cbrkit
from pathlib import Path

class CbrUpdated():
    def __init__(self):
        self.indice = 0
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
        
        df.to_csv('../dbtrucoimitacao_maos_cbrkit.csv')
        
    def atualizarDataframe(self):
        self.gerar_novo_CSV()
        casebase = cbrkit.loaders.file(Path('../dbtrucoimitacao_maos_cbrkit.csv'))
        return casebase
    
    def retornarSimilares(self, registro):
        global_sim = self.global_similarity()
        retriever = cbrkit.retrieval.build(global_sim, limit=100)
        casebase_columns = [
            'idMao','jogadorMao','cartaAltaRobo','cartaMediaRobo','cartaBaixaRobo','cartaAltaHumano','cartaMediaHumano','cartaBaixaHumano',
            'primeiraCartaRobo','primeiraCartaHumano','segundaCartaRobo','segundaCartaHumano','terceiraCartaRobo','terceiraCartaHumano',
            'ganhadorPrimeiraRodada','ganhadorSegundaRodada','ganhadorTerceiraRodada','quemPediuEnvido','quemPediuFaltaEnvido','quemPediuRealEnvido',
            'pontosEnvidoRobo','pontosEnvidoHumano','quemNegouEnvido','quemGanhouEnvido','tentosEnvido','quemFlor','quemContraFlor','quemContraFlorResto',
            'quemNegouFlor','pontosFlorRobo','pontosFlorHumano','quemGanhouFlor','tentosFlor','quemEscondeuPontosEnvido','quemEscondeuPontosFlor',
            'quemTruco','quandoTruco','quemRetruco','quandoRetruco','quemValeQuatro','quandoValeQuatro','quemNegouTruco','quemGanhouTruco','tentosTruco',
            'tentosAnterioresRobo','tentosAnterioresHumano','tentosPosterioresRobo','tentosPosterioresHumano','quemBaralho','quandoBaralho','quemContraFlorFalta',
            'quemEnvidoEnvido','quemFlorFlor','quandoCartaVirada','naipeCartaAltaRobo','naipeCartaMediaRobo','naipeCartaBaixaRobo','naipeCartaAltaHumano',
            'naipeCartaMediaHumano','naipeCartaBaixaHumano','naipePrimeiraCartaRobo','naipePrimeiraCartaHumano','naipeSegundaCartaRobo','naipeSegundaCartaHumano',
            'naipeTerceiraCartaRobo','naipeTerceiraCartaHumano','quantidadeChamadasHumano','quantidadeChamadasRobo','qualidadeMaoRobo','qualidadeMaoHumano',
            'quantidadeChamadasEnvidoRobo','quantidadeChamadasEnvidoHumano','saldoTruco','saldoEnvido','saldoFlor'
        ]
        if hasattr(registro, 'to_dict'):
            query = {k: (v if not isinstance(v, dict) else 0) for k, v in registro.to_dict().items() if k in casebase_columns}
        else:
            query = {k: (v if not isinstance(v, dict) else 0) for k, v in dict(registro).items() if k in casebase_columns}
        query = {k: v for k, v in query.items() if isinstance(v, (int, float, str, bool, type(None)))}
        # Pré-filtra o casebase pelo jogadorMao para acelerar
        if 'jogadorMao' in query and hasattr(self.casebase, 'df'):
            filtered_df = self.casebase.df[self.casebase.df['jogadorMao'] == query['jogadorMao']]
            filtered_casebase = cbrkit.loaders.dataframe(filtered_df)
        else:
            filtered_casebase = self.casebase
        result = cbrkit.retrieval.apply(filtered_casebase, query, retriever)
        if isinstance(result.casebase, dict):
            if all(isinstance(v, list) for v in result.casebase.values()):
                jogadas_similares_df = pd.DataFrame(result.casebase)
            else:
                jogadas_similares_df = pd.DataFrame([result.casebase])
            if 'idMao' in jogadas_similares_df.columns:
                jogadas_similares_df.set_index('idMao', inplace=True)
            valid_indices = [i for i in result.ranking if i < len(jogadas_similares_df)]
            jogadas_similares_df = jogadas_similares_df.iloc[valid_indices]
        else:
            valid_indices = [i for i in result.ranking if i < len(result.casebase)]
            jogadas_similares_df = result.casebase.iloc[valid_indices]
        for col in casebase_columns:
            if col not in jogadas_similares_df.columns:
                jogadas_similares_df[col] = 0
        jogadas_similares_df = jogadas_similares_df[casebase_columns]
        v1 = [query.get('ganhadorPrimeiraRodada', 0), query.get('ganhadorSegundaRodada', 0), query.get('ganhadorTerceiraRodada', 0)]
        count1 = v1.count(1)
        count2 = v1.count(2)
        rodada_cols = ['ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada']
        sum1 = (jogadas_similares_df[rodada_cols] == 1).sum(axis=1)
        sum2 = (jogadas_similares_df[rodada_cols] == 2).sum(axis=1)
        mask = (sum1 == count1) | (sum2 == count2)
        jogadas_similares_df = jogadas_similares_df[mask]
        jogadas_similares_df['vitorias_robo'] = (jogadas_similares_df[rodada_cols] == 1).sum(axis=1)
        jogadas_similares_df = jogadas_similares_df.sort_values(by='vitorias_robo', ascending=False)
        return jogadas_similares_df
    
    def global_similarity(self):
        # Função de similaridade global baseada em todos os atributos do CSV
        sim_fn = cbrkit.sim.attribute_value(
            attributes={
                'cartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaAltaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaMediaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'cartaBaixaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'primeiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'primeiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'segundaCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'segundaCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'terceiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=12),
                'terceiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=12),
                'ganhadorPrimeiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorSegundaRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'ganhadorTerceiraRodada': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuFaltaEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemPediuRealEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'pontosEnvidoRobo': cbrkit.sim.numbers.linear(min=0, max=33),
                'pontosEnvidoHumano': cbrkit.sim.numbers.linear(min=0, max=33),
                'quemNegouEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'tentosEnvido': cbrkit.sim.numbers.linear(min=0, max=15),
                'quemFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemContraFlorResto': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemNegouFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'pontosFlorRobo': cbrkit.sim.numbers.linear(min=0, max=33),
                'pontosFlorHumano': cbrkit.sim.numbers.linear(min=0, max=33),
                'quemGanhouFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'tentosFlor': cbrkit.sim.numbers.linear(min=0, max=15),
                'quemEscondeuPontosEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemEscondeuPontosFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quandoTruco': cbrkit.sim.numbers.linear(min=0, max=3),
                'quemRetruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quandoRetruco': cbrkit.sim.numbers.linear(min=0, max=3),
                'quemValeQuatro': cbrkit.sim.numbers.linear(min=0, max=2),
                'quandoValeQuatro': cbrkit.sim.numbers.linear(min=0, max=3),
                'quemNegouTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemGanhouTruco': cbrkit.sim.numbers.linear(min=0, max=2),
                'tentosTruco': cbrkit.sim.numbers.linear(min=0, max=15),
                'tentosAnterioresRobo': cbrkit.sim.numbers.linear(min=0, max=15),
                'tentosAnterioresHumano': cbrkit.sim.numbers.linear(min=0, max=15),
                'tentosPosterioresRobo': cbrkit.sim.numbers.linear(min=0, max=15),
                'tentosPosterioresHumano': cbrkit.sim.numbers.linear(min=0, max=15),
                'quemBaralho': cbrkit.sim.numbers.linear(min=0, max=2),
                'quandoBaralho': cbrkit.sim.numbers.linear(min=0, max=3),
                'quemContraFlorFalta': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemEnvidoEnvido': cbrkit.sim.numbers.linear(min=0, max=2),
                'quemFlorFlor': cbrkit.sim.numbers.linear(min=0, max=2),
                'quandoCartaVirada': cbrkit.sim.numbers.linear(min=0, max=3),
                'naipeCartaAltaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaMediaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaBaixaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaAltaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaMediaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeCartaBaixaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipePrimeiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipePrimeiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeSegundaCartaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeSegundaCartaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeTerceiraCartaRobo': cbrkit.sim.numbers.linear(min=1, max=4),
                'naipeTerceiraCartaHumano': cbrkit.sim.numbers.linear(min=1, max=4),
                'quantidadeChamadasHumano': cbrkit.sim.numbers.linear(min=0, max=10),
                'quantidadeChamadasRobo': cbrkit.sim.numbers.linear(min=0, max=10),
                'qualidadeMaoRobo': cbrkit.sim.numbers.linear(min=0, max=100),
                'qualidadeMaoHumano': cbrkit.sim.numbers.linear(min=0, max=100),
                'quantidadeChamadasEnvidoRobo': cbrkit.sim.numbers.linear(min=0, max=10),
                'quantidadeChamadasEnvidoHumano': cbrkit.sim.numbers.linear(min=0, max=10),
                'saldoTruco': cbrkit.sim.numbers.linear(min=-15, max=15),
                'saldoEnvido': cbrkit.sim.numbers.linear(min=-33, max=33),
                'saldoFlor': cbrkit.sim.numbers.linear(min=-33, max=33),
            },
            types={
                int: cbrkit.sim.numbers.linear(max=9999999),
            },
            aggregator=cbrkit.sim.aggregator("mean"),
        )
        return sim_fn