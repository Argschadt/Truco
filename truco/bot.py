import random 
import pandas as pd

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
        self.modeloRegistro = pd.read_csv('../modelo_registro.csv', index_col='idMao')

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
        df = cbr.retornarSimilares(self.modeloRegistro)
        carta_escolhida = 0
        ordem_carta_jogada = 'CartaRobo'

        if (len(self.indices) == 3): ordem_carta_jogada = 'primeira' + ordem_carta_jogada
        elif (len(self.indices) == 2): ordem_carta_jogada = 'segunda' + ordem_carta_jogada
        elif (len(self.indices) == 1): ordem_carta_jogada = 'terceira' + ordem_carta_jogada

        for i in reversed(range(len(df[ordem_carta_jogada].value_counts().index.to_list()))): 
            aux = df[ordem_carta_jogada].value_counts().index.to_list()[i]
            
            if(carta_escolhida in self.pontuacaoCartas):
                carta_escolhida = aux

        if(carta_escolhida == 0):
            valor_referencia = df[ordem_carta_jogada].value_counts().index.to_list()[0]
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
        

    def adicionarPonto(self):
        self.pontos += 1
    
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
            print('Flor do Bot!')
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


    # def caseBasedReasoning(self):
        