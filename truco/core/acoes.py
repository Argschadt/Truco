from truco.core.rules import calcular_pontuacao
from truco.utils.interface import mostrar_mao, mostrar_estado, prompt_acao, mostrar_mensagem, mostrar_resultado_envido, mostrar_resultado_flor, mostrar_vencedor_rodada, mostrar_empate_rodada, mostrar_vencedor_mao, mostrar_mao_terminou_empatada
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class EstadoFlor:
    flor_ja_pedida: bool
    flor_pode_ser_pedida: bool
    envido_pode_ser_pedido: bool

@dataclass
class EstadoEnvido:
    envido_pedido: bool
    pode_envido: bool
    pode_flor: bool
    flor_pedida: bool

# Funções de ações especiais do Truco Gaúcho

def prompt_envido_flor_options(estado, jogador_que_responde, controller=None):
    """
    Monta o prompt e opções para pedir Envido/Flor antes de responder ao Truco.
    Se o jogador que responde for o Bot, toma a decisão automaticamente.
    """
    pode_pedir_envido = estado['pode_envido'] and not estado['envido_pedido']
    pode_pedir_flor = estado['pode_flor'] and not estado['flor_pedida'] and jogador_que_responde.checaFlor() and len(jogador_que_responde.mao) == 3
    pode_pedir_real_envido = pode_pedir_envido
    pode_pedir_falta_envido = pode_pedir_envido
    if hasattr(jogador_que_responde, 'nome') and jogador_que_responde.nome == 'Bot':
        # Decisão automática do bot: prioriza Flor > Envido > Real Envido > Falta Envido
        # Garante que controller não é None antes de acessar controller.cbr
        cbr = controller.cbr if controller is not None else None
        if pode_pedir_flor and hasattr(jogador_que_responde, 'pedir_flor') and jogador_que_responde.pedir_flor(cbr, controller):
            return 'l', ['l'], pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor
        if pode_pedir_envido and hasattr(jogador_que_responde, 'pedir_envido') and jogador_que_responde.pedir_envido(cbr, controller):
            return 'e', ['e'], pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor
        if pode_pedir_real_envido and hasattr(jogador_que_responde, 'pedir_real_envido') and jogador_que_responde.pedir_real_envido(cbr, controller):
            return 'r', ['r'], pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor
        if pode_pedir_falta_envido and hasattr(jogador_que_responde, 'pedir_falta_envido') and jogador_que_responde.pedir_falta_envido(cbr, controller):
            return 'f', ['f'], pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor
        # Se não quiser pedir nada
        return '', [], pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor
    prompt = "Deseja pedir Envido/Flor antes de responder ao Truco?\n"
    opcoes = []
    if pode_pedir_envido:
        prompt += "[E]nvido "
        opcoes.append('e')
    if pode_pedir_real_envido:
        prompt += "[R]eal Envido "
        opcoes.append('r')
    if pode_pedir_falta_envido:
        prompt += "[F]alta Envido "
        opcoes.append('f')
    if pode_pedir_flor:
        prompt += "[L]Flor "
        opcoes.append('l')
    prompt += "ou pressione Enter para não pedir: "
    return prompt, opcoes, pode_pedir_envido, pode_pedir_real_envido, pode_pedir_falta_envido, pode_pedir_flor

