import os
import random 
import pandas as pd
from truco.models.modelo_registro import ModeloRegistro

NAIPE_MAP = {
    "ESPADAS": 1,
    "OUROS": 2,
    "BASTOS": 3,
    "COPAS": 4
}

class Bot():

    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.maoRank = []
        self.indices = []
        self.pontuacaoCartas = []
        self.forcaMao = 0
        self.pontos = 0
        self.rodadas = 0
        self.invido = 0
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediuTruco = False
        self.modeloRegistro = ModeloRegistro()
        # Caminho absoluto para a raiz do projeto
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
        
    # Cria a mão do bot com 3 cartas retiradas do baralho, verifica se tem Flor e inicializa o registro do modelo.    
    def criarMao(self, baralho, controller=None):
        self.indices = [0, 1, 2]
        
        for i in range(3):
            carta_original = baralho.retirarCarta()
            carta_copia = carta_original.copiar()
            self.mao.append(carta_copia)
        self.flor = self.checaFlor()
            
        self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        self.forcaMao = sum(self.pontuacaoCartas)
        self.inicializarRegistro(controller)
        self.cartas_jogadas_robo = [0, 0, 0]
        self.cartas_jogadas_humano = [0, 0, 0]
        
    def jogarCarta(self, cbr=None, controller=None):
        if not self.mao:
            return None

        # Atualiza o modelo de registro antes de decidir a carta
        if controller:
            controller.atualizar_modelo_registro()

        # Decide qual carta jogar
        carta_idx = self._decidir_carta_a_jogar(cbr, controller)

        carta_jogada = self._remover_carta_da_mao(carta_idx)

        # Atualiza o modelo de registro após jogar a carta
        if controller and carta_jogada:
            controller.atualizar_modelo_registro()

        return carta_jogada

    def _decidir_carta_a_jogar(self, cbr=None, controller=None):
        """Decide o índice da carta a ser jogada, usando CBR se possível, senão a menor carta.
        Se a carta da maioria não estiver disponível, tenta a próxima (Alta > Media > Baixa)."""
        # Atualiza os índices se necessário
        if self.indices is None or len(self.indices) != len(self.mao):
            self.indices = list(range(len(self.mao)))
        if not self.mao:
            return None
        df = cbr.retornarSimilares(controller.modeloRegistro)
        
        ordem_carta_jogada = 'CartaRobo'
        if self.indices is not None and len(self.indices) == 3:
            ordem_carta_jogada = 'primeira' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 2:
            ordem_carta_jogada = 'segunda' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 1:
            ordem_carta_jogada = 'terceira' + ordem_carta_jogada

        # Se não há CBR ou coluna correspondente, joga a menor carta
        if df.empty or ordem_carta_jogada not in df.columns:
            return self._indice_menor_carta()

        cartas_mao = {
            'Alta': self.modeloRegistro.cartaAltaRobo,
            'Media': self.modeloRegistro.cartaMediaRobo,
            'Baixa': self.modeloRegistro.cartaBaixaRobo
        }
        # Conta quantas vezes cada valor de carta da mão aparece nas queries
        counts = {'Alta': 0, 'Media': 0, 'Baixa': 0}
        for valor in df[ordem_carta_jogada]:
            for tipo, carta in cartas_mao.items():
                if valor == carta:
                    counts[tipo] += 1
        # Ordena as opções por maioria
        opcoes_ordenadas = sorted(counts, key=counts.get, reverse=True)
        # Tenta jogar a carta da maioria, se não estiver disponível tenta as próximas
        for tipo in opcoes_ordenadas:
            carta_escolhida = cartas_mao[tipo]
            if carta_escolhida in self.pontuacaoCartas:
                return self.pontuacaoCartas.index(carta_escolhida)
        return self._indice_menor_carta()

    def _indice_menor_carta(self):
        """Retorna o índice da menor carta na mão atual."""
        menor_pontuacao = min(self.pontuacaoCartas)
        return self.pontuacaoCartas.index(menor_pontuacao)

    def _remover_carta_da_mao(self, idx_mao):
        """Remove a carta da mão, atualiza os estados e retorna a carta jogada."""
        if idx_mao is None or not self.mao:
            return None
        self.indices.pop(idx_mao)
        carta_jogada = self.mao.pop(idx_mao)
        self.pontuacaoCartas.pop(idx_mao)
        # Atualiza pontuação e ranking de acordo com o número de cartas restantes
        if len(self.mao) >= 3:
            self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        elif len(self.mao) > 0:
            # Para 2 ou 1 carta, calcula pontuação simples
            self.pontuacaoCartas = [carta.retornarNumero() for carta in self.mao]
            self.maoRank = ["Alta" if i == 0 else "Baixa" for i in range(len(self.mao))]
        else:
            self.pontuacaoCartas, self.maoRank = [], []
            self.indices = []
        # Ajusta os índices restantes
        self.indices = list(range(len(self.mao)))
        return carta_jogada

    # Ajusta os índices da mão de acordo com o tamanho da mão
    def AjustaIndicesMao(self, tam_mao):
        if(tam_mao) == 2:
            return [0, 1]
        
        if(tam_mao) == 1:
            return [0]

    def mostrarMao(self):
        i = 0
        for carta in self.mao:
            carta.printarCarta(i)
            i += 1

    def adicionarPonto(self, valor=1):
        self.pontos += valor
    
    def adicionarRodada(self, rodadas):
        self.rodadas += rodadas
    
    def resetar(self):
        # Não zera os pontos
        self.mao = []
        self.flor = False
        self.pediuTruco = False
        # ...outros estados temporários se necessário...

    def checaMao(self):
        return self.mao
    
    def calculaInvido(self):
        self.invido += 1

    def checaFlor(self):
        # print('checaflor')
        if all(carta.retornarNaipe() == self.mao[0].retornarNaipe() for carta in self.mao):
            self.flor = True
            return True
        return False
    
    def inicializarRegistro(self, controller=None):
        self.modeloRegistro.jogadorMao = 1 if controller and hasattr(controller, 'jogador_mao') else 2
        if controller:
            if controller.proximo_primeiro == controller.jogador1:
                self.modeloRegistro.jogadorMao = 2
            else:
                self.modeloRegistro.jogadorMao = 1
        # Definir índices de Alta, Media e Baixa se existirem
        idx_alta = self.maoRank.index("Alta") if "Alta" in self.maoRank else None
        idx_media = self.maoRank.index("Media") if "Media" in self.maoRank else None
        idx_baixa = self.maoRank.index("Baixa") if "Baixa" in self.maoRank else None

        self.modeloRegistro.cartaAltaRobo = self.pontuacaoCartas[idx_alta] if idx_alta is not None else 0
        self.modeloRegistro.cartaMediaRobo = self.pontuacaoCartas[idx_media] if idx_media is not None else 0
        self.modeloRegistro.cartaBaixaRobo = self.pontuacaoCartas[idx_baixa] if idx_baixa is not None else 0

        self.modeloRegistro.naipeCartaAltaRobo = NAIPE_MAP.get(self.mao[idx_alta].retornarNaipe(), 0) if idx_alta is not None else 0
        self.modeloRegistro.naipeCartaMediaRobo = NAIPE_MAP.get(self.mao[idx_media].retornarNaipe(), 0) if idx_media is not None else 0
        self.modeloRegistro.naipeCartaBaixaRobo = NAIPE_MAP.get(self.mao[idx_baixa].retornarNaipe(), 0) if idx_baixa is not None else 0

        self.modeloRegistro.ganhadorPrimeiraRodada = 0
        self.modeloRegistro.ganhadorSegundaRodada = 0
        self.modeloRegistro.ganhadorTerceiraRodada = 0
        
        self.modeloRegistro.pontosEnvidoRobo = self.calcular_pontos_envido()

    def pedir_truco(self, cbr=None, controller=None):
        controller.atualizar_modelo_registro()
        if cbr is not None:
            df = cbr.retornarSimilares(controller.modeloRegistro)
            if not df.empty:
                # Decisão pela maioria: verifica se a maioria ganhou o truco
                maioria = df['quemGanhouTruco'].value_counts().idxmax()
                return maioria == 1
        return False

    def aceitar_truco(self, valor_truco, cbr=None, controller=None):
        controller.atualizar_modelo_registro()
        if cbr is not None:
            df = cbr.retornarSimilares(controller.modeloRegistro)
            if not df.empty:
                quemMaisFugiuTruco = df['quemNegouTruco'].value_counts().idxmax()
                quemGanhouMaisTruco = df['quemGanhouTruco'].value_counts().idxmax()
                if quemGanhouMaisTruco == 1:
                    return True
                if quemMaisFugiuTruco == 2:
                    return True
        return False

    def pedir_envido(self, cbr=None, controller=None):
        controller.atualizar_modelo_registro()
        df = cbr.retornarSimilares(controller.modeloRegistro)
        if not df.empty:
            # Considera apenas situações em que o bot pediu envido
            df_filtrado = df[df['quemPediuEnvido'] == 1]
            if not df_filtrado.empty:
                # Decisão pela maioria: verifica se a maioria ganhou o envido
                maioria = df_filtrado['quemGanhouEnvido'].value_counts().idxmax()
                return maioria == 1
        return False
        
    def aceitar_envido(self, valor_envido, cbr=None, controller=None):
        controller.atualizar_modelo_registro()
        df = cbr.retornarSimilares(controller.modeloRegistro)
        if not df.empty:
            # Considera apenas situações em que o adversário pediu envido
            df_filtrado = df[df['quemPediuEnvido'] == 2]
            if not df_filtrado.empty:
                # Decisão pela maioria: verifica se a maioria ganhou o envido
                maioria = df_filtrado['quemGanhouEnvido'].value_counts().idxmax()
                return maioria == 1
        return False

    def registrar_resultado_rodada(self, resultado, controller=None):
        self.rodadas += 1
        if controller:
            controller.atualizar_modelo_registro()

    def registrar_resultado_mao(self, resultado, controller=None):
        if controller:
            controller.atualizar_modelo_registro()
        
    def resetar_estado_mao(self, controller=None):
        """Limpa todos os estados temporários ao fim de uma mão."""
        self.mao = []
        self.maoRank = []
        self.indices = []
        self.pontuacaoCartas = []
        self.forcaMao = 0
        self.flor = False
        self.pediuTruco = False
        self.rodadas = 0
        self.invido = 0
        self.cartas_jogadas_robo = [0, 0, 0]
        self.cartas_jogadas_humano = [0, 0, 0]
        if controller:
            controller.atualizar_modelo_registro()

    def calcular_pontos_envido(self):
        from truco.utils.pontos import ENVIDO
        naipes = {}
        for carta in self.mao:
            n = carta.retornarNaipe()
            v = ENVIDO.get(str(carta.retornarNumero()), 0)
            if n not in naipes:
                naipes[n] = []
            naipes[n].append(v)
        max_envido = 0
        for valores in naipes.values():
            if len(valores) >= 2:
                valores = sorted(valores, reverse=True)
                max_envido = max(max_envido, 20 + valores[0] + valores[1])
        # Corrige erro se não houver cartas
        todos_valores = [v for sub in naipes.values() for v in sub]
        if max_envido == 0:
            if todos_valores:
                max_envido = max(todos_valores)
            else:
                max_envido = 0
        return max_envido

    def pedir_flor(self, cbr=None, controller=None):
        controller.atualizar_modelo_registro()
        # Não usa CBR: pede Flor apenas se tiver Flor
        return self.flor
