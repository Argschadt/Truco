from truco.utils.pontos import MANILHA, CARTAS_VALORES

# Hierarquia completa do Truco Gaúcho
HIERARQUIA_TRUCO_GAUCHO = [
    "1 de ESPADAS",
    "1 de BASTOS",
    "7 de ESPADAS",
    "7 de OUROS",
    "3 de ESPADAS", "3 de OUROS", "3 de COPAS", "3 de BASTOS",
    "2 de ESPADAS", "2 de OUROS", "2 de COPAS", "2 de BASTOS",
    "1 de OUROS", "1 de COPAS",
    "12 de ESPADAS", "12 de OUROS", "12 de COPAS", "12 de BASTOS",
    "11 de ESPADAS", "11 de OUROS", "11 de COPAS", "11 de BASTOS",
    "10 de ESPADAS", "10 de OUROS", "10 de COPAS", "10 de BASTOS",
    "7 de COPAS", "7 de BASTOS",
    "6 de ESPADAS", "6 de OUROS", "6 de COPAS", "6 de BASTOS",
    "5 de ESPADAS", "5 de OUROS", "5 de COPAS", "5 de BASTOS",
    "4 de ESPADAS", "4 de OUROS", "4 de COPAS", "4 de BASTOS"
]

HIERARQUIA_MAPA = {nome.upper(): i for i, nome in enumerate(HIERARQUIA_TRUCO_GAUCHO)}

def verificar_ganhador_rodada(carta1, carta2):
    # Empata se o número for igual e não for manilha
    nome1 = f"{carta1.numero} de {carta1.naipe}".upper().strip()
    nome2 = f"{carta2.numero} de {carta2.naipe}".upper().strip()
    # Checa se são manilhas
    eh_manilha1 = nome1.title() in MANILHA
    eh_manilha2 = nome2.title() in MANILHA
    if carta1.numero == carta2.numero and not (eh_manilha1 or eh_manilha2):
        return "Empate"
    idx1 = HIERARQUIA_MAPA.get(nome1, 100)
    idx2 = HIERARQUIA_MAPA.get(nome2, 100)
    if idx1 < idx2:
        return carta1
    elif idx2 < idx1:
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
