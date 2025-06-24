# Imports agrupados por domínio
from truco.core.utils import configurar_jogo
from truco.core.game_runner import loop_jogo
from truco.utils.interface import mostrar_mensagem


def main():
    """
    Função principal que executa o loop do jogo Truco Gaúcho.
    """
    controller, primeiro_da_partida = configurar_jogo()
    loop_jogo(controller, primeiro_da_partida)
    mostrar_mensagem(
        f'\nFIM DE JOGO! Vencedor: {controller.determinar_vencedor().nome} com {controller.determinar_vencedor().pontos} pontos!'
    )


if __name__ == '__main__':
    main()