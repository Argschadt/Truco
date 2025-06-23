from truco.core.rules import calcular_pontuacao
from truco.utils.interface import mostrar_mao, mostrar_estado, prompt_acao, mostrar_mensagem, mostrar_resultado_envido, mostrar_resultado_flor, mostrar_vencedor_rodada, mostrar_empate_rodada, mostrar_vencedor_mao, mostrar_mao_terminou_empatada

# Funções de ações especiais do Truco Gaúcho

def processar_acao_truco(controller, jogador_que_pediu, jogador_que_responde, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida):
    """
    Processa a ação de pedir Truco, incluindo a resposta do adversário e atualização dos estados do jogo.
    """
    controller.pedir_truco(jogador_que_pediu)
    etapa_truco += 1
    truco_pode_ser_pedido = False
    mostrar_mensagem(f"{jogador_que_pediu.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
    # Decisão automática para bot
    if hasattr(jogador_que_responde, 'aceitar_truco') and jogador_que_responde.nome == 'Bot':
        aceitou = jogador_que_responde.aceitar_truco(controller.pontos_truco, cbr=controller.cbr, controller=controller)
        resposta = 's' if aceitou else 'n'
    else:
        resposta = ''
        while resposta not in ['s', 'n']:
            resposta = prompt_acao(f"{jogador_que_responde.nome}, você aceita o Truco? (vale {controller.pontos_truco} pontos) [s/n]: ")
            if resposta not in ['s', 'n']:
                mostrar_mensagem("Por favor, digite 's' para aceitar ou 'n' para correr.")
    if resposta == 's':
        mostrar_mensagem(f"{jogador_que_responde.nome} aceitou o Truco!")
        truco_pode_ser_pedido = True
        envido_pode_ser_pedido = False
        quem_pode_pedir_truco = jogador_que_responde
        return True, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, False
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

def processar_acao_envido(controller, quem_pediu, quem_responde, tipo_envido, pontos_envido, primeiro_da_partida):
    """
    Processa a ação de Envido, Real Envido e Falta Envido, incluindo escalada de apostas.
    tipo_envido: 'envido', 'real_envido', 'falta_envido'
    pontos_envido: pontos atuais da aposta
    """
    pontos_falta = 30 - max(controller.jogador1.pontos, controller.jogador2.pontos)
    escalada = [
        ('envido', 2),
        ('real_envido', 3),
        ('falta_envido', pontos_falta)
    ]
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
        return 0, None, None, False
    if hasattr(quem_responde, 'aceitar_envido') and quem_responde.nome == 'Bot':
        if hasattr(quem_responde, 'checaFlor') and quem_responde.checaFlor():
            resposta = 'l'
        else:
            if tipo_envido == 'envido':
                aceitou = quem_responde.aceitar_envido(2, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
            elif tipo_envido == 'real_envido':
                aceitou = quem_responde.aceitar_envido(3, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
            else:
                aceitou = quem_responde.aceitar_envido(pontos_falta, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
    else:
        resposta = ''
        while resposta not in opcoes:
            resposta = input(prompt).strip().lower()
            if resposta not in opcoes:
                print(f"Opção inválida! Digite uma das opções: {', '.join(opcoes)}.")
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
        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedida = resolver_flor(
            quem_responde, quem_pediu, controller, calcular_pontuacao,
            flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedida,
            primeiro_da_partida
        )
        return 0, None, None, True, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedida
    else:
        mostrar_mensagem(f"{quem_responde.nome} recusou o {tipo_envido.replace('_', ' ').title()}! {quem_pediu.nome} ganha 1 ponto.")
        calcular_pontuacao(quem_pediu, 'envido', 1)
        return 1, quem_pediu, tipo_envido, False

def resolver_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido, primeiro_da_partida=None):
    """
    Resolve toda a lógica de Flor, Contra-Flor e Contra-Flor ao Resto.
    Retorna as flags (flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido) atualizadas.
    """
    from truco.utils.interface import (
        mostrar_pedido_flor, mostrar_sem_flor, mostrar_pedido_contra_flor, mostrar_pedido_contra_flor_ao_resto,
        mostrar_boa, mostrar_resultado_flor, mostrar_mensagem, mostrar_aceitou_contra_flor, mostrar_aceitou_contra_flor_ao_resto,
        mostrar_recusou_contra_flor, mostrar_recusou_contra_flor_ao_resto, mostrar_desistiu_flor, mostrar_opcao_invalida,
        prompt_aceite_contra_flor, prompt_aceite_contra_flor_ao_resto, prompt_acao_flor
    )
    flor_ja_pedida = True
    flor_pode_ser_pedida = False
    mostrar_pedido_flor(quem_pediu)
    if not quem_responde.checaFlor():
        mostrar_sem_flor(quem_responde, quem_pediu)
        calcular_pontuacao(quem_pediu, 'flor', 3)
        envido_pode_ser_pedido = False
        return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    else:
        # Ambos têm Flor
        if quem_responde.nome == 'Bot':
            pontos_bot = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
            if 20 <= pontos_bot <= 28:
                bot_decision = 'boa'
            elif 29 <= pontos_bot <= 33:
                bot_decision = 'contra-flor'
            else:
                bot_decision = 'contra-flor e o resto'
            if bot_decision == 'boa':
                mostrar_boa('Bot')
                calcular_pontuacao(quem_pediu, 'flor', 3)
            elif bot_decision == 'contra-flor':
                mostrar_pedido_contra_flor(quem_pediu, quem_responde)
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
        else:
            while True:
                resposta = prompt_acao_flor(quem_responde.nome)
                if resposta == 'c':
                    mostrar_pedido_contra_flor(quem_pediu, quem_responde)
                    envido_pode_ser_pedido = False
                    if quem_pediu.nome == 'Bot':
                        pontos_bot = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                        if 20 <= pontos_bot <= 30:
                            mostrar_boa('Bot')
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        elif 31 <= pontos_bot <= 33:
                            mostrar_aceitou_contra_flor('Bot')
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
                    else:
                        aceita = prompt_aceite_contra_flor(quem_pediu.nome)
                        if aceita == 's':
                            mostrar_aceitou_contra_flor(quem_pediu.nome)
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
                        else:
                            mostrar_recusou_contra_flor(quem_pediu.nome, quem_responde.nome)
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        break
                elif resposta == 'r':
                    mostrar_pedido_contra_flor_ao_resto(quem_pediu, quem_responde)
                    envido_pode_ser_pedido = False
                    if quem_pediu.nome == 'Bot':
                        pontos_bot = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                        if 20 <= pontos_bot <= 30:
                            mostrar_boa('Bot')
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        elif 31 <= pontos_bot <= 33:
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
                            mostrar_recusou_contra_flor_ao_resto('Bot', quem_responde.nome)
                            calcular_pontuacao(quem_responde, 'flor', 6)
                        break
                    else:
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
            envido_pode_ser_pedido = False
            return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
