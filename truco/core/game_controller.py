from truco.models.baralho import Baralho
from truco.models.jogador import Jogador
from truco.models.carta import Carta
from truco.core.jogo import Jogo
from truco.bots.cbr_updated import CbrUpdated
from truco.core.rules import verificar_ganhador_rodada, calcular_pontuacao
from truco.models.modelo_registro import ModeloRegistro

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
        # Novos atributos para rastrear estados do modeloRegistro
        self.quemTruco = 0
        self.quemNegouTruco = 0
        self.quemGanhouTruco = 0
        self.quemRetruco = 0
        self.quemGanhouRetruco = 0
        self.quemValeQuatro = 0
        self.quemGanhouValeQuatro = 0
        self.quemNegouEnvido = 0
        self.quemGanhouEnvido = 0
        self.quemPediuRealEnvido = 0
        self.quemPediuFaltaEnvido = 0
        self.quemFlor = 0
        self.quemGanhouFlor = 0
        self.quemContraFlor = 0
        self.quemContraFlorResto = 0
        self.modeloRegistro = ModeloRegistro()

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
        cartas_vistas = set()
        for carta in self.jogador1.mao + self.jogador2.mao:
            chave = f"{carta.numero}_{carta.naipe}"
            if chave in cartas_vistas:
                print(f"❌ CARTA DUPLICADA: {chave}")
            else:
                cartas_vistas.add(chave)
        
        # Inicializar arrays de cartas jogadas
        self.inicializar_arrays_cartas_jogadas()
    
    def verificar_cartas_duplicadas(self):
        cartas_humano = [(c.numero, c.naipe) for c in self.jogador1.mao]
        cartas_bot = [(c.numero, c.naipe) for c in self.jogador2.mao]
        duplicadas = set(cartas_humano).intersection(cartas_bot)
        if duplicadas:
            print("⚠️ AVISO: CARTA DUPLICADA DETECTADA:", duplicadas)
    

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
        """Retorna True se a mão já foi decidida por qualquer critério válido (2 vitórias, 2x0, 3 rodadas, empate, etc)."""
        h = self.historico_rodadas
        # Alguém venceu 2 rodadas
        if h.count(1) == 2 or h.count(2) == 2:
            return True
        # Duas rodadas jogadas e ambas vencidas pelo mesmo jogador (2x0)
        if len(h) == 2 and h[0] == h[1] and h[0] in [1, 2]:
            return True
        # Duas rodadas jogadas, uma vitória e um empate (ex: [1,0] ou [2,0])
        if len(h) == 2 and (h.count(1) == 1 and h.count(0) == 1 or h.count(2) == 1 and h.count(0) == 1):
            return True
        # Três rodadas jogadas (independente do resultado)
        if len(h) == 3:
            return True
        # Três empates
        if len(h) == 3 and h.count(0) == 3:
            return True
        # Empate total (ex: [1,2,1] e [2,1,2] não são empates, mas [1,2,0] pode ser)
        if len(h) == 3 and h.count(1) == h.count(2):
            return True
        return False

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
        # Caso: 2 rodadas jogadas, uma vitória e um empate
        if len(h) == 2:
            if h.count(1) == 1 and h.count(0) == 1:
                calcular_pontuacao(self.jogador1, 'mao', self.pontos_truco)
                return self.jogador1
            if h.count(2) == 1 and h.count(0) == 1:
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
            self.quemTruco = 1 if quem_pediu == self.jogador1 else 2
        elif self.pontos_truco == 2:
            self.pontos_truco = 3  # Retruco
            self.quemRetruco = 1 if quem_pediu == self.jogador1 else 2
        elif self.pontos_truco == 3:
            self.pontos_truco = 4  # Vale Quatro
            self.quemValeQuatro = 1 if quem_pediu == self.jogador1 else 2
        self.ultimo_truco = quem_pediu
        
    
    # Método considerando pontos para o tipo de truco negado
        
    def aceitar_truco(self, aceitou):
        # Se recusar, quem pediu ganha pontos baseados no nível do truco
        if not aceitou:
            self.historico_rodadas = []  # Limpa histórico para evitar pontos extras
            pontos_ganhos = 1  # Padrão: Truco negado dá 1 ponto
            if self.pontos_truco == 3:  # Retruco negado
                pontos_ganhos = 2
            elif self.pontos_truco == 4:  # Vale Quatro negado
                pontos_ganhos = 3

            if self.ultimo_truco == self.jogador1:
                self.quemNegouTruco = 2  # Jogador 2 negou
                calcular_pontuacao(self.jogador1, 'mao', pontos_ganhos)
                return self.jogador1
            else:
                self.quemNegouTruco = 1  # Jogador 1 negou
                calcular_pontuacao(self.jogador2, 'mao', pontos_ganhos)
                return self.jogador2
        return None

    #def aceitar_truco(self, aceitou):
    #    # Se recusar, quem pediu ganha apenas 1 ponto (regra correta)
    #    if not aceitou:
    #        self.historico_rodadas = []  # Limpa histórico para evitar pontos extras
    #        if self.ultimo_truco == self.jogador1:
    #            self.quemNegouTruco = 2  # Jogador 2 negou
    #            calcular_pontuacao(self.jogador1, 'mao', 1)
    #            return self.jogador1
    #        else:
    #            self.quemNegouTruco = 1  # Jogador 1 negou
    #            calcular_pontuacao(self.jogador2, 'mao', 1)
    #            return self.jogador2
    #    return None

    def pedir_envido(self, quem_pediu, tp_envido):
        # Envido só pode ser pedido na primeira rodada
        self.envido_pedido = True
        self.ultimo_envido = quem_pediu
        if tp_envido == 1:  # Envido
            self.modeloRegistro.quemPediuEnvido = 2 if quem_pediu == self.jogador1 else 1
        elif tp_envido == 2:  # Real Envido
            self.modeloRegistro.quemPediuRealEnvido = 2 if quem_pediu == self.jogador1 else 1
        elif tp_envido == 3:  # Falta Envido
            self.modeloRegistro.quemPediuFaltaEnvido = 2 if quem_pediu == self.jogador1 else 1

    def aceitar_envido(self, aceitou):
        if not aceitou:
            # Quem pediu envido ganha 1 ponto
            if self.ultimo_envido == self.jogador1:
                self.quemNegouEnvido = 2  # Jogador 2 negou
                calcular_pontuacao(self.jogador1, 'envido', 1)
                return self.jogador1
            else:
                self.quemNegouEnvido = 1  # Jogador 1 negou
                calcular_pontuacao(self.jogador2, 'envido', 1)
                return self.jogador2
        return None
    
    def recusar_envido(self, quem_pediu, tp_envido):
        """Registra recusa de envido."""
        self.envido_pedido = True
        self.modeloRegistro.quemNegouEnvido = 2 if quem_pediu == self.jogador1 else 1

    def pedir_flor(self, quem_pediu):
        """Registra pedido de flor."""
        self.flor_pedida = True
        self.quemFlor = 1 if quem_pediu == self.jogador1 else 2
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
        # Resetar também os novos atributos
        self.quemNegouTruco = 0
        self.quemGanhouRetruco = 0
        self.quemGanhouValeQuatro = 0
        self.quemNegouEnvido = 0

    def fim_de_jogo(self):
        # Truco Gaúcho: vence quem chega a 30 pontos
        return self.jogador1.pontos >= 30 or self.jogador2.pontos >= 30

    def determinar_vencedor(self):
        if self.jogador1.pontos >= 30 and self.jogador2.pontos >= 30:
            return self.jogador1 if self.jogador1.pontos > self.jogador2.pontos else self.jogador2
        elif self.jogador1.pontos >= 30:
            return self.jogador1
        elif self.jogador2.pontos >= 30:
            return self.jogador2
        return None

    def definir_proximo_primeiro(self, jogador):
        """Define quem será o primeiro jogador da próxima mão."""
        self.proximo_primeiro = jogador

    def atualizar_modelo_registro(self):
        # Inicializar arrays de cartas jogadas se não existirem
        if not hasattr(self.jogador1, 'cartas_jogadas_humano'):
            self.jogador1.cartas_jogadas_humano = [0, 0, 0]
        if not hasattr(self.jogador2, 'cartas_jogadas_robo'):
            self.jogador2.cartas_jogadas_robo = [0, 0, 0]
            
        # Cartas jogadas pelo bot - verificar se a lista tem elementos suficientes
        if hasattr(self.jogador2, 'cartas_jogadas_robo') and len(self.jogador2.cartas_jogadas_robo) >= 3:
            self.modeloRegistro.primeiraCartaRobo = self.jogador2.cartas_jogadas_robo[0]
            self.modeloRegistro.segundaCartaRobo = self.jogador2.cartas_jogadas_robo[1]
            self.modeloRegistro.terceiraCartaRobo = self.jogador2.cartas_jogadas_robo[2]
        else:
            # Preencher com valores padrão se não houver cartas suficientes
            cartas_robo = getattr(self.jogador2, 'cartas_jogadas_robo', [0, 0, 0])
            self.modeloRegistro.primeiraCartaRobo = cartas_robo[0] if len(cartas_robo) > 0 else 0
            self.modeloRegistro.segundaCartaRobo = cartas_robo[1] if len(cartas_robo) > 1 else 0
            self.modeloRegistro.terceiraCartaRobo = cartas_robo[2] if len(cartas_robo) > 2 else 0
            
        # Cartas jogadas pelo humano - verificar se a lista tem elementos suficientes
        if hasattr(self.jogador1, 'cartas_jogadas_humano') and len(self.jogador1.cartas_jogadas_humano) >= 3:
            self.modeloRegistro.primeiraCartaHumano = self.jogador1.cartas_jogadas_humano[0]
            self.modeloRegistro.segundaCartaHumano = self.jogador1.cartas_jogadas_humano[1]
            self.modeloRegistro.terceiraCartaHumano = self.jogador1.cartas_jogadas_humano[2]
        else:
            # Preencher com valores padrão se não houver cartas suficientes
            cartas_humano = getattr(self.jogador1, 'cartas_jogadas_humano', [0, 0, 0])
            self.modeloRegistro.primeiraCartaHumano = cartas_humano[0] if len(cartas_humano) > 0 else 0
            self.modeloRegistro.segundaCartaHumano = cartas_humano[1] if len(cartas_humano) > 1 else 0
            self.modeloRegistro.terceiraCartaHumano = cartas_humano[2] if len(cartas_humano) > 2 else 0
            
        # Rodadas - verificar se o histórico tem elementos suficientes
        if len(self.historico_rodadas) > 0:
            if self.historico_rodadas[0] == 1:
                self.modeloRegistro.ganhadorPrimeiraRodada = 2
            elif self.historico_rodadas[0] == 2:
                self.modeloRegistro.ganhadorPrimeiraRodada = 1
        else:
            self.modeloRegistro.ganhadorPrimeiraRodada = 0
            
        if len(self.historico_rodadas) > 1:
            if self.historico_rodadas[1] == 1:
                self.modeloRegistro.ganhadorSegundaRodada = 2
            elif self.historico_rodadas[1] == 2:
                self.modeloRegistro.ganhadorSegundaRodada = 1
        else:
            self.modeloRegistro.ganhadorSegundaRodada = 0
            
        if len(self.historico_rodadas) > 2:
            if self.historico_rodadas[2] == 1:
                self.modeloRegistro.ganhadorTerceiraRodada = 2
            elif self.historico_rodadas[2] == 2:
                self.modeloRegistro.ganhadorTerceiraRodada = 1
        else:
            self.modeloRegistro.ganhadorTerceiraRodada = 0
        
        # Truco - usar valores padrão se atributos não existirem
        if (self.quemTruco == 1):
            self.modeloRegistro.quemTruco = 2
        elif (self.quemTruco == 2):
            self.modeloRegistro.quemTruco = 1
        else:
            self.modeloRegistro.quemTruco = 0
        
        if (self.quemNegouTruco == 1):
            self.modeloRegistro.quemNegouTruco = 2
        elif (self.quemNegouTruco == 2):
            self.modeloRegistro.quemNegouTruco = 1
        else:
            self.modeloRegistro.quemNegouTruco = 0
        
        if (self.quemGanhouTruco == 1):
            self.modeloRegistro.quemGanhouTruco = 2
        elif (self.quemGanhouTruco == 2):
            self.modeloRegistro.quemGanhouTruco = 1
        else:
            self.modeloRegistro.quemGanhouTruco = 0
            
        if self.quemRetruco == 1:
            self.modeloRegistro.quemRetruco = 2
        elif self.quemRetruco == 2:
            self.modeloRegistro.quemRetruco = 1
        else:
            self.modeloRegistro.quemRetruco = 0
            
        if self.quemGanhouRetruco == 1:
            self.modeloRegistro.quemGanhouRetruco = 2
        elif self.quemGanhouRetruco == 2:
            self.modeloRegistro.quemGanhouRetruco = 1
        else:
            self.modeloRegistro.quemGanhouRetruco = 0
            
        if self.quemValeQuatro == 1:
            self.modeloRegistro.quemValeQuatro = 2
        elif self.quemValeQuatro == 2:
            self.modeloRegistro.quemValeQuatro = 1
        else:
            self.modeloRegistro.quemValeQuatro = 0
            
        if self.quemGanhouValeQuatro == 1:
            self.modeloRegistro.quemGanhouValeQuatro = 2
        elif self.quemGanhouValeQuatro == 2:
            self.modeloRegistro.quemGanhouValeQuatro = 1
        else:
            self.modeloRegistro.quemGanhouValeQuatro = 0
        
        # Envido 
        self.modeloRegistro.pontosEnvidoRobo = self.jogador2.calcular_pontos_envido()
        
        
        if hasattr(self, 'ultimo_envido'):
            if self.ultimo_envido == self.jogador1:
                self.modeloRegistro.quemPediuEnvido = 2
            elif self.ultimo_envido == self.jogador2:
                self.modeloRegistro.quemPediuEnvido = 1
            else:
                self.modeloRegistro.quemPediuEnvido = 0
        else:
            self.modeloRegistro.quemPediuEnvido = 0
        
        if self.quemGanhouEnvido == 1:
            self.modeloRegistro.quemGanhouEnvido = 2
        elif self.quemGanhouEnvido == 2:
            self.modeloRegistro.quemGanhouEnvido = 1
        else:
            self.modeloRegistro.quemGanhouEnvido = 0
            
        if self.quemNegouEnvido == 1:
            self.modeloRegistro.quemNegouEnvido = 2
        elif self.quemNegouEnvido == 2:
            self.modeloRegistro.quemNegouEnvido = 1
        else:
            self.modeloRegistro.quemNegouEnvido = 0
        
        if self.quemPediuRealEnvido == 1:
            self.modeloRegistro.quemPediuRealEnvido = 2
        elif self.quemPediuRealEnvido == 2:
            self.modeloRegistro.quemPediuRealEnvido = 1
        else:
            self.modeloRegistro.quemPediuRealEnvido = 0
        
        if self.quemPediuFaltaEnvido == 1:
            self.modeloRegistro.quemPediuFaltaEnvido = 2
        elif self.quemPediuFaltaEnvido == 2:
            self.modeloRegistro.quemPediuFaltaEnvido = 1
        else:
            self.modeloRegistro.quemPediuFaltaEnvido = 0
        
        # Flor
        if self.quemFlor == 1:
            self.modeloRegistro.quemFlor = 2
        elif self.quemFlor == 2:
            self.modeloRegistro.quemFlor = 1
        else:
            self.modeloRegistro.quemFlor = 0
        if hasattr(self, 'quemGanhouFlor'):
            if self.quemGanhouFlor == 1:
                self.modeloRegistro.quemGanhouFlor = 2
            elif self.quemGanhouFlor == 2:
                self.modeloRegistro.quemGanhouFlor = 1
            else:
                self.modeloRegistro.quemGanhouFlor = 0
        
        if hasattr(self, 'quemContraFlor'):
            if self.quemContraFlor == 1:
                self.modeloRegistro.quemContraFlor = 2
            elif self.quemContraFlor == 2:
                self.modeloRegistro.quemContraFlor = 1
            else:
                self.modeloRegistro.quemContraFlor = 0
        
        if hasattr(self, 'quemContraFlorResto'):
            if self.quemContraFlorResto == 1:
                self.modeloRegistro.quemContraFlorResto = 2
            elif self.quemContraFlorResto == 2:
                self.modeloRegistro.quemContraFlorResto = 1
            else:
                self.modeloRegistro.quemContraFlorResto = 0
        
        # Cartas na mão do bot (robo) - verificação mais robusta
        self._atualizar_cartas_mao_robo()
        
        # Jogador Mao (quem é o primeiro) - melhor tratamento
        if hasattr(self, 'proximo_primeiro') and self.proximo_primeiro:
            self.modeloRegistro.jogadorMao = 2 if self.proximo_primeiro == self.jogador1 else 1
        else:
            # Valor padrão se não foi definido
            self.modeloRegistro.jogadorMao = 1
            
        #self.printar_modelo_registro()
        
    def _atualizar_cartas_mao_robo(self):
        """Atualiza as cartas do robo APENAS se ainda não foram definidas (ou seja, só no início da mão)."""
        # Só atualiza se todas as cartas ainda forem zero (não definidas)
        if (
            getattr(self.modeloRegistro, 'cartaAltaRobo', 0) != 0 or
            getattr(self.modeloRegistro, 'cartaMediaRobo', 0) != 0 or
            getattr(self.modeloRegistro, 'cartaBaixaRobo', 0) != 0
        ):
            return

        if not all(hasattr(self.jogador2, attr) for attr in ['pontuacaoCartas', 'mao', 'maoRank']):
            return
        if not all([self.jogador2.pontuacaoCartas, self.jogador2.mao, self.jogador2.maoRank]):
            return
        if not (len(self.jogador2.pontuacaoCartas) == len(self.jogador2.mao) == len(self.jogador2.maoRank)):
            return
        try:
            NAIPE_MAP = {"ESPADAS": 1, "OUROS": 2, "BASTOS": 3, "COPAS": 4}
            idx_alta = self.jogador2.maoRank.index("Alta") if "Alta" in self.jogador2.maoRank else None
            idx_media = self.jogador2.maoRank.index("Media") if "Media" in self.jogador2.maoRank else None
            idx_baixa = self.jogador2.maoRank.index("Baixa") if "Baixa" in self.jogador2.maoRank else None
            if idx_alta is not None and idx_alta < len(self.jogador2.pontuacaoCartas):
                self.modeloRegistro.cartaAltaRobo = self.jogador2.pontuacaoCartas[idx_alta]
                if idx_alta < len(self.jogador2.mao):
                    naipe = self.jogador2.mao[idx_alta].retornarNaipe()
                    self.modeloRegistro.naipeCartaAltaRobo = NAIPE_MAP.get(naipe, 0)
            if idx_media is not None and idx_media < len(self.jogador2.pontuacaoCartas):
                self.modeloRegistro.cartaMediaRobo = self.jogador2.pontuacaoCartas[idx_media]
                if idx_media < len(self.jogador2.mao):
                    naipe = self.jogador2.mao[idx_media].retornarNaipe()
                    self.modeloRegistro.naipeCartaMediaRobo = NAIPE_MAP.get(naipe, 0)
            if idx_baixa is not None and idx_baixa < len(self.jogador2.pontuacaoCartas):
                self.modeloRegistro.cartaBaixaRobo = self.jogador2.pontuacaoCartas[idx_baixa]
                if idx_baixa < len(self.jogador2.mao):
                    naipe = self.jogador2.mao[idx_baixa].retornarNaipe()
                    self.modeloRegistro.naipeCartaBaixaRobo = NAIPE_MAP.get(naipe, 0)
        except (ValueError, IndexError, AttributeError) as e:
            print(f"[DEBUG] Erro ao atualizar cartas mão robo: {e}")
            pass

    def printar_modelo_registro(self):
        print("\n--- Estado atual do ModeloRegistro ---")
        print(self.modeloRegistro)
        print("--- Fim do ModeloRegistro ---\n")
        
    def inicializar_arrays_cartas_jogadas(self):
        """Inicializa ou reseta os arrays de cartas jogadas para ambos os jogadores."""
        if not hasattr(self.jogador1, 'cartas_jogadas_humano'):
            self.jogador1.cartas_jogadas_humano = [0, 0, 0]
        else:
            self.jogador1.cartas_jogadas_humano = [0, 0, 0]
            
        if not hasattr(self.jogador2, 'cartas_jogadas_robo'):
            self.jogador2.cartas_jogadas_robo = [0, 0, 0]
        else:
            self.jogador2.cartas_jogadas_robo = [0, 0, 0]

    def registrar_carta_jogada(self, jogador, carta_valor, rodada_num):
        """Registra uma carta jogada por um jogador específico."""
        if rodada_num < 1 or rodada_num > 3:
            return
            
        idx = rodada_num - 1  # Converter para índice 0-based
        if jogador == self.jogador1:
            if not hasattr(self.jogador1, 'cartas_jogadas_humano'):
                self.jogador1.cartas_jogadas_humano = [0, 0, 0]
            self.jogador1.cartas_jogadas_humano[idx] = carta_valor
        elif jogador == self.jogador2:
            if not hasattr(self.jogador2, 'cartas_jogadas_robo'):
                self.jogador2.cartas_jogadas_robo = [0, 0, 0]
            self.jogador2.cartas_jogadas_robo[idx] = carta_valor
            
        # Atualizar o modelo de registro sempre que uma carta for jogada
        self.atualizar_modelo_registro()

    def definir_ganhador_truco(self, ganhador):
        """Define quem ganhou o truco/retruco/vale quatro."""
        if self.pontos_truco == 2:  # Truco
            self.quemGanhouTruco = 1 if ganhador == self.jogador1 else 2
        elif self.pontos_truco == 3:  # Retruco
            self.quemGanhouRetruco = 1 if ganhador == self.jogador1 else 2
        elif self.pontos_truco == 4:  # Vale Quatro
            self.quemGanhouValeQuatro = 1 if ganhador == self.jogador1 else 2

    def definir_ganhador_envido(self, ganhador):
        """Define quem ganhou o envido."""
        self.quemGanhouEnvido = 1 if ganhador == self.jogador1 else 2

    def definir_ganhador_flor(self, ganhador):
        """Define quem ganhou a flor."""
        self.quemGanhouFlor = 1 if ganhador == self.jogador1 else 2

    def zerar_modelo_registro(self):
        """Reseta o modeloRegistro para o estado inicial."""
        self.quemTruco = 0
        self.quemNegouTruco = 0
        self.quemGanhouTruco = 0
        self.quemRetruco = 0
        self.quemGanhouRetruco = 0
        self.quemValeQuatro = 0
        self.quemGanhouValeQuatro = 0
        self.quemNegouEnvido = 0
        self.quemGanhouEnvido = 0
        self.quemPediuRealEnvido = 0
        self.quemPediuFaltaEnvido = 0
        self.quemFlor = 0
        self.quemGanhouFlor = 0
        self.quemContraFlor = 0
        self.quemContraFlorResto = 0
        self.modeloRegistro = ModeloRegistro()
