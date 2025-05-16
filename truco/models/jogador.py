from truco.models.carta import Carta
from truco.models.baralho import Baralho
import random

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
        # Ensure jogador1 (Heitor) always gets a "flor" (3 cards of the same suit)
        if self.nome == 'Heitor':
            # Get all available suits in the deck
            available_suits = list(set(carta.naipe for carta in baralho.cartas))
            if available_suits:
                chosen_suit = random.choice(available_suits)
                
                # Find all cards of the chosen suit
                suit_cards = [carta for carta in baralho.cartas if carta.naipe == chosen_suit]
                
                # If we have at least 3 cards of the chosen suit, use them
                if len(suit_cards) >= 3:
                    # Remove these cards from the deck
                    for carta in suit_cards[:3]:
                        baralho.cartas.remove(carta)
                    
                    # Add them to the player's hand
                    self.mao.extend(suit_cards[:3])
                    
                    # Flag that we have a flor
                    self.flor = True
                    return
            
            # Fallback: Standard hand creation if we couldn't create a flor
            print("Warning: Couldn't create a flor for Heitor, using random cards instead.")
            
        # Standard hand creation for other players or fallback
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
        # NÃO zera os pontos!
        self.mao = []
        self.flor = False
        self.pediuTruco = False
        # ...outros estados temporários se necessário...

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

    def pedir_envido(self, estado_jogo=None):
        # Não pede Envido se tiver Flor
        if self.flor:
            return False
        naipes = [carta.retornarNaipe() for carta in self.mao]
        return len(set(naipes)) < 3