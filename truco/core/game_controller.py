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
        self.rodada_atual = 1

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
        self.rodada_atual = 1

    def jogar_rodada(self, carta1, carta2):
        ganhador = verificar_ganhador_rodada(carta1, carta2)
        if ganhador == carta1:
            self.historico_rodadas.append(1)
            calcular_pontuacao(self.jogador1, 'rodada', 1)
        elif ganhador == carta2:
            self.historico_rodadas.append(2)
            calcular_pontuacao(self.jogador2, 'rodada', 1)
        else:
            self.historico_rodadas.append(0)
        self.rodada_atual += 1
        return ganhador

    def processar_fim_mao(self):
        h = self.historico_rodadas
        if len(h) == 3:
            if h.count(1) > h.count(2):
                calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                return self.jogador1
            elif h.count(2) > h.count(1):
                calcular_pontuacao(self.jogador2, 'mao', self.pontos_truco)
                return self.jogador2
            else:
                return None  # Empate
        return None

    def mostrar_estado(self):
        print(f"\n--- Placar Atual ---")
        print(f"Jogador 1 - {self.jogador1.nome}: {self.jogador1.pontos} pontos")
        print(f"Jogador 2 - {self.jogador2.nome}: {self.jogador2.pontos} pontos")
        print(f"Rodadas vencidas nesta mão: {self.historico_rodadas}")
        print(f"---------------------\n")

    def fim_de_jogo(self):
        return self.jogador1.pontos >= 12 or self.jogador2.pontos >= 12

    def vencedor(self):
        if self.jogador1.pontos >= 12:
            return self.jogador1
        elif self.jogador2.pontos >= 12:
            return self.jogador2
        return None
