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

def pode_pedir_truco_humano(estado, controller, jogador):
    if not estado['pode_truco']:
        return False
    if estado['truco_fase'] == 0 and controller.pontos_truco == 1:
        return True
    if estado['truco_fase'] == 1 and controller.pontos_truco == 2 and estado['vez_truco'] == jogador:
        return True
    if estado['truco_fase'] == 2 and controller.pontos_truco == 3 and estado['vez_truco'] == jogador:
        return True
    return False

def pode_pedir_envido(estado, rodada):
    return rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']

def pode_pedir_flor(estado, jogador):
    return estado['pode_flor'] and not estado['flor_pedida'] and jogador.checaFlor() and len(jogador.mao) == 3

def processar_envido(controller, primeiro_jogador, segundo_jogador, tipo, pontos, primeiro_da_partida, estado):
    estado['envido_pedido'] = True
    estado['pode_envido'] = False
    resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, tipo, pontos, primeiro_da_partida)
    if isinstance(resultado, tuple) and len(resultado) == 7:
        _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado

def processar_flor(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida):
    estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resolver_flor(
        primeiro_jogador, segundo_jogador, controller, calcular_pontuacao,
        estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'],
        primeiro_da_partida
    )

def processar_acao_humana(acao, opcoes, controller, primeiro_jogador, segundo_jogador, estado, primeiro_da_partida, rodada):
    mao_encerrada = False
    carta_idx = None
    if acao == 't' and opcoes['pode_pedir_truco']:
        resultado, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], mao_encerrada = processar_acao_truco(
            controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida, rodada=rodada, estado=estado)
        return None, estado, mao_encerrada, resultado
    elif acao == 'e' and opcoes['pode_pedir_envido']:
        processar_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida, estado)
        return None, estado, False, True
    elif acao == 'r' and opcoes['pode_pedir_real_envido']:
        processar_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida, estado)
        return None, estado, False, True
    elif acao == 'f' and opcoes['pode_pedir_falta_envido']:
        pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
        processar_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida, estado)
        return None, estado, False, True
    elif acao == 'l' and opcoes['pode_pedir_flor']:
        processar_flor(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida)
        return None, estado, False, True
    elif acao.isdigit():
        carta_idx = int(acao)
        if 0 <= carta_idx < len(primeiro_jogador.mao):
            mostrar_mensagem(f"Você escolheu: {primeiro_jogador.mao[carta_idx].numero} de {primeiro_jogador.mao[carta_idx].naipe}")
            return carta_idx, estado, False, False
        else:
            mostrar_mensagem(f"Índice inválido! Escolha entre 0 e {len(primeiro_jogador.mao)-1}.")
            return None, estado, False, True
    else:
        mostrar_mensagem("Opção inválida! Digite T, E, R, F ou o número da carta.")
        return None, estado, False, True

def turno_jogador_humano(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida, rodada, montar_prompt_acao):
    """
    Executa o turno do jogador humano, processando todas as ações possíveis e retorna:
    (carta_idx, estado, mao_encerrada)
    """
    carta_idx = None
    mao_encerrada = False
    while True:
        # Checa todas as opções possíveis para o jogador
        opcoes = {
            'pode_pedir_truco': pode_pedir_truco_humano(estado, controller, primeiro_jogador) and (estado['truco_fase'] == 0 or estado['vez_truco'] is None or estado['vez_truco'] == primeiro_jogador),
            'pode_pedir_envido': pode_pedir_envido(estado, rodada),
            'pode_pedir_real_envido': pode_pedir_envido(estado, rodada),
            'pode_pedir_falta_envido': pode_pedir_envido(estado, rodada),
            'pode_pedir_flor': pode_pedir_flor(estado, primeiro_jogador)
        }
        mostrar_mao(primeiro_jogador)
        prompt = montar_prompt_acao(
            opcoes['pode_pedir_truco'],
            controller.pontos_truco,
            opcoes['pode_pedir_envido'],
            opcoes['pode_pedir_flor'],
            primeiro_jogador,
            opcoes['pode_pedir_real_envido'],
            opcoes['pode_pedir_falta_envido']
        )
        acao = prompt_acao(prompt)
        carta_idx, estado, mao_encerrada, repetir = processar_acao_humana(
            acao, opcoes, controller, primeiro_jogador, segundo_jogador, estado, primeiro_da_partida, rodada)
        if mao_encerrada:
            break
        if carta_idx is not None:
            break
        # Define quem pode pedir truco na próxima vez, se necessário
        if estado['truco_fase'] == 0 and rodada == 1 and estado['vez_truco'] is None:
            estado['vez_truco'] = segundo_jogador
        if not repetir:
            break
    return carta_idx, estado, mao_encerrada