def tratar_escolha_envido_flor(escolha, estado, controller, jogador_que_responde, jogador_que_pediu, primeiro_da_partida):
    """
    Processa a escolha do jogador para Envido/Flor antes do Truco.
    Retorna True se a mão foi encerrada (por Flor), False caso contrário.
    """
    if escolha == 'e':
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        resultado = processar_acao_envido(controller, jogador_que_responde, jogador_que_pediu, 'envido', 2, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return False
    elif escolha == 'r':
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        resultado = processar_acao_envido(controller, jogador_que_responde, jogador_que_pediu, 'real_envido', 3, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return False
    elif escolha == 'f':
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
        resultado = processar_acao_envido(controller, jogador_que_responde, jogador_que_pediu, 'falta_envido', pontos_falta, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return False
    elif escolha == 'l':
        estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resolver_flor(
            jogador_que_responde, jogador_que_pediu, controller, calcular_pontuacao,
            estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'],
            primeiro_da_partida
        )
        # Se alguém atingiu a pontuação máxima, encerra a mão
        pontos_max = getattr(controller, 'pontos_maximos', 15)
        if controller.jogador1.pontos >= pontos_max or controller.jogador2.pontos >= pontos_max:
            return True
        return False
    return False

def obter_resposta_truco(jogador_que_responde, controller):
    """
    Obtém a resposta do jogador (ou bot) para o pedido de Truco.
    """
    if hasattr(jogador_que_responde, 'aceitar_truco') and jogador_que_responde.nome == 'Bot':
        aceitou = jogador_que_responde.aceitar_truco(controller.pontos_truco, cbr=controller.cbr, controller=controller)
        return 's' if aceitou else 'n'
    else:
        resposta = ''
        while resposta not in ['s', 'n']:
            resposta = prompt_acao(f"{jogador_que_responde.nome}, você aceita o Truco? (vale {controller.pontos_truco} pontos) [s/n]: ")
            if resposta not in ['s', 'n']:
                mostrar_mensagem("Por favor, digite 's' para aceitar ou 'n' para correr.")
        return resposta

def processar_acao_truco(
    controller,
    jogador_que_pediu,
    jogador_que_responde,
    etapa_truco: int,
    truco_pode_ser_pedido: bool,
    envido_pode_ser_pedido: bool,
    quem_pode_pedir_truco,
    primeiro_da_partida,
    rodada: int = 1,
    estado: Optional[dict] = None
) -> Tuple[bool, int, bool, bool, object, bool]:
    """
    Processa a ação de pedir Truco, incluindo a resposta do adversário e atualização dos estados do jogo.
    Agora permite que o segundo jogador peça Envido/Flor antes de responder ao Truco, se for a primeira rodada.

    Parâmetros:
        controller: Controller do jogo
        jogador_que_pediu: Jogador que pediu Truco
        jogador_que_responde: Jogador que responde
        etapa_truco: Etapa atual do Truco
        truco_pode_ser_pedido: Flag se Truco pode ser pedido
        envido_pode_ser_pedido: Flag se Envido pode ser pedido
        quem_pode_pedir_truco: Jogador que pode pedir Truco
        primeiro_da_partida: Jogador que iniciou a mão
        rodada: Número da rodada
        estado: Estado do jogo (dict ou EstadoEnvido)
    Retorno:
        Tuple com flags e estados atualizados
    """
    controller.pedir_truco(jogador_que_pediu)
    etapa_truco += 1
    truco_pode_ser_pedido = False
    mostrar_mensagem(f"{jogador_que_pediu.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")

    # Permite Envido/Flor antes da resposta ao Truco, apenas na primeira rodada
    if rodada == 1 and envido_pode_ser_pedido and estado is not None and not (estado['envido_pedido'] if isinstance(estado, dict) else estado.envido_pedido):
        prompt, opcoes, _, _, _, _ = prompt_envido_flor_options(estado, jogador_que_responde, controller) if isinstance(estado, dict) else prompt_envido_flor_options(estado.__dict__, jogador_que_responde, controller)
        # Se o retorno do prompt é uma escolha automática do bot (ex: 'l', 'e', ...), já processa direto
        if isinstance(prompt, str) and prompt in ['l', 'e', 'r', 'f', '']:
            if prompt in opcoes:
                mao_encerrada = tratar_escolha_envido_flor(prompt, estado, controller, jogador_que_responde, jogador_que_pediu, primeiro_da_partida)
                if mao_encerrada:
                    return False, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, True
        else:
            escolha = input(prompt).strip().lower()
            if escolha in opcoes:
                mao_encerrada = tratar_escolha_envido_flor(escolha, estado, controller, jogador_que_responde, jogador_que_pediu, primeiro_da_partida)
                if mao_encerrada:
                    return False, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, True

    resposta = obter_resposta_truco(jogador_que_responde, controller)
    if resposta == 's':
        mostrar_mensagem(f"{jogador_que_responde.nome} aceitou o Truco!")
        truco_pode_ser_pedido = True
        envido_pode_ser_pedido = False
        quem_pode_pedir_truco = jogador_que_responde
        return False, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, False
    else:
        mostrar_mensagem(f"{jogador_que_responde.nome} correu do Truco!")
        vencedor = controller.aceitar_truco(False)
        controller.resetar_apostas()
        mostrar_mensagem(f"{vencedor.nome} ganhou a mão!")
        controller.historico_rodadas = []
        controller.mostrar_estado()
        controller.pontos_truco = 1
        # Alternância fixa de quem começa a próxima mão
        if not hasattr(controller, 'alternar_primeiro'):
            controller.alternar_primeiro = (primeiro_da_partida == controller.jogador1)
        controller.alternar_primeiro = not controller.alternar_primeiro
        if controller.alternar_primeiro:
            controller.definir_proximo_primeiro(controller.jogador1)
        else:
            controller.definir_proximo_primeiro(controller.jogador2)
        return False, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, True

def montar_prompt_envido(quem_pediu, quem_responde, tipo_envido, pontos_falta):
    """
    Monta o prompt e opções para o pedido de Envido, Real Envido ou Falta Envido.
    """
    tem_flor = quem_responde.checaFlor() if hasattr(quem_responde, 'checaFlor') else False
    if tipo_envido == 'envido':
        if tem_flor:
            opcoes = ['s', 'r', 'f', 'n', 'l']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Envido. Aceita [s], aumenta para Real Envido [r], Falta Envido [f], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'r', 'f', 'n']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Envido. Aceita [s], aumenta para Real Envido [r], Falta Envido [f] ou recusa [n]? "
    elif tipo_envido == 'real_envido':
        if tem_flor:
            opcoes = ['s', 'f', 'n', 'l']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Real Envido. Aceita [s], aumenta para Falta Envido [f], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'f', 'n']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Real Envido. Aceita [s], aumenta para Falta Envido [f] ou recusa [n]? "
    elif tipo_envido == 'falta_envido':
        if tem_flor:
            opcoes = ['s', 'n', 'l']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Falta Envido (vale {pontos_falta} pontos). Aceita [s], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'n']
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Falta Envido (vale {pontos_falta} pontos). Aceita [s] ou recusa [n]? "
    else:
        opcoes = []
        prompt = ""
    return prompt, opcoes

