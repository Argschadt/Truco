import os
import random 
import pandas as pd
from truco.models.modelo_registro import ModeloRegistro

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
    
    def criarMao(self, baralho):
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
        self.inicializarRegistro()
    
    def jogarCarta(self, cbr, **game_state):
        self.atualizar_modelo_registro(**game_state)
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
        self.pontuacaoCartas.remove(self.pontuacaoCartas[self.pontuacaoCartas.index(carta_escolhida)])
        self.indices = self.AjustaIndicesMao(len(self.indices))
        return self.mao.pop(indice)


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
    
    def inicializarRegistro(self):
        self.modeloRegistro.jogadorMao = 1
        self.modeloRegistro.cartaAltaRobo = self.pontuacaoCartas[self.maoRank.index("Alta")]
        self.modeloRegistro.cartaMediaRobo = self.pontuacaoCartas[self.maoRank.index("Media")]
        self.modeloRegistro.cartaBaixaRobo = self.pontuacaoCartas[self.maoRank.index("Baixa")]
        self.modeloRegistro.ganhadorPrimeiraRodada = 2
        self.modeloRegistro.ganhadorSegundaRodada = 2
        self.modeloRegistro.ganhadorTerceiraRodada = 2
    
    def avaliarJogadaHumano(self):
        pass

    def avaliarTruco(self, cbr):
        if (self.forcaMao > 40):
            return True
        
        else:
            return False
    
    # implementar retruco do bot
    def avaliarAumentarTruco(self, possibilidade, cbr):
        if (possibilidade):
            return True
        return False

    def avaliarEnvido(self):
        return None

    def atualizar_modelo_registro(self, rodada=None, cartas_jogadas=None, ganhadores_rodadas=None, pontos=None, truco_atual=None, envido_atual=None, flor_atual=None, jogador_mao=None, 
                                 cartaAltaRobo=None, cartaMediaRobo=None, cartaBaixaRobo=None,
                                 naipeCartaAltaRobo=None, naipeCartaMediaRobo=None, naipeCartaBaixaRobo=None,
                                 primeiraCartaRobo=None, primeiraCartaHumano=None,
                                 segundaCartaRobo=None, segundaCartaHumano=None,
                                 terceiraCartaRobo=None, terceiraCartaHumano=None,
                                 quemTruco=None, quemGanhouTruco=None,
                                 quemRetruco=None, quemGanhouRetruco=None,
                                 quemValeQuatro=None, quemGanhouValeQuatro=None,
                                 pontosEnvidoRobo=None,
                                 quemPediuEnvido=None, quemGanhouEnvido=None,
                                 quemPediuRealEnvido=None, quemGanhouRealEnvido=None,
                                 quemPediuFaltaEnvido=None, quemGanhouFaltaEnvido=None,
                                 quemFlor=None, quemGanhouFlor=None,
                                 quemContraFlor=None, quemGanhouContraFlor=None,
                                 quemContraFlorResto=None, quemGanhouContraFlorEnvido=None):
        """
        Atualiza o ModeloRegistro do bot com o estado atual do jogo.
        Os parâmetros devem ser passados conforme disponíveis no contexto do jogo.
        """
        if jogador_mao is not None:
            self.modeloRegistro.jogadorMao = jogador_mao
        if cartaAltaRobo is not None:
            self.modeloRegistro.cartaAltaRobo = cartaAltaRobo
        if cartaMediaRobo is not None:
            self.modeloRegistro.cartaMediaRobo = cartaMediaRobo
        if cartaBaixaRobo is not None:
            self.modeloRegistro.cartaBaixaRobo = cartaBaixaRobo
        if naipeCartaAltaRobo is not None:
            self.modeloRegistro.naipeCartaAltaRobo = naipeCartaAltaRobo
        if naipeCartaMediaRobo is not None:
            self.modeloRegistro.naipeCartaMediaRobo = naipeCartaMediaRobo
        if naipeCartaBaixaRobo is not None:
            self.modeloRegistro.naipeCartaBaixaRobo = naipeCartaBaixaRobo
        if primeiraCartaRobo is not None:
            self.modeloRegistro.primeiraCartaRobo = primeiraCartaRobo
        if primeiraCartaHumano is not None:
            self.modeloRegistro.primeiraCartaHumano = primeiraCartaHumano
        if segundaCartaRobo is not None:
            self.modeloRegistro.segundaCartaRobo = segundaCartaRobo
        if segundaCartaHumano is not None:
            self.modeloRegistro.segundaCartaHumano = segundaCartaHumano
        if terceiraCartaRobo is not None:
            self.modeloRegistro.terceiraCartaRobo = terceiraCartaRobo
        if terceiraCartaHumano is not None:
            self.modeloRegistro.terceiraCartaHumano = terceiraCartaHumano
        if ganhadores_rodadas is not None:
            self.modeloRegistro.ganhadorPrimeiraRodada = ganhadores_rodadas[0] if len(ganhadores_rodadas) > 0 else 2
            self.modeloRegistro.ganhadorSegundaRodada = ganhadores_rodadas[1] if len(ganhadores_rodadas) > 1 else 2
            self.modeloRegistro.ganhadorTerceiraRodada = ganhadores_rodadas[2] if len(ganhadores_rodadas) > 2 else 2
        if quemTruco is not None:
            self.modeloRegistro.quemTruco = quemTruco
        if quemGanhouTruco is not None:
            self.modeloRegistro.quemGanhouTruco = quemGanhouTruco
        if quemRetruco is not None:
            self.modeloRegistro.quemRetruco = quemRetruco
        if quemGanhouRetruco is not None:
            self.modeloRegistro.quemGanhouRetruco = quemGanhouRetruco
        if quemValeQuatro is not None:
            self.modeloRegistro.quemValeQuatro = quemValeQuatro
        if quemGanhouValeQuatro is not None:
            self.modeloRegistro.quemGanhouValeQuatro = quemGanhouValeQuatro
        if pontosEnvidoRobo is not None:
            self.modeloRegistro.pontosEnvidoRobo = pontosEnvidoRobo
        if quemPediuEnvido is not None:
            self.modeloRegistro.quemPediuEnvido = quemPediuEnvido
        if quemGanhouEnvido is not None:
            self.modeloRegistro.quemGanhouEnvido = quemGanhouEnvido
        if quemPediuRealEnvido is not None:
            self.modeloRegistro.quemPediuRealEnvido = quemPediuRealEnvido
        if quemGanhouRealEnvido is not None:
            self.modeloRegistro.quemGanhouRealEnvido = quemGanhouRealEnvido
        if quemPediuFaltaEnvido is not None:
            self.modeloRegistro.quemPediuFaltaEnvido = quemPediuFaltaEnvido
        if quemGanhouFaltaEnvido is not None:
            self.modeloRegistro.quemGanhouFaltaEnvido = quemGanhouFaltaEnvido
        if quemFlor is not None:
            self.modeloRegistro.quemFlor = quemFlor
        if quemGanhouFlor is not None:
            self.modeloRegistro.quemGanhouFlor = quemGanhouFlor
        if quemContraFlor is not None:
            self.modeloRegistro.quemContraFlor = quemContraFlor
        if quemGanhouContraFlor is not None:
            self.modeloRegistro.quemGanhouContraFlor = quemGanhouContraFlor
        if quemContraFlorResto is not None:
            self.modeloRegistro.quemContraFlorResto = quemContraFlorResto
        if quemGanhouContraFlorEnvido is not None:
            self.modeloRegistro.quemGanhouContraFlorEnvido = quemGanhouContraFlorEnvido
        # Atualiza cartas do bot automaticamente se não passadas explicitamente
        if (cartaAltaRobo is None or cartaMediaRobo is None or cartaBaixaRobo is None) and hasattr(self, 'pontuacaoCartas') and hasattr(self, 'maoRank') and self.pontuacaoCartas and self.maoRank:
            try:
                self.modeloRegistro.cartaAltaRobo = self.pontuacaoCartas[self.maoRank.index("Alta")]
                self.modeloRegistro.cartaMediaRobo = self.pontuacaoCartas[self.maoRank.index("Media")]
                self.modeloRegistro.cartaBaixaRobo = self.pontuacaoCartas[self.maoRank.index("Baixa")]
            except Exception:
                pass

    def pedir_truco(self, cbr=None, **game_state):
        self.atualizar_modelo_registro(**game_state)
        """Decide se vai pedir truco (ou aumentar aposta) usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemTruco' in df.columns:
                # 1 = bot pediu truco, 0 = não pediu
                maioria = df['quemTruco'].value_counts().idxmax()
                return maioria == 1
        return self.forcaMao > 40

    def aceitar_truco(self, valor_truco, cbr=None, **game_state):
        self.atualizar_modelo_registro(**game_state)
        """Decide se aceita o truco pedido pelo adversário usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouTruco' in df.columns:
                # 0 = não negou (aceitou), 1 = negou (recusou)
                maioria = df['quemNegouTruco'].value_counts().idxmax()
                return maioria == 0
        # fallback heurístico
        return self.forcaMao > 25

    def pedir_envido(self, cbr=None, **game_state):
        self.atualizar_modelo_registro(**game_state)
        """Decide se vai pedir envido usando CBR se disponível."""
        if self.flor:
            return False
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemEnvidoEnvido' in df.columns:
                maioria = df['quemEnvidoEnvido'].value_counts().idxmax()
                return maioria == 1
        naipes = [carta.retornarNaipe() for carta in self.mao]
        return len(set(naipes)) < 3

    def aceitar_envido(self, valor_envido, cbr=None, **game_state):
        self.atualizar_modelo_registro(**game_state)
        """Decide se aceita o envido pedido pelo adversário usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemNegouEnvido' in df.columns:
                maioria = df['quemNegouEnvido'].value_counts().idxmax()
                return maioria == 0
        return False

    def pedir_flor(self, cbr=None, **game_state):
        self.atualizar_modelo_registro(**game_state)
        """Decide se vai pedir flor usando CBR se disponível."""
        if cbr is not None:
            df = cbr.retornarSimilares(self.modeloRegistro)
            if not df.empty and 'quemFlor' in df.columns:
                maioria = df['quemFlor'].value_counts().idxmax()
                return maioria == 1
        return self.flor

    def registrar_resultado_rodada(self, resultado):
        """Atualiza o estado do bot após cada rodada (ganhou, perdeu, empatou)."""
        self.rodadas += 1
        # Pode adicionar lógica de aprendizado ou ajuste de estratégia

    def registrar_resultado_mao(self, resultado):
        """Atualiza o estado do bot após cada mão (ganhou, perdeu, empatou)."""
        # Pode adicionar lógica de aprendizado ou ajuste de estratégia
        pass

    def resetar_estado_mao(self):
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