def pode_pedir_truco_bot(estado, controller, jogador):
    if not estado['pode_truco']:
        return False
    if estado['truco_fase'] == 0 and controller.pontos_truco == 1 and (estado['vez_truco'] is None or estado['vez_truco'] == jogador):
        return True
    if estado['truco_fase'] == 1 and controller.pontos_truco == 2 and estado['vez_truco'] == jogador:
        return True
    if estado['truco_fase'] == 2 and controller.pontos_truco == 3 and estado['vez_truco'] == jogador:
        return True
    return False

def processar_envido_bot(controller, primeiro_jogador, segundo_jogador, tipo, pontos, primeiro_da_partida, estado):
    estado['envido_pedido'] = True
    estado['pode_envido'] = False
    resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, tipo, pontos, primeiro_da_partida)
    if isinstance(resultado, tuple) and len(resultado) == 7:
        _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado

def turno_jogador_bot(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida, rodada):
    """
    Executa o turno do bot, processando todas as ações possíveis e retorna:
    (carta_idx, estado, mao_encerrada)
    """
    carta_idx = None
    mao_encerrada = False
    while True:
        # Debug: mostra o nome do bot que está jogando
        print(f"[DEBUG] Bot atual: {getattr(primeiro_jogador, 'nome', str(primeiro_jogador))}")
        # Checa possibilidades de pedir envido, real envido, falta envido ou flor
        pode_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
        pode_flor = estado['pode_flor'] and not estado['flor_pedida'] and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
        # 1. Flor
        if pode_flor and hasattr(primeiro_jogador, 'pedir_flor') and primeiro_jogador.pedir_flor(controller.cbr, controller):
            processar_flor(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida)
            continue
        # 2. Envido, Real Envido ou Falta Envido
        if pode_envido and not estado['envido_pedido']:
            if hasattr(primeiro_jogador, 'pedir_envido') and primeiro_jogador.pedir_envido(controller.cbr, controller):
                processar_envido_bot(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida, estado)
                continue
            if hasattr(primeiro_jogador, 'pedir_real_envido') and primeiro_jogador.pedir_real_envido(controller.cbr):
                processar_envido_bot(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida, estado)
                continue
            if hasattr(primeiro_jogador, 'pedir_falta_envido') and primeiro_jogador.pedir_falta_envido(controller.cbr):
                pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                processar_envido_bot(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida, estado)
                continue
        # 3. Truco
        if pode_pedir_truco_bot(estado, controller, primeiro_jogador) and hasattr(primeiro_jogador, 'pedir_truco') and primeiro_jogador.pedir_truco(controller.cbr, controller):
            resultado, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], mao_encerrada = processar_acao_truco(
                controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida, rodada=rodada, estado=estado)
            if resultado:
                if mao_encerrada:
                    return None, estado, mao_encerrada
                continue
        # 4. Jogar carta
        if hasattr(primeiro_jogador, 'escolher_carta') and len(primeiro_jogador.mao) > 0:
            carta_idx = primeiro_jogador.escolher_carta(controller.cbr, controller)
        else:
            carta_idx = 0 if len(primeiro_jogador.mao) > 0 else None
        return carta_idx, estado, mao_encerrada
