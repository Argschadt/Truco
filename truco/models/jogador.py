from truco.models.carta import Carta
from truco.models.baralho import Baralho

class Jogador():

    def __init__(self, nome):
        self.nome = nome
        self.mao = []
        self.maoRank = []
        self.pontos = 0
        self.invido = 0
        self.primeiro = False
        self.ultimo = False
        self.flor = False
        self.pediuTruco = False

    def mostrarOpcoes(self):
        self.mostrarMao()
        if self.pediuTruco is False:
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

    def adicionarPonto(self, valor=1):
        self.pontos += valor
    
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

    def aceitar_truco(self, valor_truco):
        resp = input(f"Seu oponente pediu Truco (vale {valor_truco} pontos). Aceita? [s/n]: ").strip().lower()
        return resp == 's'

    def aceitar_envido(self, valor_envido):
        resp = input(f"Seu oponente pediu Envido (vale {valor_envido} pontos). Aceita? [s/n]: ").strip().lower()
        return resp == 's'

    def aceitar_flor(self):
        resp = input(f"Seu oponente pediu Flor (vale 3 pontos). Aceita? [s/n]: ").strip().lower()
        return resp == 's'

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
            # Se não houver 2 cartas do mesmo naipe, pega o maior valor de envido isolado
            max_envido = max([v for sub in naipes.values() for v in sub])
        return max_envido