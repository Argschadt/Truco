def novo_estado_mao():
    """
    Retorna o estado inicial de uma mão de Truco.
    """
    return {
        'truco_fase': 0,  # 0: nada, 1: truco, 2: retruco, 3: vale quatro
        'pode_truco': True,
        'pode_envido': True,
        'pode_flor': True,
        'envido_pedido': False,
        'flor_pedida': False,
        'vez_truco': None,
    }


def definir_primeiro_e_segundo(controller):
    """
    Define quem será o primeiro e o segundo jogador da mão.
    """
    if hasattr(controller, 'proximo_primeiro') and controller.proximo_primeiro:
        primeiro = controller.proximo_primeiro
        segundo = controller.jogador1 if controller.proximo_primeiro == controller.jogador2 else controller.jogador2
        controller.proximo_primeiro = None
    else:
        primeiro, segundo = controller.jogador1, controller.jogador2
    return primeiro, segundo


def configurar_jogo():
    """
    Realiza a configuração inicial do jogo e retorna o controller e o primeiro jogador da partida.
    """
    from truco.utils.interface import mostrar_mensagem
    from truco.core.game_controller import GameController
    import random
    mostrar_mensagem('Bem-vindo ao Truco Gaúcho!')
    nome1 = 'Heitor'
    nome2 = 'Bot'
    controller = GameController(nome1, nome2, bot=True)
    primeiro_da_partida = random.choice([controller.jogador1, controller.jogador2])
    controller.proximo_primeiro = primeiro_da_partida
    mostrar_mensagem(f'Quem começa a primeira mão: {primeiro_da_partida.nome}')
    return controller, primeiro_da_partida