def obter_resposta_envido(quem_responde, tipo_envido, pontos_falta, controller):
    """
    Obtém a resposta do jogador (ou bot) para o pedido de Envido.
    """
    if hasattr(quem_responde, 'aceitar_envido') and quem_responde.nome == 'Bot':
        if hasattr(quem_responde, 'checaFlor') and quem_responde.checaFlor():
            return 'l'
        else:
            if tipo_envido == 'envido':
                aceitou = quem_responde.aceitar_envido(2, cbr=controller.cbr, controller=controller)
                return 's' if aceitou else 'n'
            elif tipo_envido == 'real_envido':
                aceitou = quem_responde.aceitar_envido(3, cbr=controller.cbr, controller=controller)
                return 's' if aceitou else 'n'
            else:
                aceitou = quem_responde.aceitar_envido(pontos_falta, cbr=controller.cbr, controller=controller)
                return 's' if aceitou else 'n'
    else:
        prompt, opcoes = montar_prompt_envido(controller.jogador1 if quem_responde == controller.jogador2 else controller.jogador2, quem_responde, tipo_envido, pontos_falta)
        resposta = ''
        while resposta not in opcoes:
            resposta = input(prompt).strip().lower()
            if resposta not in opcoes:
                print(f"Opção inválida! Digite uma das opções: {', '.join(opcoes)}.")
        return resposta

