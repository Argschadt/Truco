from truco.utils.interface import mostrar_mensagem, mostrar_mao

# Funções auxiliares para separar lógica de jogada

def jogar_carta_humano(jogador, carta_idx):
    """Executa a jogada do jogador humano."""
    return jogador.jogarCarta(carta_idx)

def jogar_carta_bot(jogador, cbr, controller):
    """Executa a jogada do bot."""
    return jogador.jogarCarta(cbr, controller)

def registrar_jogada(controller, jogador, carta, rodada_num, humano=False):
    """Registra a jogada do jogador e atualiza o modelo de registro."""
    pontos = carta.retornarPontosCarta(carta)
    print(f'\n{jogador.nome} jogou: {carta.numero} de {carta.naipe} ({pontos} pontos)')
    if humano:
        controller.registrar_carta_jogada(jogador, pontos, rodada_num)
    else:
        controller.registrar_carta_jogada(jogador, pontos, rodada_num)
    # Atualiza o modelo de registro após registrar a jogada
    if hasattr(controller, 'atualizar_modelo_registro'):
        controller.atualizar_modelo_registro()


def jogar_rodada(controller, jogador_atual, jogador_oponente, rodada, carta_idx, mao_encerrada):
    """
    Executa uma rodada entre dois jogadores, realiza as jogadas, exibe mensagens e retorna um dicionário com o resultado.
    """
    rodada_num = rodada
    if jogador_atual == controller.jogador1:
        carta1 = jogar_carta_humano(jogador_atual, carta_idx)
        registrar_jogada(controller, jogador_atual, carta1, rodada_num, humano=True)
        if jogador_oponente == controller.jogador2:
            carta2 = jogar_carta_bot(jogador_oponente, controller.cbr, controller)
            registrar_jogada(controller, jogador_oponente, carta2, rodada_num)
        else:
            carta2 = jogar_carta_humano(jogador_oponente, carta_idx)
            registrar_jogada(controller, jogador_oponente, carta2, rodada_num, humano=True)
    else:
        carta1 = jogar_carta_bot(jogador_atual, controller.cbr, controller)
        registrar_jogada(controller, jogador_atual, carta1, rodada_num)
        mostrar_mao(jogador_oponente)
        if jogador_oponente == controller.jogador1:
            carta2 = jogar_carta_humano(jogador_oponente, carta_idx)
            registrar_jogada(controller, jogador_oponente, carta2, rodada_num, humano=True)
            mostrar_mensagem(f'Você jogou: {carta2.numero} de {carta2.naipe}')
        else:
            carta2 = jogar_carta_bot(jogador_oponente, controller.cbr, controller)
            registrar_jogada(controller, jogador_oponente, carta2, rodada_num)
    mostrar_mensagem(f'{jogador_atual.nome} jogou: {carta1.numero} de {carta1.naipe}')
    mostrar_mensagem(f'{jogador_oponente.nome} jogou: {carta2.numero} de {carta2.naipe}')
    ganhador_rodada, vencedor_mao = controller.jogar_rodada(carta1, carta2, jogador_atual, jogador_oponente)
    return {
        'ganhador_rodada': ganhador_rodada,
        'vencedor_mao': vencedor_mao,
        'jogador_atual': jogador_atual,
        'jogador_oponente': jogador_oponente,
        'carta1': carta1,
        'carta2': carta2,
        'mao_encerrada': mao_encerrada
    }


def alternar_jogadores(jogador_atual, jogador_oponente):
    """Troca a vez dos jogadores."""
    return jogador_oponente, jogador_atual

# Funções auxiliares para mensagens

def exibir_resultado_rodada(ganhador_rodada, jogador_atual, jogador_oponente, carta1, carta2):
    """Exibe mensagem do resultado da rodada."""
    if ganhador_rodada == carta1:
        mostrar_mensagem(f'{jogador_atual.nome} venceu a rodada!')
    elif ganhador_rodada == carta2:
        mostrar_mensagem(f'{jogador_oponente.nome} venceu a rodada!')
    else:
        mostrar_mensagem('Rodada empatada!')


