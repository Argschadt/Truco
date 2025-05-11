import itertools
from pontos import MANILHA, CARTAS_VALORES

class Carta():

    def __init__(self, numero, naipe):
        self.numero = numero
        self.naipe = naipe

    # def verificarCarta(self, carta_01, carta_02):
    #     if self.CARTAS_VALORES[str(carta_01.numero)] > self.CARTAS_VALORES[str(carta_02.numero)]:
    #         return carta_01
    #     elif self.CARTAS_VALORES[str(carta_01.retornarNumero())] < self.CARTAS_VALORES[str(carta_02.retornarNumero())]:
    #         return carta_02
    #     else:
    #         return "Empate"

    # def verificarCarta(self, carta_01, carta_02):
    #     print(1)
    #     if (str(carta_01.numero)+" de "+carta_01.naipe) in self.MANILHA and (str(carta_02.numero)+" de "+carta_02.naipe) in self.MANILHA:
    #         print(2)
    #         if self.MANILHA[str(carta_01.numero)+" de "+carta_01.naipe] > self.MANILHA[str(carta_02.numero)+" de "+carta_02.naipe]:
    #             return carta_01
    #             print(3)
    #         elif self.MANILHA[str(carta_02.numero)+" de "+carta_02.naipe] > self.MANILHA[str(carta_01.numero)+" de "+carta_01.naipe]:
    #             return carta_02
    #             print(4)
    #     elif (str(carta_01.numero)+" de "+carta_01.naipe) in self.MANILHA:
    #         return carta_01
    #         print(5)
    #     elif (str(carta_02.numero)+" de "+carta_02.naipe) in self.MANILHA:
    #         return carta_02
    #         print(6)
    #     else:
    #         if self.CARTAS_VALORES[str(carta_01.numero)] > self.CARTAS_VALORES[str(carta_02.numero)]:
    #             return carta_01
    #         elif self.CARTAS_VALORES[str(carta_01.retornarNumero())] < self.CARTAS_VALORES[str(carta_02.retornarNumero())]:
    #             return carta_02
    #         else:
    #             return "Empate"

    def verificarCartaAlta(self, carta_01, carta_02):
        if (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA and (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            if MANILHA[str(carta_01.numero)+" de "+carta_01.naipe] > MANILHA[str(carta_02.numero)+" de "+carta_02.naipe]:
                return carta_01
            elif MANILHA[str(carta_02.numero)+" de "+carta_02.naipe] > MANILHA[str(carta_01.numero)+" de "+carta_01.naipe]:
                return carta_02
        elif (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA:
            print('in manilha')
            return carta_01
        elif (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            print('in manilha')
            return carta_02
        else:
            if CARTAS_VALORES[str(carta_01.numero)] > CARTAS_VALORES[str(carta_02.numero)]:
                return carta_01
            else:
                return carta_02
        return carta_01
        
    def verificarCartaBaixa(self, carta_01, carta_02):
        if (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA and (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            if MANILHA[str(carta_01.numero)+" de "+carta_01.naipe] < MANILHA[str(carta_02.numero)+" de "+carta_02.naipe]:
                return carta_01
            elif MANILHA[str(carta_02.numero)+" de "+carta_02.naipe] < MANILHA[str(carta_01.numero)+" de "+carta_01.naipe]:
                return carta_02
        elif (str(carta_01.numero)+" de "+carta_01.naipe) in MANILHA:
            return carta_02
        elif (str(carta_02.numero)+" de "+carta_02.naipe) in MANILHA:
            return carta_01
        else:
            if CARTAS_VALORES[str(carta_01.numero)] < CARTAS_VALORES[str(carta_02.numero)]:
                return carta_01
            else:
                return carta_02
        return carta_01

    def cartaManilha(self, carta):
        if(((carta.numero)+" de "+carta.naipe) in self.MANILHA):
            return True
        return False

    
    def retornarPontosCarta(self, carta):
        if (str(carta.numero)+" de "+carta.naipe) in MANILHA:
            return MANILHA[str(carta.numero)+" de "+carta.naipe]
        else:
            return CARTAS_VALORES[str(carta.numero)]

    def classificarCarta(self, cartas):
        carta_alta = self.verificarCartaAlta(self.verificarCartaAlta(cartas[0], cartas[1]), cartas[2])
        carta_baixa = self.verificarCartaBaixa(self.verificarCartaBaixa(cartas[0], cartas[1]), cartas[2])
        lista_classificacao = ['', '', '']
        lista_pontos = ['', '', '']
        
        for i in range(len(lista_classificacao)):
            if carta_alta == cartas[i]: 
                lista_classificacao[i] = 'Alta'
                lista_pontos[i] = self.retornarPontosCarta(cartas[i])
            
            if carta_baixa == cartas[i]: 
                lista_classificacao[i] = 'Baixa'
                lista_pontos[i] = self.retornarPontosCarta(cartas[i])
            
            if not lista_classificacao[i]: 
                lista_classificacao[i] = 'Media'
                lista_pontos[i] = self.retornarPontosCarta(cartas[i])


        return lista_pontos, lista_classificacao

    def printarCarta(self, i=None):
        if i == None:
            i = ""
        if self.numero == 1 and self.naipe == 'Espadas':
            print(f"[{i}] ESPADÃO +")
        elif self.numero == 1 and self.naipe == 'Bastos':
            print(f"[{i}] BASTIÃO +")
        elif self.numero == 7 and self.naipe == 'Espadas':
            print(f"[{i}] Sete de espadas +")
        elif self.numero == 7 and self.naipe == 'Ouros':
            print(f"[{i}] Sete de Ouros +")
        else:
            print(f"[{i}] {self.numero} de {self.naipe}")

    def retornarNumero(self):
        return self.numero
    
    def retornarNaipe(self):
        return self.naipe

    def desenharCarta(self, s):
        l_mostrar_carta = [] 
        l_mostrar_carta.append("┌─────────┐")
        l_mostrar_carta.append("│{}{}. . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . {}. .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . . . .│")
        l_mostrar_carta.append("│. . .{}{}│")
        l_mostrar_carta.append("└─────────┘")

        x = ("│.", s[:1], ". . . .│")
        l_mostrar_carta[1] = "".join(x)

        x = ("│. . . .", s[:1], ".│")
        l_mostrar_carta[7] = "".join(x)
        
        #  ["Espadas", "Ouros", "Copas", "Espadas"]
        if "OUROS" in s:
            l_mostrar_carta[4] = "│. . ♦ . .│"
        if "BASTOS" in s:
            l_mostrar_carta[4] = "│. . ♣ . .│"
        if "COPAS" in s:
            l_mostrar_carta[4] = "│. . ♥ . .│"
        if "ESPADAS" in s:
            l_mostrar_carta[4] = "│. . ♠ . .│"

        return l_mostrar_carta