def processar_resultado_envido(resposta, controller, quem_pediu, quem_responde, tipo_envido, pontos_envido, pontos_falta, primeiro_da_partida):
    """
    Processa o resultado do Envido, Real Envido ou Falta Envido, de acordo com a resposta do jogador.
    """
    if resposta == 's':
        pontos1 = quem_pediu.calcular_pontos_envido()
        pontos2 = quem_responde.calcular_pontos_envido()
        mostrar_resultado_envido(quem_pediu, quem_responde, pontos1, pontos2)
        if pontos1 > pontos2:
            calcular_pontuacao(quem_pediu, 'envido', pontos_envido)
            mostrar_mensagem(f"{quem_pediu.nome} ganhou o {tipo_envido.replace('_', ' ').title()}!")
            return pontos_envido, quem_pediu, tipo_envido, True
        elif pontos2 > pontos1:
            calcular_pontuacao(quem_responde, 'envido', pontos_envido)
            mostrar_mensagem(f"{quem_responde.nome} ganhou o {tipo_envido.replace('_', ' ').title()}!")
            return pontos_envido, quem_responde, tipo_envido, True
        else:
            if primeiro_da_partida is not None:
                calcular_pontuacao(primeiro_da_partida, 'envido', pontos_envido)
                mostrar_mensagem(f"Empate no {tipo_envido.replace('_', ' ').title()}! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_envido} pontos!")
                return pontos_envido, primeiro_da_partida, tipo_envido, True
            else:
                mostrar_mensagem(f"Empate no {tipo_envido.replace('_', ' ').title()}!")
                return pontos_envido, None, tipo_envido, True
    elif resposta == 'r' and tipo_envido == 'envido':
        mostrar_mensagem(f"{quem_responde.nome} aumentou para Real Envido!")
        return processar_acao_envido(controller, quem_responde, quem_pediu, 'real_envido', 5, primeiro_da_partida)
    elif resposta == 'f' and tipo_envido in ['envido', 'real_envido']:
        mostrar_mensagem(f"{quem_responde.nome} aumentou para Falta Envido!")
        return processar_acao_envido(controller, quem_responde, quem_pediu, 'falta_envido', pontos_falta, primeiro_da_partida)
    elif resposta == 'l' and quem_responde.checaFlor():
        mostrar_mensagem(f"{quem_responde.nome} tem Flor! Envido cancelado.")
        flor_ja_pedida = True
        flor_pode_ser_pedida = False
        envido_pode_ser_pedido = False
        from .acoes import resolver_flor  # Importação tardia para evitar import circular
        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(
            quem_responde, quem_pediu, controller, calcular_pontuacao,
            flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido,
            primeiro_da_partida
        )
        return 0, None, None, True, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    else:
        mostrar_mensagem(f"{quem_responde.nome} recusou o {tipo_envido.replace('_', ' ').title()}! {quem_pediu.nome} ganha 1 ponto.")
        calcular_pontuacao(quem_pediu, 'envido', 1)
        return 1, quem_pediu, tipo_envido, False

def processar_acao_envido(
    controller,
    quem_pediu,
    quem_responde,
    tipo_envido: str,
    pontos_envido: int,
    primeiro_da_partida: Optional[object]
) -> Tuple:
    """
    Processa a ação de Envido, Real Envido e Falta Envido, incluindo escalada de apostas.
    tipo_envido: 'envido', 'real_envido', 'falta_envido'
    pontos_envido: pontos atuais da aposta
    Retorno: Tuple com resultado e estado atualizado
    """
    pontos_falta = 30 - max(controller.jogador1.pontos, controller.jogador2.pontos)
    resposta = obter_resposta_envido(quem_responde, tipo_envido, pontos_falta, controller)
    return processar_resultado_envido(resposta, controller, quem_pediu, quem_responde, tipo_envido, pontos_envido, pontos_falta, primeiro_da_partida)

def obter_decisao_flor_bot(quem_responde):
    """
    Decide a ação do bot quando ambos têm Flor.
    """
    pontos_bot = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
    if 20 <= pontos_bot <= 28:
        return 'boa'
    elif 29 <= pontos_bot <= 33:
        return 'contra-flor'
    else:
        return 'contra-flor e o resto'

