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
        # Garante que self.indices é uma lista válida
        if self.indices is None:
            self.indices = list(range(len(self.mao)))
        df = cbr.retornarSimilares(self.modeloRegistro)
        carta_escolhida = 0
        ordem_carta_jogada = 'CartaRobo'

        if self.indices is not None and len(self.indices) == 3:
            ordem_carta_jogada = 'primeira' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 2:
            ordem_carta_jogada = 'segunda' + ordem_carta_jogada
        elif self.indices is not None and len(self.indices) == 1:
            ordem_carta_jogada = 'terceira' + ordem_carta_jogada

        # Protege contra DataFrame vazio ou coluna inexistente
        if ordem_carta_jogada not in df.columns or df.empty:
            # fallback: joga a menor carta disponível
            indice = 0
            self.indices.remove(indice)
            self.pontuacaoCartas.pop(indice)
            self.indices = self.AjustaIndicesMao(len(self.indices))
            return self.mao.pop(indice)

        for i in reversed(range(len(df[ordem_carta_jogada].value_counts().index.to_list()))): 
            aux = df[ordem_carta_jogada].value_counts().index.to_list()[i]
            if carta_escolhida in self.pontuacaoCartas:
                carta_escolhida = aux

        if carta_escolhida == 0:
            valores = df[ordem_carta_jogada].value_counts().index.to_list()
            if valores:
                valor_referencia = valores[0]
            else:
                # Valor padrão caso não haja valores (exemplo: escolha aleatória)
                valor_referencia = min(self.pontuacaoCartas)  # joga a menor carta
            carta_escolhida = min(self.pontuacaoCartas, key=lambda x:abs(x-valor_referencia))

        indice = self.pontuacaoCartas.index(carta_escolhida)
        self.indices.remove(indice)
        carta_jogada = self.mao.pop(indice)
        # Após remover a carta da mão, recalcule a pontuação e ranking das cartas restantes
        if self.mao:
            self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        else:
            self.pontuacaoCartas, self.maoRank = [], []        
            self.indices = self.AjustaIndicesMao(len(self.indices))
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
        """Decide se vai pedir truco (ou aumentar aposta) usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemTruco' in df.columns:
                # 1 = bot pediu truco, 0 = não pediu
                maioria = df['quemTruco'].value_counts().idxmax()
                return maioria == 1
        return self.forcaMao > 40

    def aceitar_truco(self, valor_truco, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se aceita o truco pedido pelo adversário usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouTruco' in df.columns:
                # 0 = não negou (aceitou), 1 = negou (recusou)
                maioria = df['quemNegouTruco'].value_counts().idxmax()
                return maioria == 0
        # fallback heurístico
        return self.forcaMao > 25

    def pedir_envido(self, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai pedir envido usando CBR se disponível."""
        if self.flor:
            return False
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemPediuEnvido' in df.columns:
                maioria = df['quemPediuEnvido'].value_counts().idxmax()
                return maioria == 2
        print("Nao usou o CBR para pedir envido")
        return False

    def aceitar_envido(self, valor_envido, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se aceita o envido pedido pelo adversário usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouEnvido' in df.columns:
                maioria = df['quemNegouEnvido'].value_counts().idxmax()
                return maioria == 0
        return False

    def pedir_flor(self, cbr=None, controller=None):
        self.atualizar_modelo_registro(controller)
        """Decide se vai pedir flor usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemFlor' in df.columns:
                maioria = df['quemFlor'].value_counts().idxmax()
                return maioria == 1
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
