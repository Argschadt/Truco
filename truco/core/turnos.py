from truco.utils.interface import mostrar_mao, prompt_acao, mostrar_mensagem
from truco.core.rules import calcular_pontuacao
from truco.core.acoes import processar_acao_truco, processar_acao_envido, resolver_flor

def montar_prompt_acao(pode_pedir_truco, pontos_truco, pode_pedir_envido, pode_pedir_flor, jogador=None, pode_pedir_real_envido=False, pode_pedir_falta_envido=False):
    """
    Monta o texto do prompt de ação para o jogador, indicando as opções disponíveis.
    """
    prompt = ""
    if pode_pedir_truco:
        if pontos_truco == 1:
            prompt += "[T]ruco"
        elif pontos_truco == 2:
            prompt += "[T]ruco (Retruco)"
        elif pontos_truco == 3:
            prompt += "[T]ruco (Vale Quatro)"
    if pode_pedir_envido:
        if prompt:
            prompt += ", "
        prompt += "[E]nvido"
    if pode_pedir_real_envido:
        if prompt:
            prompt += ", "
        prompt += "[R]eal Envido"
    if pode_pedir_falta_envido:
        if prompt:
            prompt += ", "
        prompt += "[F]alta Envido"
    if pode_pedir_flor:
        if prompt:
            prompt += ", "
        prompt += "[L]Flor"
    if prompt:
        prompt += " ou "
    if jogador:
        prompt += f"digite o número da carta para jogar (0 a {len(jogador.mao)-1}): "
    else:
        prompt += "digite o número da carta para jogar: "
    return prompt

def turno_jogador_humano(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida, rodada, montar_prompt_acao):
    """
    Executa o turno do jogador humano, processando todas as ações possíveis e retorna:
    (carta_idx, estado, mao_encerrada)
    """
    carta_idx = None
    mao_encerrada = False
    while True:
        # Verifica se o jogador pode pedir truco nesta rodada
        pode_pedir_truco = False
        if estado['pode_truco']:
            if estado['truco_fase'] == 0 and controller.pontos_truco == 1:
                pode_pedir_truco = True
            elif (estado['truco_fase'] == 1 and controller.pontos_truco == 2 and estado['vez_truco'] == primeiro_jogador):
                pode_pedir_truco = True
            elif (estado['truco_fase'] == 2 and controller.pontos_truco == 3 and estado['vez_truco'] == primeiro_jogador):
                pode_pedir_truco = True
        # Verifica se pode pedir envido ou flor
        pode_pedir_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_pedir_flor = estado['pode_flor'] and not estado['flor_pedida'] and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
        pode_pedir_real_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_pedir_falta_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']

        mostrar_mao(primeiro_jogador)
        prompt = montar_prompt_acao(
            pode_pedir_truco and (estado['truco_fase'] == 0 or estado['vez_truco'] is None or estado['vez_truco'] == primeiro_jogador),
            controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, primeiro_jogador, pode_pedir_real_envido, pode_pedir_falta_envido)
        acao = prompt_acao(prompt)
        # Processa a ação escolhida pelo jogador
        if acao == 't' and pode_pedir_truco and (estado['truco_fase'] == 0 or estado['vez_truco'] is None or estado['vez_truco'] == primeiro_jogador):
            # Jogador pede truco
            resultado, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], mao_encerrada = processar_acao_truco(
                controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida, rodada=rodada, estado=estado)
            if resultado:
                continue
            else:
                break
        elif acao == 'e' and pode_pedir_envido:
            # Jogador pede envido
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        elif acao == 'r' and pode_pedir_real_envido:
            # Jogador pede real envido
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        elif acao == 'f' and pode_pedir_falta_envido:
            # Jogador pede falta envido
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        elif acao == 'l' and pode_pedir_flor:
            # Jogador pede flor
            estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resolver_flor(
                primeiro_jogador, segundo_jogador, controller, calcular_pontuacao,
                estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'],
                primeiro_da_partida
            )
            continue
        elif acao.isdigit():
            # Jogador escolhe uma carta para jogar
            carta_idx = int(acao)
            if 0 <= carta_idx < len(primeiro_jogador.mao):
                mostrar_mensagem(f"Você escolheu: {primeiro_jogador.mao[carta_idx].numero} de {primeiro_jogador.mao[carta_idx].naipe}")
                break
            else:
                mostrar_mensagem(f"Índice inválido! Escolha entre 0 e {len(primeiro_jogador.mao)-1}.")
        else:
            mostrar_mensagem("Opção inválida! Digite T, E, R, F ou o número da carta.")
        # Define quem pode pedir truco na próxima vez, se necessário
        if estado['truco_fase'] == 0 and rodada == 1 and estado['vez_truco'] is None:
            estado['vez_truco'] = segundo_jogador
    return carta_idx, estado, mao_encerrada

def turno_jogador_bot(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida, rodada):
    """
    Executa o turno do bot, processando todas as ações possíveis e retorna:
    (carta_idx, estado, mao_encerrada)
    """
    carta_idx = None
    mao_encerrada = False
    while True:
        # Checa possibilidades de pedir envido, real envido, falta envido ou flor
        pode_pedir_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_pedir_real_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_pedir_falta_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_pedir_flor = estado['pode_flor'] and not estado['flor_pedida'] and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
        # 1. Flor
        if pode_pedir_flor and primeiro_jogador.pedir_flor(controller.cbr, controller):
            estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resolver_flor(primeiro_jogador, segundo_jogador, controller, calcular_pontuacao, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'], primeiro_da_partida)
            # Continua o turno para jogar carta
            continue
        # 2. Envido, Real Envido ou Falta Envido
        elif pode_pedir_envido and not estado['envido_pedido'] and primeiro_jogador.pedir_envido(controller.cbr, controller):
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        elif pode_pedir_real_envido and not estado['envido_pedido'] and hasattr(primeiro_jogador, 'pedir_real_envido') and primeiro_jogador.pedir_real_envido(controller.cbr):
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        elif pode_pedir_falta_envido and not estado['envido_pedido'] and hasattr(primeiro_jogador, 'pedir_falta_envido') and primeiro_jogador.pedir_falta_envido(controller.cbr):
            estado['envido_pedido'] = True
            estado['pode_envido'] = False
            pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
            resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
            if isinstance(resultado, tuple) and len(resultado) == 7:
                _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
            continue
        # 3. Truco
        pode_pedir_truco = False
        if estado['pode_truco']:
            if estado['truco_fase'] == 0 and controller.pontos_truco == 1 and (estado['vez_truco'] is None or estado['vez_truco'] == primeiro_jogador):
                pode_pedir_truco = True
            elif estado['truco_fase'] == 1 and controller.pontos_truco == 2 and estado['vez_truco'] == primeiro_jogador:
                pode_pedir_truco = True
            elif estado['truco_fase'] == 2 and controller.pontos_truco == 3 and estado['vez_truco'] == primeiro_jogador:
                pode_pedir_truco = True
        if pode_pedir_truco and hasattr(primeiro_jogador, 'pedir_truco') and primeiro_jogador.pedir_truco(controller.cbr, controller):
            resultado, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], mao_encerrada = processar_acao_truco(
                controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida, rodada=rodada, estado=estado)
            if resultado:
                if mao_encerrada:
                    return None, estado, mao_encerrada
                continue
        # 4. Jogar carta
        carta_idx = primeiro_jogador.escolher_carta(controller.cbr, controller) if hasattr(primeiro_jogador, 'escolher_carta') else 0
        return carta_idx, estado, mao_encerrada