def processar_contra_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida):
    """
    Processa a lógica de Contra-Flor e Contra-Flor ao Resto.
    """
    from truco.utils.interface import (
        mostrar_pedido_contra_flor, mostrar_pedido_contra_flor_ao_resto, mostrar_boa, mostrar_resultado_flor, mostrar_mensagem,
        mostrar_aceitou_contra_flor, mostrar_aceitou_contra_flor_ao_resto, mostrar_recusou_contra_flor, mostrar_recusou_contra_flor_ao_resto,
        mostrar_opcao_invalida, prompt_aceite_contra_flor, prompt_aceite_contra_flor_ao_resto
    )
    while True:
        aceita = prompt_aceite_contra_flor(quem_pediu.nome)
        if aceita == 's':
            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
            mostrar_resultado_flor(quem_pediu, quem_responde, pontos1, pontos2)
            if pontos1 > pontos2:
                calcular_pontuacao(quem_pediu, 'flor', 6)
                mostrar_mensagem(f"{quem_pediu.nome} ganhou a Contra-Flor!")
            elif pontos2 > pontos1:
                calcular_pontuacao(quem_responde, 'flor', 6)
                mostrar_mensagem(f"{quem_responde.nome} ganhou a Contra-Flor!")
            else:
                if primeiro_da_partida is not None:
                    calcular_pontuacao(primeiro_da_partida, 'flor', 6)
                    mostrar_mensagem(f"Empate na Contra-Flor! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha 6 pontos!")
                else:
                    mostrar_mensagem(f"Empate na Contra-Flor!")
            break
        elif aceita == 'n':
            mostrar_recusou_contra_flor(quem_pediu.nome, quem_responde.nome)
            calcular_pontuacao(quem_responde, 'flor', 3)
            break
        elif aceita == 'r':
            mostrar_pedido_contra_flor_ao_resto(quem_pediu, quem_responde)
            pontos_bot = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
            if pontos_bot >= 31:
                mostrar_aceitou_contra_flor_ao_resto('Bot')
                pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                mostrar_resultado_flor(quem_pediu, quem_responde, pontos1, pontos2)
                pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                if pontos1 > pontos2:
                    calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                    mostrar_mensagem(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                elif pontos2 > pontos1:
                    calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                    mostrar_mensagem(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                else:
                    if primeiro_da_partida is not None:
                        calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                        mostrar_mensagem(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                    else:
                        mostrar_mensagem(f"Empate na Contra-Flor ao Resto!")
            else:
                mostrar_recusou_contra_flor_ao_resto('Bot', quem_pediu.nome)
                calcular_pontuacao(quem_pediu, 'flor', 6)
            break
        else:
            mostrar_opcao_invalida(['s','n','r'])

def processar_flor_bot(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida):
    """
    Processa a lógica de Flor quando ambos têm Flor e o bot responde.
    """
    from truco.utils.interface import (
        mostrar_boa, mostrar_pedido_contra_flor, mostrar_pedido_contra_flor_ao_resto, mostrar_resultado_flor, mostrar_mensagem,
        mostrar_aceitou_contra_flor_ao_resto, mostrar_recusou_contra_flor_ao_resto
    )
    bot_decision = obter_decisao_flor_bot(quem_responde)
    if bot_decision == 'boa':
        mostrar_boa('Bot')
        calcular_pontuacao(quem_pediu, 'flor', 3)
    elif bot_decision == 'contra-flor':
        mostrar_pedido_contra_flor(quem_pediu, quem_responde)
        processar_contra_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida)
    else:
        mostrar_pedido_contra_flor_ao_resto(quem_pediu, quem_responde)
        pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
        pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
        mostrar_resultado_flor(quem_pediu, quem_responde, pontos1, pontos2)
        pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
        if pontos1 > pontos2:
            calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
            mostrar_mensagem(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
        elif pontos2 > pontos1:
            calcular_pontuacao(quem_responde, 'flor', pontos_resto)
            mostrar_mensagem(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
        else:
            if primeiro_da_partida is not None:
                calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                mostrar_mensagem(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
            else:
                mostrar_mensagem(f"Empate na Contra-Flor ao Resto!")

def processar_flor_jogador(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida):
    """
    Processa a lógica de Flor quando ambos têm Flor e o jogador responde.
    """
    from truco.utils.interface import (
        mostrar_pedido_contra_flor, mostrar_pedido_contra_flor_ao_resto, mostrar_boa, mostrar_resultado_flor, mostrar_mensagem,
        mostrar_aceitou_contra_flor, mostrar_aceitou_contra_flor_ao_resto, mostrar_recusou_contra_flor, mostrar_recusou_contra_flor_ao_resto,
        mostrar_desistiu_flor, mostrar_opcao_invalida, prompt_aceite_contra_flor, prompt_aceite_contra_flor_ao_resto, prompt_acao_flor
    )
    while True:
        resposta = prompt_acao_flor(quem_responde.nome)
        if resposta == 'c':
            mostrar_pedido_contra_flor(quem_pediu, quem_responde)
            processar_contra_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida)
            break
        elif resposta == 'r':
            mostrar_pedido_contra_flor_ao_resto(quem_pediu, quem_responde)
            aceita = prompt_aceite_contra_flor_ao_resto(quem_pediu.nome)
            if aceita == 's':
                mostrar_aceitou_contra_flor_ao_resto(quem_pediu.nome)
                pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                mostrar_resultado_flor(quem_pediu, quem_responde, pontos1, pontos2)
                pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                if pontos1 > pontos2:
                    calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                    mostrar_mensagem(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                elif pontos2 > pontos1:
                    calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                    mostrar_mensagem(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                else:
                    if primeiro_da_partida is not None:
                        calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                        mostrar_mensagem(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                    else:
                        mostrar_mensagem(f"Empate na Contra-Flor ao Resto!")
            else:
                mostrar_recusou_contra_flor_ao_resto(quem_pediu.nome, quem_responde.nome)
                calcular_pontuacao(quem_responde, 'flor', 6)
            break
        elif resposta == 'd':
            mostrar_desistiu_flor(quem_responde.nome)
            break
        else:
            mostrar_opcao_invalida(['c','r','d'])

def resolver_flor(
    quem_pediu,
    quem_responde,
    controller,
    calcular_pontuacao,
    flor_ja_pedida: bool,
    flor_pode_ser_pedida: bool,
    envido_pode_ser_pedido: bool,
    primeiro_da_partida: Optional[object] = None
) -> Tuple[bool, bool, bool]:
    """
    Resolve toda a lógica de Flor, Contra-Flor e Contra-Flor ao Resto.
    Retorna as flags (flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido) atualizadas.

    Parâmetros:
        quem_pediu: Jogador que pediu Flor
        quem_responde: Jogador que responde
        controller: Controller do jogo
        calcular_pontuacao: Função para calcular pontuação
        flor_ja_pedida: Flag se Flor já foi pedida
        flor_pode_ser_pedida: Flag se Flor pode ser pedida
        envido_pode_ser_pedido: Flag se Envido pode ser pedido
        primeiro_da_partida: Jogador que iniciou a mão
    Retorno:
        Tuple[bool, bool, bool]: (flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido)
    """
    from truco.utils.interface import mostrar_pedido_flor, mostrar_sem_flor
    flor_ja_pedida = True
    flor_pode_ser_pedida = False
    mostrar_pedido_flor(quem_pediu)
    if not hasattr(quem_responde, 'checaFlor'):
        raise AttributeError("O objeto 'quem_responde' não possui o método 'checaFlor'.")
    if not quem_responde.checaFlor():
        mostrar_sem_flor(quem_responde, quem_pediu)
        calcular_pontuacao(quem_pediu, 'flor', 3)
        envido_pode_ser_pedido = False
        return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    else:
        if getattr(quem_responde, 'nome', None) == 'Bot':
            processar_flor_bot(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida)
        else:
            processar_flor_jogador(quem_pediu, quem_responde, controller, calcular_pontuacao, primeiro_da_partida)
        return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