def processar_fim_mao(controller, jogador_atual, jogador_oponente):
    """Processa o fim da mão e exibe mensagens apropriadas."""
    vencedor_mao = controller.processar_fim_mao()
    if vencedor_mao:
        mostrar_mensagem(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
        controller.mostrar_estado()
        controller.definir_proximo_primeiro(vencedor_mao)
    else:
        mostrar_mensagem('\nA mão terminou empatada!')
        if jogador_atual == controller.jogador1:
            controller.definir_proximo_primeiro(controller.jogador2)
        else:
            controller.definir_proximo_primeiro(controller.jogador1)
    return True


def jogar_mao(controller, jogador_atual, jogador_oponente, primeiro_da_partida, novo_estado_mao):
    """
    Executa o loop de uma mão completa, incluindo rodadas e alternância de jogadores.
    Novo fluxo: cada jogador executa seu turno completo (inclusive jogar carta e registrar),
    e a rodada apenas avalia o resultado.
    """
    from truco.core.turnos import turno_jogador_humano, montar_prompt_acao, turno_jogador_bot
    estado = novo_estado_mao()
    mao_encerrada = False
    controller.zerar_modelo_registro()
    for rodada in range(1, 4):
        if controller.mao_decidida():
            break
        mostrar_mensagem(f'\nRodada {rodada}')
        estado['pode_truco'] = True
        # 1ª carta
        if jogador_atual == controller.jogador1:
            # jogador humano
            while True:
                carta_idx1, estado, mao_encerrada = turno_jogador_humano(
                    jogador_atual, jogador_oponente, controller, estado, primeiro_da_partida, rodada, montar_prompt_acao)
                if mao_encerrada or carta_idx1 is not None:
                    break
            if mao_encerrada:
                break
            carta1 = jogador_atual.jogarCarta(carta_idx1)
            registrar_jogada(controller, jogador_atual, carta1, rodada, humano=True)
        else:
            # jogador bot
            while True:
                carta_idx1, estado, mao_encerrada = turno_jogador_bot(
                    jogador_atual, jogador_oponente, controller, estado, primeiro_da_partida, rodada)
                if mao_encerrada:
                    break
                # para bot, sempre joga carta após turno
                break
            if mao_encerrada:
                break
            # usa helper para bot
            carta1 = jogar_carta_bot(jogador_atual, controller.cbr, controller)
            registrar_jogada(controller, jogador_atual, carta1, rodada)
        # Turno do oponente
        if jogador_oponente == controller.jogador1:
            while True:
                carta_idx2, estado, mao_encerrada = turno_jogador_humano(
                    jogador_oponente, jogador_atual, controller, estado, primeiro_da_partida, rodada, montar_prompt_acao)
                if mao_encerrada:
                    break
                if carta_idx2 is not None:
                    break
            if mao_encerrada:
                break
            carta2 = jogador_oponente.jogarCarta(carta_idx2)
            registrar_jogada(controller, jogador_oponente, carta2, rodada, humano=True)
        else:
             # jogador bot
            while True:
                carta_idx1, estado, mao_encerrada = turno_jogador_bot(
                    jogador_oponente, jogador_atual, controller, estado, primeiro_da_partida, rodada)
                if mao_encerrada:
                    break
                # para bot, sempre joga carta após turno
                break
            if mao_encerrada:
                break
            # usa helper para bot
            carta2 = jogar_carta_bot(jogador_oponente, controller.cbr, controller)
            registrar_jogada(controller, jogador_oponente, carta1, rodada)
        # Avalia resultado da rodada
        ganhador_rodada, vencedor_mao = controller.jogar_rodada(carta1, carta2, jogador_atual, jogador_oponente)
        exibir_resultado_rodada(ganhador_rodada, jogador_atual, jogador_oponente, carta1, carta2)
        if controller.mao_decidida():
            mao_encerrada = processar_fim_mao(controller, jogador_atual, jogador_oponente)
            break
        # Alterna jogadores se necessário
        if ganhador_rodada == carta2:
            jogador_atual, jogador_oponente = alternar_jogadores(jogador_atual, jogador_oponente)
    return {
        'mao_encerrada': mao_encerrada,
        'estado': estado,
        'jogador_atual': jogador_atual,
        'jogador_oponente': jogador_oponente
    }
