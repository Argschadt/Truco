from truco.models.carta import Carta
from truco.models.baralho import Baralho
from truco.models.jogador import Jogador
from truco.bots.bot import Bot
from truco.utils.pontos import MANILHA, CARTAS_VALORES
from truco.core.rules import verificar_ganhador_rodada
import random

class Jogo():

    def __init__(self):
        self.rodadas = []
        self.trucoPontos = 1
        self.historico_rodadas = []  # Adicionado para controle do histórico das rodadas
    
    def iniciarJogo(self):
        pass

    def criarJogador(self, nome, baralho):
        jogador = Jogador(nome)
        jogador.criarMao(baralho)
        return jogador

    def criarBot(self, nome, baralho):
        bot = Bot(nome)
        #bot.criarMao(baralho)
        return bot

    def verificarGanhador(self, carta1, carta2):
        ganhador = self.verificarCartaVencedora(carta1, carta2)
        return ganhador

    
    def adicionarPonto(self, jogador1, jogador2, carta1, carta2, ganhador):
        if ganhador == "Empate":
            # Não soma ponto para ninguém, apenas retorna Empate
            return "Empate"
        
        elif ganhador == carta1:
            jogador1.adicionarPonto()
        elif ganhador == carta2:
            jogador2.adicionarPonto()
        else:
            return "Erro"

    def quemJogaPrimeiro(self, jogador1, jogador2, carta1, carta2, ganhador):
        if carta1 == ganhador:
            jogador1.primeiro = True
            jogador2.primeiro = False
        
        elif carta2 == ganhador:
            jogador1.primeiro = False
            jogador2.primeiro = True
        
        elif ganhador == "Empate":
            pass

    def quemIniciaRodada(self, jogador1, jogador2):
        if jogador1.pontos == 0 and jogador2.pontos == 0:
            if jogador1.ultimo == True:
                jogador2.ultimo = True
                jogador1.ultimo = False
                jogador1.primeiro = True
                jogador2.primeiro = False
            
            elif jogador2.ultimo == True:
                jogador2.ultimo = False
                jogador1.primeiro = False
                jogador2.primeiro = True

    def verificarCartaVencedora(self, carta_jogador_01, carta_jogador_02):
        return verificar_ganhador_rodada(carta_jogador_01, carta_jogador_02)
    

    def trucoAceito(self, aceitou):
        if aceitou:
            # Truco aceito: aumenta para 3 pontos, ou dobra se já foi aumentado
            if self.trucoPontos == 1:
                self.trucoPontos = 3
            else:
                self.trucoPontos *= 2
        else:
            # Truco recusado: mantém pontuação mínima para quem pediu
            if self.trucoPontos == 1:
                self.trucoPontos = 1
            else:
                self.trucoPontos -= 1
    
    def retornaTrucoPontos(self):
        return self.trucoPontos
    
    def resetarTrucoPontos(self):
        self.trucoPontos = 1

    def resetarHistoricoRodadas(self):
        self.historico_rodadas = []