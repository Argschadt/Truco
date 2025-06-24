from truco.utils.interface import mostrar_mao, mostrar_estado, prompt_acao, mostrar_mensagem, mostrar_resultado_envido, mostrar_resultado_flor, mostrar_vencedor_rodada, mostrar_empate_rodada, mostrar_vencedor_mao, mostrar_mao_terminou_empatada
from truco.core.rules import calcular_pontuacao
from truco.core.acoes import processar_acao_truco, processar_acao_envido, resolver_flor
from truco.core.turnos import turno_jogador_humano, turno_jogador_bot, montar_prompt_acao
from truco.core.game_loop import jogar_mao
from truco.core.utils import novo_estado_mao, definir_primeiro_e_segundo, configurar_jogo

def main():
    """
    Função principal que executa o loop do jogo Truco Gaúcho.
    """
    controller, primeiro_da_partida = configurar_jogo()
    while not controller.fim_de_jogo():
        mostrar_estado(controller)
        controller.reiniciar_mao()
        controller.historico_rodadas = []
        if controller.jogador1.nome != 'Bot':
            mostrar_mao(controller.jogador1)
        elif controller.jogador2.nome != 'Bot':
            mostrar_mao(controller.jogador2)
        primeiro, segundo = definir_primeiro_e_segundo(controller)
        mao_encerrada, estado, primeiro, segundo = jogar_mao(controller, primeiro, segundo, primeiro_da_partida, novo_estado_mao)
        if mao_encerrada:
            continue
        vencedor_mao = controller.processar_fim_mao()
        if vencedor_mao:
            mostrar_mensagem(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
            controller.definir_proximo_primeiro(vencedor_mao)
        elif len(controller.historico_rodadas) == 3 and controller.historico_rodadas.count(1) == controller.historico_rodadas.count(2):
            mostrar_mensagem('\nA mão terminou empatada!')
            if primeiro == controller.jogador1:
                controller.definir_proximo_primeiro(controller.jogador2)
            else:
                controller.definir_proximo_primeiro(controller.jogador1)
            controller.historico_rodadas = []
        controller.mostrar_estado()
    mostrar_mensagem(f'\nFIM DE JOGO! Vencedor: {controller.determinar_vencedor().nome} com {controller.determinar_vencedor().pontos} pontos!')

if __name__ == '__main__':
    main()