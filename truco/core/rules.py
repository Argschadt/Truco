from truco.utils.pontos import MANILHA, CARTAS_VALORES

def verificar_ganhador_rodada(carta1, carta2):
    # Retorna a carta vencedora ou 'Empate'
    if (str(carta1.numero)+" de "+carta1.naipe) in MANILHA and (str(carta2.numero)+" de "+carta2.naipe) in MANILHA:
        if MANILHA[str(carta1.numero)+" de "+carta1.naipe] > MANILHA[str(carta2.numero)+" de "+carta2.naipe]:
            return carta1
        elif MANILHA[str(carta2.numero)+" de "+carta2.naipe] > MANILHA[str(carta1.numero)+" de "+carta1.naipe]:
            return carta2
    elif (str(carta1.numero)+" de "+carta1.naipe) in MANILHA:
        return carta1
    elif (str(carta2.numero)+" de "+carta2.naipe) in MANILHA:
        return carta2
    else:
        if CARTAS_VALORES[str(carta1.numero)] > CARTAS_VALORES[str(carta2.numero)]:
            return carta1
        elif CARTAS_VALORES[str(carta1.numero)] < CARTAS_VALORES[str(carta2.numero)]:
            return carta2
        else:
            return "Empate"

def calcular_pontuacao(jogador, tipo_ponto, valor=1):
    # Exemplo: tipo_ponto pode ser 'rodada', 'truco', 'envido', etc.
    jogador.pontos += valor

def validar_truco(estado_jogo, quem_pediu):
    # Em breve: lógica para validar pedido de truco
    pass

def validar_envido(estado_jogo, quem_pediu):
    # Em breve: lógica para validar pedido de envido
    pass

def verificar_mao_de_onze(jogador1, jogador2):
    # Em breve: lógica para mão de onze
    pass

def verificar_escurinho(jogador1, jogador2):
    # Em breve: lógica para escurinho
    pass
