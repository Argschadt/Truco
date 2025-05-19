from truco.models.baralho import Baralho
from truco.models.jogador import Jogador
from truco.models.carta import Carta
from truco.core.jogo import Jogo
from truco.bots.cbr_updated import CbrUpdated
from truco.core.rules import verificar_ganhador_rodada, calcular_pontuacao

class GameController:
    def __init__(self, jogador1_nome, jogador2_nome, bot=True):
        self.baralho = Baralho()
        self.jogo = Jogo()
        self.cbr = CbrUpdated()
        self.jogador1 = self.jogo.criarJogador(jogador1_nome, self.baralho)
        if bot:
            self.jogador2 = self.jogo.criarBot(jogador2_nome, self.baralho)
        else:
            self.jogador2 = self.jogo.criarJogador(jogador2_nome, self.baralho)
        self.pontos_truco = 1
        self.historico_rodadas = []
        self.estado = 'inicio'

    def reiniciar_mao(self):
        self.jogador1.resetar()
        self.jogador2.resetar()
        self.baralho.resetarBaralho()
        self.baralho.criarBaralho()
        self.baralho.embaralhar()
        self.jogador1.criarMao(self.baralho)
        self.jogador2.criarMao(self.baralho)
        self.jogo.resetarTrucoPontos()
        self.historico_rodadas = []
        self.resetar_apostas()  # Reset apostas e variáveis de truco/retruco

    def jogar_rodada(self, carta1, carta2, primeiro_jogador, segundo_jogador):
        """
        Joga uma rodada, atualiza o histórico e retorna o ganhador da rodada.
        O histórico registra 1 para self.jogador1, 2 para self.jogador2.
        """
        ganhador = verificar_ganhador_rodada(carta1, carta2)
        if ganhador == carta1:
            if primeiro_jogador == self.jogador1:
                self.historico_rodadas.append(1)
            else:
                self.historico_rodadas.append(2)
        elif ganhador == carta2:
            if segundo_jogador == self.jogador1:
                self.historico_rodadas.append(1)
            else:
                self.historico_rodadas.append(2)
        else:
            self.historico_rodadas.append(0)  # Empate
        return ganhador, None

    def mao_decidida(self):
        """Retorna True se algum jogador já venceu 2 rodadas nesta mão."""
        return self.historico_rodadas.count(1) >= 2 or self.historico_rodadas.count(2) >= 2

    def processar_fim_mao(self):
        h = self.historico_rodadas
        # Garantir que empates são 0, vitórias jogador1 = 1, jogador2 = 2
        # Caso clássico: alguém vence 2 rodadas
        if h.count(1) == 2:
            calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
            return self.jogador1
        if h.count(2) == 2:
            calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
            return self.jogador2
        # Caso: 3 rodadas jogadas
        if len(h) == 3:
            # 3 empates
            if h.count(0) == 3:
                return None
            # 2 empates e 1 vitória
            if h.count(0) == 2:
                if h[0] != 0:
                    # Primeira rodada não foi empate, quem ganhou leva
                    if h[0] == 1:
                        calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                        return self.jogador1
                    elif h[0] == 2:
                        calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                        return self.jogador2
                if h[1] != 0:
                    # Segunda rodada não foi empate, quem ganhou leva
                    if h[1] == 1:
                        calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                        return self.jogador1
                    elif h[1] == 2:
                        calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                        return self.jogador2
                if h[2] != 0:
                    # Terceira rodada não foi empate, quem ganhou leva
                    if h[2] == 1:
                        calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                        return self.jogador1
                    elif h[2] == 2:
                        calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                        return self.jogador2
                return None
            # 1 empate e 2 vitórias diferentes (ex: [1,2,0] ou [2,1,0])
            if h.count(0) == 1 and h.count(1) == 1 and h.count(2) == 1:
                # Quem ganhou a primeira rodada leva
                if h[0] == 1:
                    calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                    return self.jogador1
                elif h[0] == 2:
                    calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                    return self.jogador2
                else:
                    return None
            # 1 vitória para cada e a última decide
            if h.count(1) == 1 and h.count(2) == 1 and h.count(0) == 0:
                if h[2] == 1:
                    calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                    return self.jogador1
                elif h[2] == 2:
                    calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                    return self.jogador2
                else:
                    return None
            # 2 empates e 1 vitória (redundante, já coberto acima)
            # 1 vitória e 2 empates (redundante, já coberto acima)
        return None

    def mostrar_estado(self):
        print(f"Jogador 1 - {self.jogador1.nome}: {self.jogador1.pontos} pontos")
        print(f"Jogador 2 - {self.jogador2.nome}: {self.jogador2.pontos} pontos")

    def pedir_truco(self, quem_pediu):
        # Truco Gaúcho: Truco = 2, Retruco = 3, Vale Quatro = 4
        if self.pontos_truco == 1:
            self.pontos_truco = 2  # Truco
        elif self.pontos_truco == 2:
            self.pontos_truco = 3  # Retruco
        elif self.pontos_truco == 3:
            self.pontos_truco = 4  # Vale Quatro
        self.ultimo_truco = quem_pediu

    def aceitar_truco(self, aceitou):
        # Se recusar, quem pediu ganha apenas 1 ponto (regra correta)
        if not aceitou:
            self.historico_rodadas = []  # Limpa histórico para evitar pontos extras
            if self.ultimo_truco == self.jogador1:
                calcular_pontuacao(self.jogador1, 'mao', 1)
                return self.jogador1
            else:
                calcular_pontuacao(self.jogador2, 'mao', 1)
                return self.jogador2
        return None

    def pedir_envido(self, quem_pediu):
        # Envido só pode ser pedido na primeira rodada
        self.envido_pedido = True
        self.ultimo_envido = quem_pediu

    def aceitar_envido(self, aceitou):
        if not aceitou:
            # Quem pediu envido ganha 1 ponto
            if self.ultimo_envido == self.jogador1:
                calcular_pontuacao(self.jogador1, 'envido', 1)
                return self.jogador1
            else:
                calcular_pontuacao(self.jogador2, 'envido', 1)
                return self.jogador2
        return None

    def pedir_flor(self, quem_pediu):
        self.flor_pedida = True
        self.ultimo_flor = quem_pediu

    def aceitar_flor(self, aceitou):
        if not aceitou:
            # Quem pediu flor ganha 3 pontos
            if self.ultimo_flor == self.jogador1:
                calcular_pontuacao(self.jogador1, 'flor', 3)
                return self.jogador1
            else:
                calcular_pontuacao(self.jogador2, 'flor', 3)
                return self.jogador2
        return None

    def resetar_apostas(self):
        self.pontos_truco = 1
        self.envido_pedido = False
        self.flor_pedida = False
        self.ultimo_truco = None
        self.ultimo_envido = None
        self.ultimo_flor = None

    def fim_de_jogo(self):
        # Truco Gaúcho: vence quem chega a 12 pontos
        return self.jogador1.pontos >= 12 or self.jogador2.pontos >= 12

    def determinar_vencedor(self):
        if self.jogador1.pontos >= 12 and self.jogador2.pontos >= 12:
            return self.jogador1 if self.jogador1.pontos > self.jogador2.pontos else self.jogador2
        elif self.jogador1.pontos >= 12:
            return self.jogador1
        elif self.jogador2.pontos >= 12:
            return self.jogador2
        return None

    def definir_proximo_primeiro(self, jogador):
        """Define quem será o primeiro jogador da próxima mão."""
        self.proximo_primeiro = jogador
