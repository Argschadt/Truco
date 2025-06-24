from truco.utils.interface import mostrar_mao, mostrar_estado, mostrar_mensagem
from truco.core.utils import novo_estado_mao, definir_primeiro_e_segundo
from truco.core.game_loop import jogar_mao


def exibir_mao_jogador(controller):
    """Mostra a mão do jogador humano, se houver."""
    if controller.jogador1.nome != 'Bot':
        mostrar_mao(controller.jogador1)
    elif controller.jogador2.nome != 'Bot':
        mostrar_mao(controller.jogador2)


def processar_fim_mao(controller, primeiro_jogador, segundo_jogador):
    """Processa o fim da mão, mostrando mensagens e definindo o próximo primeiro jogador."""
    vencedor_mao = controller.processar_fim_mao()
    if vencedor_mao:
        mostrar_mensagem(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
        controller.definir_proximo_primeiro(vencedor_mao)
    elif len(controller.historico_rodadas) == 3 and controller.historico_rodadas.count(1) == controller.historico_rodadas.count(2):
        mostrar_mensagem('\nA mão terminou empatada!')
        proximo_primeiro = controller.jogador2 if primeiro_jogador == controller.jogador1 else controller.jogador1
        controller.definir_proximo_primeiro(proximo_primeiro)
        controller.historico_rodadas = []


def loop_jogo(controller, primeiro_da_partida):
    """Executa o loop principal do jogo."""
    while not controller.fim_de_jogo():
        mostrar_estado(controller)
        controller.reiniciar_mao()
        controller.historico_rodadas = []
        exibir_mao_jogador(controller)
        primeiro_jogador, segundo_jogador = definir_primeiro_e_segundo(controller)
        mao_encerrada, _, primeiro_jogador, segundo_jogador = jogar_mao(
            controller, primeiro_jogador, segundo_jogador, primeiro_da_partida, novo_estado_mao
        )
        if mao_encerrada:
            continue
        processar_fim_mao(controller, primeiro_jogador, segundo_jogador)
        controller.mostrar_estado()
