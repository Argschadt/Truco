from truco.utils.interface import mostrar_mensagem, mostrar_mao

def jogar_rodada(controller, primeiro, segundo, rodada, carta_idx, mao_encerrada):
    """
    Executa uma rodada entre dois jogadores, realiza as jogadas, exibe mensagens e retorna:
    (ganhador_rodada, vencedor_mao, primeiro, segundo, mao_encerrada)
    """
    if primeiro == controller.jogador1:
        carta1 = primeiro.jogarCarta(carta_idx)
        rodada_num = rodada
        controller.jogador2.registrar_carta_humano(carta1.retornarPontosCarta(carta1), rodada_num, controller)
        if segundo == controller.jogador2:
            carta2 = segundo.jogarCarta(controller.cbr, controller)
        else:
            carta2 = segundo.jogarCarta(carta_idx)
        controller.jogador2.registrar_carta_jogada(carta2.retornarPontosCarta(carta2), rodada_num, controller)
    else:
        carta1 = primeiro.jogarCarta(controller.cbr, controller)
        rodada_num = rodada
        controller.jogador2.registrar_carta_jogada(carta1.retornarPontosCarta(carta1), rodada_num, controller)
        mostrar_mao(segundo)
        if segundo == controller.jogador1:
            carta2 = segundo.jogarCarta(carta_idx)
            mostrar_mensagem(f'Você jogou: {carta2.numero} de {carta2.naipe}')
        else:
            carta2 = segundo.jogarCarta(controller.cbr, controller)
    mostrar_mensagem(f'{primeiro.nome} jogou: {carta1.numero} de {carta1.naipe}')
    mostrar_mensagem(f'{segundo.nome} jogou: {carta2.numero} de {carta2.naipe}')
    ganhador_rodada, vencedor_mao = controller.jogar_rodada(carta1, carta2, primeiro, segundo)
    return ganhador_rodada, vencedor_mao, primeiro, segundo, carta1, carta2, mao_encerrada


def jogar_mao(controller, primeiro, segundo, primeiro_da_partida, novo_estado_mao):
    """
    Executa o loop de uma mão completa, incluindo rodadas e alternância de jogadores.
    """
    estado = novo_estado_mao()
    mao_encerrada = False
    for rodada in range(1, 4):
        if controller.mao_decidida():
            break
        mostrar_mensagem(f'\nRodada {rodada}')
        if 1 < controller.pontos_truco < 4:
            estado['pode_truco'] = True
        carta_idx = None
        if primeiro == controller.jogador1:
            from truco.core.turnos import turno_jogador_humano, montar_prompt_acao
            carta_idx, estado, mao_encerrada = turno_jogador_humano(
                primeiro, segundo, controller, estado, primeiro_da_partida, rodada, montar_prompt_acao)
        else:
            from truco.core.turnos import turno_jogador_bot
            carta_idx, estado, mao_encerrada = turno_jogador_bot(
                primeiro, segundo, controller, estado, primeiro_da_partida, rodada)
            if not mao_encerrada and carta_idx is not None:
                mostrar_mensagem(f'{primeiro.nome} jogou: {primeiro.mao[carta_idx].numero} de {primeiro.mao[carta_idx].naipe}')
        if mao_encerrada:
            break
        ganhador_rodada, vencedor_mao, primeiro, segundo, carta1, carta2, mao_encerrada = jogar_rodada(
            controller, primeiro, segundo, rodada, carta_idx, mao_encerrada)
        if controller.mao_decidida():
            vencedor_mao = controller.processar_fim_mao()
            if vencedor_mao:
                mostrar_mensagem(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
                controller.mostrar_estado()
                controller.definir_proximo_primeiro(vencedor_mao)
            else:
                mostrar_mensagem('\nA mão terminou empatada!')
                if primeiro == controller.jogador1:
                    controller.definir_proximo_primeiro(controller.jogador2)
                else:
                    controller.definir_proximo_primeiro(controller.jogador1)
            mao_encerrada = True
            break
        if ganhador_rodada == carta1:
            mostrar_mensagem(f'{primeiro.nome} venceu a rodada!')
        elif ganhador_rodada == carta2:
            mostrar_mensagem(f'{segundo.nome} venceu a rodada!')
            primeiro, segundo = segundo, primeiro
        elif ganhador_rodada == "Empate":
            mostrar_mensagem('Rodada empatada!')
        else:
            mostrar_mensagem('Rodada empatada!')
    return mao_encerrada, estado, primeiro, segundo
