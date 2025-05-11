from baralho import Baralho
from jogador import Jogador
from bot import Bot
import random
from pontos import MANILHA, CARTAS_VALORES

class Jogo():

    def __init__(self):
        self.rodadas = []
        self.trucoPontos = 1
    
    def iniciarJogo(self):
        pass

    def criarJogador(self, nome, baralho):
        jogador = Jogador(nome)
        jogador.criarMao(baralho)
        return jogador

    def criarBot(self, nome, baralho):
        bot = Bot(nome)
        bot.criarMao(baralho)
        return bot

    def verificarGanhador(self, carta1, carta2):
        # print("numeros: ")
        # print(str(carta1.numero))
        # print(str(carta2.numero))
        ganhador = self.verificarCartaVencedora(carta1, carta2)
        print(ganhador)
        return ganhador
        # if self.verificarCartaVencedora(carta1, carta2) is None:
        #     if carta1.numero == carta2.numero:
        #         ganhador = "Empate"
        #     elif CARTAS_VALORES[str(carta1.numero)] > CARTAS_VALORES[str(carta2.numero)]:
        #         ganhador = carta1
        #     else:
        #         ganhador = carta2
        #     print(ganhador)
        #     return ganhador
        # else:
        #     return self.verificarCartaVencedora(carta1, carta2)

    
    def adicionarPonto(self, jogador1, jogador2, carta1, carta2, ganhador):
        if ganhador == "Empate":
            # jogador1.adicionarPonto()
            # jogador2.adicionarPonto()
            return "Empate"
        
        elif ganhador == carta1:
            jogador1.adicionarPonto()
            ganhador.printarCarta()
        
        elif ganhador == carta2:
            jogador2.adicionarPonto()
            ganhador.printarCarta()
        
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
        if (str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe) in MANILHA and (str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe) in MANILHA:
            if MANILHA[str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe] > MANILHA[str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe]:
                return carta_jogador_01
           
            elif MANILHA[str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe] > MANILHA[str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe]:
                return carta_jogador_02
        
        elif (str(carta_jogador_01.numero)+" de "+carta_jogador_01.naipe) in MANILHA:
            return carta_jogador_01
        
        elif (str(carta_jogador_02.numero)+" de "+carta_jogador_02.naipe) in MANILHA:
            return carta_jogador_02
        
        else:
            if CARTAS_VALORES[str(carta_jogador_01.numero)] >= CARTAS_VALORES[str(carta_jogador_02.numero)]:
                return carta_jogador_01
        
            elif CARTAS_VALORES[str(carta_jogador_01.retornarNumero())] < CARTAS_VALORES[str(carta_jogador_02.retornarNumero())]:
                return carta_jogador_02
        
            else:
                return "Empate"
    

    def trucoAceito(self, aceitou):
        print("Truco")
        if(aceitou is False and self.trucoPontos == 1):
            self.trucoPontos = 1
            
        elif(aceitou is False and self.trucoPontos != 1):
            self.trucoPontos -= 1

        elif(self.trucoPontos == 1):
            self.trucoPontos += 1
        
        else:
            self.trucoPontos +=2
    
    def retornaTrucoPontos(self):
        return self.trucoPontos
    
    def resetarTrucoPontos(self):
        self.trucoPontos = 1