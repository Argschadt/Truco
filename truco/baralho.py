from carta import Carta
import random


class Baralho():
    
    def __init__(self):
        # self.vira = []
        self.manilhas = []
        self.cartas = []
        self.criarBaralho() 

    def criarBaralho(self):
        for i in ["ESPADAS", "OUROS", "COPAS", "BASTOS"]:
            for n in range(1, 13):
                if n < 8 or n >= 10:
                    self.cartas.append(Carta(n, i))
    
    def embaralhar(self):
        random.shuffle(self.cartas)

    def retirarCarta(self):
        return self.cartas.pop()
    
    def resetarBaralho(self):
        self.vira = []
        self.manilhas = []
        self.cartas = []

    def printarVira(self):
        for v in self.vira:
            v.printarCarta()

    def printarManilhas(self):
        for m in self.manilhas:
            m.printarCarta()
    
    def printarBaralho(self):
        for c in self.cartas:
            c.printarCarta()