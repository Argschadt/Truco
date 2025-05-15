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
        
        # Mudar forma de classificação dos dados vindos da base de casos, para ter uma métrica extra de inserção
        for i in range(3):
            self.mao.append(baralho.retirarCarta())
        self.flor = self.checaFlor()
        self.pontuacaoCartas, self.maoRank = self.mao[0].classificarCarta(self.mao)
        self.forcaMao = sum(self.pontuacaoCartas)
        self.inicializarRegistro()
    
    def jogarCarta(self, cbr):
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

    # --- Métodos essenciais para Truco Gaúcho ---
    def pedir_truco(self, estado_jogo=None):
        """Decide se vai pedir truco (ou aumentar aposta). Pode usar heurística ou CBR."""
        # Exemplo simples: pede truco se a mão for forte
        return self.forcaMao > 40

    def aceitar_truco(self, valor_truco, estado_jogo=None):
        """Decide se aceita o truco pedido pelo adversário."""
        # Exemplo simples: aceita se a mão for razoável
        return self.forcaMao > 25

    def pedir_envido(self, estado_jogo=None):
        """Decide se vai pedir envido."""
        # Exemplo simples: pede envido se tem duas cartas do mesmo naipe
        naipes = [carta.retornarNaipe() for carta in self.mao]
        return len(set(naipes)) < 3

    def aceitar_envido(self, valor_envido, estado_jogo=None):
        """Decide se aceita o envido pedido pelo adversário."""
        # Exemplo simples: aceita se tem pelo menos 25 pontos de envido
        return self.calcular_pontos_envido() >= 25

    def pedir_flor(self, estado_jogo=None):
        """Decide se vai pedir flor."""
        return self.flor

    def aceitar_flor(self, estado_jogo=None):
        """Decide se aceita a flor do adversário."""
        # Exemplo simples: sempre aceita
        return True

    def decidir_correr_mao_de_onze(self, estado_jogo=None):
        """Decide se corre ou joga a mão de onze."""
        # Exemplo simples: corre se a mão for muito ruim
        return self.forcaMao < 20

    def decidir_escurinho(self, estado_jogo=None):
        """Decide como jogar no escurinho (mão de onze especial)."""
        # Exemplo: joga normalmente, pode ser expandido
        return True

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
