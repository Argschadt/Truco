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
    def criarMao(self, baralho, controller=None):
        self.indices = [0, 1, 2]
        
        """ # Obter todos os naipes disponíveis no baralho
        available_suits = list(set(carta.naipe for carta in baralho.cartas))
        if available_suits:
            chosen_suit = random.choice(available_suits)
            
            # Encontrar todas as cartas do naipe escolhido
            suit_cards = [carta for carta in baralho.cartas if carta.naipe == chosen_suit]
            
            # Se tivermos pelo menos 3 cartas do naipe escolhido, use-as
            if len(suit_cards) >= 3:
                # Remover estas cartas do baralho
                for carta in suit_cards[:3]:
                    baralho.cartas.remove(carta)
                
                # Adicionar à mão do bot
                self.mao.extend(suit_cards[:3])
                
                # Marcar que temos uma flor
                self.flor = True
            else:
                # Fallback: criação padrão de mão se não pudermos criar uma flor
                print("Aviso: Não foi possível criar uma flor para o Bot, usando cartas aleatórias.")
                for i in range(3):
                    self.mao.append(baralho.retirarCarta())
                self.flor = self.checaFlor()
        else: """
            # Fallback: criação padrão de mão
        for i in range(3):
            self.mao.append(baralho.retirarCarta())
        self.flor = self.checaFlor()
            
        self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        self.forcaMao = sum(self.pontuacaoCartas)
        self.inicializarRegistro(controller)
        self.atualizar_modelo_registro(controller)
        self.cartas_jogadas_robo = [0, 0, 0]
        self.cartas_jogadas_humano = [0, 0, 0]
    
    def jogarCarta(self, cbr, controller=None):
        self.atualizar_modelo_registro(controller)
        if self.indices is None or len(self.indices) != len(self.mao):
            self.indices = list(range(len(self.mao)))
        if not self.mao:
            return None
        df = cbr.retornarSimilares(self.modeloRegistro)
        ordem_carta_jogada = 'CartaRobo'
        if self.indices is not None and len(self.indices) == 3:
            ordem_carta_jogada = 'primeira' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 2:
            ordem_carta_jogada = 'segunda' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 1:
            ordem_carta_jogada = 'terceira' + ordem_carta_jogada

        # Se não há CBR ou coluna correspondente, joga a menor carta
        if df.empty or ordem_carta_jogada not in df.columns:
            print("Jogou MENOR CARTA!!!!!!!!!!!!")
            # Encontra o índice da menor carta na pontuacaoCartas
            menor_pontuacao = min(self.pontuacaoCartas)
            idx_mao = self.pontuacaoCartas.index(menor_pontuacao)
            # O índice real na mão é self.indices[idx_mao]
            indice_real = self.indices[idx_mao]
            # Remove dos controles
            self.indices.pop(idx_mao)
            self.pontuacaoCartas.pop(idx_mao)
            carta_jogada = self.mao.pop(idx_mao)
            # Ajusta os índices restantes
            self.indices = list(range(len(self.mao)))
            return carta_jogada

        # Verifica qual carta (alta, media, baixa) foi jogada pela maioria
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
        # Decide pela maioria
        tipo_maioria = max(counts, key=counts.get)
        carta_escolhida = cartas_mao[tipo_maioria]
        # Se a carta escolhida não está mais na mão (já foi jogada), pega a menor
        if carta_escolhida not in self.pontuacaoCartas:
            carta_escolhida = min(self.pontuacaoCartas)
        idx_mao = self.pontuacaoCartas.index(carta_escolhida)
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
        self.pontos = 0
        self.mao = []
        self.flor = False

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

        self.modeloRegistro.ganhadorPrimeiraRodada = 3
        self.modeloRegistro.ganhadorSegundaRodada = 3
        self.modeloRegistro.ganhadorTerceiraRodada = 3

    def atualizar_modelo_registro(self, controller=None):
        if controller is None:
            return

        # jogadorMao
        if hasattr(controller, 'jogador_mao'):
            self.modeloRegistro.jogadorMao = 1 if controller.jogador_mao == self else 2                    

        # Controle robusto das cartas jogadas
        # Inicializa listas se não existirem
        if not hasattr(self, 'cartas_jogadas_robo'):
            self.cartas_jogadas_robo = [0, 0, 0]
        if not hasattr(self, 'cartas_jogadas_humano'):
            self.cartas_jogadas_humano = [0, 0, 0]
        # Atualiza os campos do modelo de registro
        self.modeloRegistro.primeiraCartaRobo = self.cartas_jogadas_robo[0]
        self.modeloRegistro.segundaCartaRobo = self.cartas_jogadas_robo[1]
        self.modeloRegistro.terceiraCartaRobo = self.cartas_jogadas_robo[2]
        self.modeloRegistro.primeiraCartaHumano = self.cartas_jogadas_humano[0]
        self.modeloRegistro.segundaCartaHumano = self.cartas_jogadas_humano[1]
        self.modeloRegistro.terceiraCartaHumano = self.cartas_jogadas_humano[2]

        # Rodadas
        if hasattr(controller, 'historico_rodadas'):
            h = controller.historico_rodadas
            self.modeloRegistro.ganhadorPrimeiraRodada = h[0] if len(h) > 0 else 0
            self.modeloRegistro.ganhadorSegundaRodada = h[1] if len(h) > 1 else 0
            self.modeloRegistro.ganhadorTerceiraRodada = h[2] if len(h) > 2 else 0

        # Truco/Retruco/Vale Quatro
        self.modeloRegistro.quemTruco = getattr(controller, 'quemTruco', 0)
        self.modeloRegistro.quemGanhouTruco = getattr(controller, 'quemGanhouTruco', 0)
        self.modeloRegistro.quemRetruco = getattr(controller, 'quemRetruco', 0)
        self.modeloRegistro.quemValeQuatro = getattr(controller, 'quemValeQuatro', 0)

        # Envido
        self.modeloRegistro.pontosEnvidoRobo = self.calcular_pontos_envido()
        self.modeloRegistro.quemPediuEnvido = getattr(controller, 'quemPediuEnvido', 0)
        self.modeloRegistro.quemGanhouEnvido = getattr(controller, 'quemGanhouEnvido', 0)
        self.modeloRegistro.quemPediuRealEnvido = getattr(controller, 'quemPediuRealEnvido', 0)
        self.modeloRegistro.quemPediuFaltaEnvido = getattr(controller, 'quemPediuFaltaEnvido', 0)

        # Flor/Contra-Flor
        self.modeloRegistro.quemFlor = getattr(controller, 'quemFlor', 0)
        self.modeloRegistro.quemGanhouFlor = getattr(controller, 'quemGanhouFlor', 0)
        self.modeloRegistro.quemContraFlor = getattr(controller, 'quemContraFlor', 0)
        self.modeloRegistro.quemContraFlorResto = getattr(controller, 'quemContraFlorResto', 0)

    def pedir_truco(self, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai pedir truco usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemTruco' in df.columns:
                maioria = df['quemTruco'].value_counts().idxmax()
                return maioria == 2

    def aceitar_truco(self, valor_truco, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai aceitar truco usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouTruco' in df.columns:
                maioria = df['quemNegouTruco'].value_counts().idxmax()
                return maioria != 2

    def pedir_envido(self, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai pedir envido usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemPediuEnvido' in df.columns:
                maioria = df['quemPediuEnvido'].value_counts().idxmax()
                return maioria == 2

    def aceitar_envido(self, valor_envido, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai aceitar envido usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouEnvido' in df.columns:
                maioria = df['quemNegouEnvido'].value_counts().idxmax()
                return maioria == 2

    def pedir_flor(self, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai pedir flor usando CBR se disponível."""
        """ if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemFlor' in df.columns:
                maioria = df['quemFlor'].value_counts().idxmax()
                return maioria == 2 """
                
        #NAO ACHEI REGISTRO DE PEDIDO DE FLOR NO CSV
        return self.flor    
    
    def registrar_resultado_rodada(self, resultado, controller=None):
        """Atualiza o estado do bot após cada rodada (ganhou, perdeu, empatou)."""
        self.rodadas += 1
        # Pode adicionar lógica de aprendizado ou ajuste de estratégia
        self.atualizar_modelo_registro(controller)    
        
    def registrar_resultado_mao(self, resultado, controller=None):
        """Atualiza o estado do bot após cada mão (ganhou, perdeu, empatou)."""
        # Pode adicionar lógica de aprendizado ou ajuste de estratégia
        self.atualizar_modelo_registro(controller)    
        
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
        self.atualizar_modelo_registro(controller)

    def registrar_carta_jogada(self, carta_valor, rodada_num, controller=None):
        """Registra uma carta jogada pelo bot no modelo de registro."""
        if rodada_num == 1:
            self.cartas_jogadas_robo[0] = carta_valor
        elif rodada_num == 2:
            self.cartas_jogadas_robo[1] = carta_valor
        elif rodada_num == 3:
            self.cartas_jogadas_robo[2] = carta_valor
        self.atualizar_modelo_registro(controller)

    def registrar_carta_humano(self, carta_valor, rodada_num, controller=None):
        """Registra uma carta jogada pelo humano no modelo de registro."""
        if rodada_num == 1:
            self.cartas_jogadas_humano[0] = carta_valor
        elif rodada_num == 2:
            self.cartas_jogadas_humano[1] = carta_valor
        elif rodada_num == 3:
            self.cartas_jogadas_humano[2] = carta_valor
        self.atualizar_modelo_registro(controller)

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
        if max_envido == 0:
            max_envido = max([v for sub in naipes.values() for v in sub])
        return max_envido
