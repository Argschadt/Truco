class Jogador():

    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.maoRank = []
        self.pontos = 0
        self.rodadas = 0
        self.invido = 0
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediuTruco = False

    def mostrarOpcoes(self):
        self.mostrarMao()
        if (self.pediuTruco is False): 
            print('[4] Truco')
        if ((len(self.mao)) == 3 and self.flor is False and (self.checaFlor())):
            print('[5] Flor')
            self.flor = True

    def criarMao(self, baralho):
        for i in range(3):
            self.mao.append(baralho.retirarCarta())  

    def jogarCarta(self, carta_escolhida):
        return self.mao.pop(carta_escolhida)
    
    def mostrarMao(self):
        i = 0
        for carta in self.mao:
            carta.printarCarta(i)
            i += 1
        cartas = [(f"{carta.numero} de {carta.naipe}") for carta in self.mao]
        # print(cartas)
        # print('\n'.join(map('  '.join, zip(*(carta.desenharCarta(c) for c in cartas)))))

    def adicionarPonto(self):
        self.pontos += 1
    
    def adicionarRodada(self, rodadas):
        self.rodadas += rodadas
    
    def resetar(self):
        self.pontos = 0
        self.mao = []
        self.flor = False
        self.pediuTruco = False

    def checaMao(self):
        return self.mao
    
    def calculaInvido(self):
        self.invido += 1
    
    def checaFlor(self):
        if all(carta.retornarNaipe() == self.mao[0].retornarNaipe() for carta in self.mao):
            # print('Flor do Jogador')
            return True
        return False