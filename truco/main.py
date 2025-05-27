from truco.utils.interface import mostrar_mao, mostrar_estado, prompt_acao, mostrar_mensagem
from truco.core.game_controller import GameController
from truco.core.rules import calcular_pontuacao
import random

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


def processar_acao_truco(controller, jogador_que_pediu, jogador_que_responde, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida):
    """
    Processa a ação de pedir Truco, incluindo a resposta do adversário e atualização dos estados do jogo.
    """
    controller.pedir_truco(jogador_que_pediu)
    etapa_truco += 1
    truco_pode_ser_pedido = False
    print(f"{jogador_que_pediu.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
    # Decisão automática para bot
    if hasattr(jogador_que_responde, 'aceitar_truco') and jogador_que_responde.nome == 'Bot':
        aceitou = jogador_que_responde.aceitar_truco(controller.pontos_truco, cbr=controller.cbr, controller=controller)
        resposta = 's' if aceitou else 'n'
    else:
        resposta = ''
        while resposta not in ['s', 'n']:
            resposta = input(f"{jogador_que_responde.nome}, você aceita o Truco? (vale {controller.pontos_truco} pontos) [s/n]: ").strip().lower()
            if resposta not in ['s', 'n']:
                print("Por favor, digite 's' para aceitar ou 'n' para correr.")
    if resposta == 's':
        print(f"{jogador_que_responde.nome} aceitou o Truco!")
        truco_pode_ser_pedido = True
        envido_pode_ser_pedido = False
        quem_pode_pedir_truco = jogador_que_responde
        return True, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, False
    else:
        print(f"{jogador_que_responde.nome} correu do Truco!")
        vencedor = controller.aceitar_truco(False)
        controller.resetar_apostas()
        print(f"{vencedor.nome} ganhou a mão!")
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
    # Determina o valor da falta envido
    pontos_falta = 30 - max(controller.jogador1.pontos, controller.jogador2.pontos)
    escalada = [
        ('envido', 2),
        ('real_envido', 3),
        ('falta_envido', pontos_falta)
    ]    # Define o próximo possível aumento
    # Verificar se o jogador que responde tem Flor
    tem_flor = quem_responde.checaFlor() if hasattr(quem_responde, 'checaFlor') else False
    
    if tipo_envido == 'envido':
        if tem_flor:
            opcoes = ['s', 'r', 'f', 'n', 'l']  # aceitar, real envido, falta envido, recusar, flor
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Envido. Aceita [s], aumenta para Real Envido [r], Falta Envido [f], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'r', 'f', 'n']  # aceitar, real envido, falta envido, recusar
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Envido. Aceita [s], aumenta para Real Envido [r], Falta Envido [f] ou recusa [n]? "
    elif tipo_envido == 'real_envido':
        if tem_flor:
            opcoes = ['s', 'f', 'n', 'l']  # aceitar, falta envido, recusar, flor
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Real Envido. Aceita [s], aumenta para Falta Envido [f], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'f', 'n']  # aceitar, falta envido, recusar
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Real Envido. Aceita [s], aumenta para Falta Envido [f] ou recusa [n]? "
    elif tipo_envido == 'falta_envido':
        if tem_flor:
            opcoes = ['s', 'n', 'l']  # aceitar, recusar, flor
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Falta Envido (vale {pontos_falta} pontos). Aceita [s], recusa [n] ou pede Flor [l]? "
        else:
            opcoes = ['s', 'n']  # aceitar, recusar
            prompt = f"{quem_responde.nome}, {quem_pediu.nome} pediu Falta Envido (vale {pontos_falta} pontos). Aceita [s] ou recusa [n]? "
    else:
        return 0, None, None, False    # Bot ou humano
    if hasattr(quem_responde, 'aceitar_envido') and quem_responde.nome == 'Bot':
        # Verifica se o Bot tem Flor, e se tiver, chama Flor automaticamente (tem precedência sobre o Envido)
        if hasattr(quem_responde, 'checaFlor') and quem_responde.checaFlor():
            resposta = 'l'  # chamar flor
        else:
            # Simples: bot aceita se tem 25+ pontos, senão recusa, nunca aumenta
            if tipo_envido == 'envido':
                aceitou = quem_responde.aceitar_envido(2, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
            elif tipo_envido == 'real_envido':
                aceitou = quem_responde.aceitar_envido(3, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
            else:  # falta envido
                aceitou = quem_responde.aceitar_envido(pontos_falta, cbr=controller.cbr, controller=controller)
                resposta = 's' if aceitou else 'n'
    else:
        resposta = ''
        while resposta not in opcoes:
            resposta = input(prompt).strip().lower()
            if resposta not in opcoes:
                print(f"Opção inválida! Digite uma das opções: {', '.join(opcoes)}.")

    # Processa resposta
    if resposta == 's':
        # Disputa de pontos de envido
        pontos1 = quem_pediu.calcular_pontos_envido()
        pontos2 = quem_responde.calcular_pontos_envido()
        print(f"{quem_pediu.nome}: {pontos1} pontos de envido | {quem_responde.nome}: {pontos2} pontos de envido")
        if pontos1 > pontos2:
            calcular_pontuacao(quem_pediu, 'envido', pontos_envido)
            print(f"{quem_pediu.nome} ganhou o {tipo_envido.replace('_', ' ').title()}!")
            return pontos_envido, quem_pediu, tipo_envido, True
        elif pontos2 > pontos1:
            calcular_pontuacao(quem_responde, 'envido', pontos_envido)
            print(f"{quem_responde.nome} ganhou o {tipo_envido.replace('_', ' ').title()}!")
            return pontos_envido, quem_responde, tipo_envido, True
        else:
            # Desempate: quem iniciou a mão vence
            if primeiro_da_partida is not None:
                calcular_pontuacao(primeiro_da_partida, 'envido', pontos_envido)
                print(f"Empate no {tipo_envido.replace('_', ' ').title()}! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_envido} pontos!")
                return pontos_envido, primeiro_da_partida, tipo_envido, True
            else:
                print(f"Empate no {tipo_envido.replace('_', ' ').title()}!")
                return pontos_envido, None, tipo_envido, True
    elif resposta == 'r' and tipo_envido == 'envido':
        # Escala para Real Envido (Envido + Real Envido = 5 pontos)
        print(f"{quem_responde.nome} aumentou para Real Envido!")
        return processar_acao_envido(controller, quem_responde, quem_pediu, 'real_envido', 5, primeiro_da_partida)
    elif resposta == 'f' and tipo_envido in ['envido', 'real_envido']:
        # Escala para Falta Envido
        print(f"{quem_responde.nome} aumentou para Falta Envido!")
        return processar_acao_envido(controller, quem_responde, quem_pediu, 'falta_envido', pontos_falta, primeiro_da_partida)    
    elif resposta == 'l' and quem_responde.checaFlor():
        # Jogador pediu Flor, que tem precedência sobre o Envido
        print(f"{quem_responde.nome} tem Flor! Envido cancelado.")
        flor_ja_pedida = True
        flor_pode_ser_pedida = False
        envido_pode_ser_pedido = False
        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(
            quem_responde, quem_pediu, controller, calcular_pontuacao, 
            flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido, 
            primeiro_da_partida
        )
        # Retorna as flags para o loop principal
        return 0, None, None, True, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    else:
        # Recusou
        print(f"{quem_responde.nome} recusou o {tipo_envido.replace('_', ' ').title()}! {quem_pediu.nome} ganha 1 ponto.")
        calcular_pontuacao(quem_pediu, 'envido', 1)
        return 1, quem_pediu, tipo_envido, False

def main():
    """
    Função principal que executa o loop do jogo Truco Gaúcho.
    """
    print('Bem-vindo ao Truco Gaúcho!')
    nome1 = 'Heitor'
    nome2 = 'Bot'
    controller = GameController(nome1, nome2, bot=True)
    
    # Sorteio para definir quem começa a primeira mão
    primeiro_da_partida = random.choice([controller.jogador1, controller.jogador2])
    controller.proximo_primeiro = primeiro_da_partida
    print(f'Quem começa a primeira mão: {primeiro_da_partida.nome}')
    # Inicializa o jogo
    controller.reiniciar_mao()
    
    while not controller.fim_de_jogo():
        print(f'\nMão nova! Placar: {controller.jogador1.nome} {controller.jogador1.pontos} x {controller.jogador2.pontos} {controller.jogador2.nome}')
        controller.reiniciar_mao()
        controller.historico_rodadas = []  # Limpa o histórico de rodadas no início de cada mão
        # Exibe as cartas do jogador humano antes de qualquer ação do bot
        if controller.jogador1.nome != 'Bot':
            mostrar_mao(controller.jogador1)
        elif controller.jogador2.nome != 'Bot':
            mostrar_mao(controller.jogador2)

        # Flags de controle de propostas para a mão
        etapa_truco = 0  # 0: nada, 1: truco, 2: retruco, 3: vale quatro
        truco_pode_ser_pedido = True
        envido_pode_ser_pedido = True
        flor_pode_ser_pedida = True
        envido_ja_pedido = False
        flor_ja_pedida = False
        # Controle de quem pode pedir o próximo aumento do truco
        quem_pode_pedir_truco = None

        # Controle de quem começa a rodada
        if hasattr(controller, 'proximo_primeiro') and controller.proximo_primeiro:
            # Se houver um jogador definido para começar (vencedor da mão anterior)
            primeiro_jogador = controller.proximo_primeiro
            segundo_jogador = controller.jogador1 if primeiro_jogador == controller.jogador2 else controller.jogador2
            controller.proximo_primeiro = None  # Reset para próxima mão
        else:
            # Por padrão, jogador1 (humano) começa a primeira mão
            primeiro_jogador = controller.jogador1
            segundo_jogador = controller.jogador2
        
        mao_encerrada = False  # Flag para encerrar a mão imediatamente
        for rodada in range(1, 4):
            if controller.mao_decidida():
                break
            mostrar_mensagem(f'\nRodada {rodada}')

            # --- PROMPTS DE TRUCO, ENVIDO, FLOR E AUMENTOS ---
            if controller.pontos_truco > 1 and controller.pontos_truco < 4:
                truco_pode_ser_pedido = True
            carta_idx = None  # Controle para garantir input único por rodada
            while True:
                # Controle de propostas Truco/Retruco/Vale Quatro
                pode_pedir_truco = False
                # Permite pedir truco em qualquer rodada se ainda não foi pedido
                if truco_pode_ser_pedido:
                    if etapa_truco == 0 and controller.pontos_truco == 1:
                        pode_pedir_truco = True
                    elif (etapa_truco == 1 and controller.pontos_truco == 2 and quem_pode_pedir_truco == primeiro_jogador):
                        pode_pedir_truco = True
                    elif (etapa_truco == 2 and controller.pontos_truco == 3 and quem_pode_pedir_truco == primeiro_jogador):
                        pode_pedir_truco = True
                pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
                pode_pedir_real_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                pode_pedir_falta_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido

                if primeiro_jogador == controller.jogador1:
                    mostrar_mao(primeiro_jogador)
                    # Só permite pedir truco se for a vez do humano pedir (quem_pode_pedir_truco == primeiro_jogador ou None no início)
                    prompt = montar_prompt_acao(
                        pode_pedir_truco and (etapa_truco == 0 or quem_pode_pedir_truco is None or quem_pode_pedir_truco == primeiro_jogador),
                        controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, primeiro_jogador, pode_pedir_real_envido, pode_pedir_falta_envido)
                    acao = prompt_acao(prompt)
                    if acao == 't' and pode_pedir_truco and (etapa_truco == 0 or quem_pode_pedir_truco is None or quem_pode_pedir_truco == primeiro_jogador):
                        resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                            controller, primeiro_jogador, segundo_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                        if resultado:
                            continue
                        else:
                            break
                    elif acao == 'e' and pode_pedir_envido:
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        continue
                    elif acao == 'r' and pode_pedir_real_envido:
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        continue
                    elif acao == 'f' and pode_pedir_falta_envido:
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        continue
                    elif acao == 'l' and pode_pedir_flor:
                        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(
                            primeiro_jogador, segundo_jogador, controller, calcular_pontuacao,
                            flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido,
                            primeiro_da_partida
                        )
                        continue
                    elif acao.isdigit():
                        carta_idx = int(acao)
                        if 0 <= carta_idx < len(primeiro_jogador.mao):
                            mostrar_mensagem(f"Você escolheu: {primeiro_jogador.mao[carta_idx].numero} de {primeiro_jogador.mao[carta_idx].naipe}")
                            break
                        else:
                            mostrar_mensagem(f"Índice inválido! Escolha entre 0 e {len(primeiro_jogador.mao)-1}.")
                    else:
                        mostrar_mensagem("Opção inválida! Digite T, E, R, F ou o número da carta.")
                    # Se não pediu truco, passa a vez de pedir truco para o segundo jogador
                    if etapa_truco == 0 and rodada == 1 and quem_pode_pedir_truco is None:
                        quem_pode_pedir_truco = segundo_jogador
                else:
                    # Bot
                    pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_real_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_falta_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
                    # 1. Flor
                    if pode_pedir_flor and primeiro_jogador.pedir_flor(controller.cbr):
                        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(primeiro_jogador, segundo_jogador, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido, primeiro_da_partida)
                        break
                    # 2. Envido, Real Envido ou Falta Envido
                    elif pode_pedir_envido and not envido_ja_pedido and primeiro_jogador.pedir_envido(controller.cbr, controller):
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        break
                    elif pode_pedir_real_envido and not envido_ja_pedido and hasattr(primeiro_jogador, 'pedir_real_envido') and primeiro_jogador.pedir_real_envido(controller.cbr, controller):
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        break
                    elif pode_pedir_falta_envido and not envido_ja_pedido and hasattr(primeiro_jogador, 'pedir_falta_envido') and primeiro_jogador.pedir_falta_envido(controller.cbr, controller):
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
                        if isinstance(resultado, tuple) and len(resultado) == 7:
                            _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                        break
                    else:
                        if etapa_truco == 0 and rodada == 1 and quem_pode_pedir_truco is None:
                            quem_pode_pedir_truco = segundo_jogador
                        break
            if mao_encerrada:
                break  # Sai do for rodada, inicia nova mão
            # Lógica com base em quem é o primeiro jogador
            if primeiro_jogador == controller.jogador1:  # Humano joga primeiro
                carta1 = primeiro_jogador.jogarCarta(carta_idx)
                carta2 = segundo_jogador.jogarCarta(controller.cbr, controller)
            else:  # Bot joga primeiro
                carta1 = primeiro_jogador.jogarCarta(controller.cbr, controller)
                print(f'{primeiro_jogador.nome} jogou: {carta1.numero} de {carta1.naipe}')
                mostrar_mao(segundo_jogador)
                # CORREÇÃO: Só permite pedir truco se quem_pode_pedir_truco for o segundo_jogador
                pode_pedir_truco = False
                if truco_pode_ser_pedido:
                    if etapa_truco == 0 and controller.pontos_truco == 1 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador):
                        pode_pedir_truco = True
                    elif etapa_truco == 1 and controller.pontos_truco == 2 and quem_pode_pedir_truco == segundo_jogador:
                        pode_pedir_truco = True
                    elif etapa_truco == 2 and controller.pontos_truco == 3 and quem_pode_pedir_truco == segundo_jogador:
                        pode_pedir_truco = True
                pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3
                prompt = montar_prompt_acao(pode_pedir_truco, controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, segundo_jogador)
                acao = prompt_acao(prompt)
                if (acao == 't' and pode_pedir_truco and etapa_truco >= 0 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador)):
                    resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                        controller, segundo_jogador, primeiro_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                    if resultado:
                        segundo_jogador.mostrarMao()
                        while True:
                            prompt2 = f"{segundo_jogador.nome}, digite o número da carta para jogar (0 a {len(segundo_jogador.mao)-1}): "
                            acao2 = prompt_acao(prompt2)
                            if acao2.isdigit():
                                carta_idx = int(acao2)
                                if 0 <= carta_idx < len(segundo_jogador.mao):
                                    print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                                    break
                                else:
                                    print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                            else:
                                print("Opção inválida! Digite o número da carta.")
                        carta2 = segundo_jogador.jogarCarta(carta_idx)
                    else:
                        break
                elif acao == 'e' and pode_pedir_envido:
                    # Envido
                    envido_ja_pedido = True
                    envido_pode_ser_pedido = False
                    resultado = processar_acao_envido(controller, segundo_jogador, primeiro_jogador, 'envido', 2, primeiro_da_partida)
                    if isinstance(resultado, tuple) and len(resultado) == 7:
                        _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                    
                    pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3
                    prompt = montar_prompt_acao(pode_pedir_truco, controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, segundo_jogador)
                    acao = prompt_acao(prompt)
                    if (acao == 't' and pode_pedir_truco and etapa_truco >= 0 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador)):
                        resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                            controller, segundo_jogador, primeiro_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                        if resultado:
                            segundo_jogador.mostrarMao()
                            while True:
                                prompt2 = f"{segundo_jogador.nome}, digite o número da carta para jogar (0 a {len(segundo_jogador.mao)-1}): "
                                acao2 = prompt_acao(prompt2)
                                if acao2.isdigit():
                                    carta_idx = int(acao2)
                                    if 0 <= carta_idx < len(segundo_jogador.mao):
                                        print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                                        break
                                    else:
                                        print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                                else:
                                    print("Opção inválida! Digite o número da carta.")
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                        else:
                            break
                    continue
                elif acao == 'r' and pode_pedir_real_envido:
                    # Real Envido
                    envido_ja_pedido = True
                    envido_pode_ser_pedido = False
                    resultado = processar_acao_envido(controller, segundo_jogador, primeiro_jogador, 'real_envido', 3, primeiro_da_partida)
                    if isinstance(resultado, tuple) and len(resultado) == 7:
                        _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                    
                    pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3    
                    prompt = montar_prompt_acao(pode_pedir_truco, controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, segundo_jogador)
                    acao = prompt_acao(prompt)
                    if (acao == 't' and pode_pedir_truco and etapa_truco >= 0 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador)):
                        resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                            controller, segundo_jogador, primeiro_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                        if resultado:
                            segundo_jogador.mostrarMao()
                            while True:
                                prompt2 = f"{segundo_jogador.nome}, digite o número da carta para jogar (0 a {len(segundo_jogador.mao)-1}): "
                                acao2 = prompt_acao(prompt2)
                                if acao2.isdigit():
                                    carta_idx = int(acao2)
                                    if 0 <= carta_idx < len(segundo_jogador.mao):
                                        print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                                        break
                                    else:
                                        print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                                else:
                                    print("Opção inválida! Digite o número da carta.")
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                        else:
                            break
                    continue
                elif acao == 'f' and pode_pedir_falta_envido:
                    # Falta Envido
                    envido_ja_pedido = True
                    envido_pode_ser_pedido = False
                    pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                    resultado = processar_acao_envido(controller, segundo_jogador, primeiro_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
                    if isinstance(resultado, tuple) and len(resultado) == 7:
                        _, _, _, _, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resultado
                    pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3    
                    prompt = montar_prompt_acao(pode_pedir_truco, controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, segundo_jogador)
                    acao = prompt_acao(prompt)
                    if (acao == 't' and pode_pedir_truco and etapa_truco >= 0 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador)):
                        resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                            controller, segundo_jogador, primeiro_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                        if resultado:
                            segundo_jogador.mostrarMao()
                            while True:
                                prompt2 = f"{segundo_jogador.nome}, digite o número da carta para jogar (0 a {len(segundo_jogador.mao)-1}): "
                                acao2 = prompt_acao(prompt2)
                                if acao2.isdigit():
                                    carta_idx = int(acao2)
                                    if 0 <= carta_idx < len(segundo_jogador.mao):
                                        print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                                        break
                                    else:
                                        print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                                else:
                                    print("Opção inválida! Digite o número da carta.")
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                        else:
                            break
                    continue
                elif acao == 'l' and pode_pedir_flor:
                    # Flor
                    flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(
                        segundo_jogador, primeiro_jogador, controller, calcular_pontuacao,
                        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido,
                        primeiro_da_partida
                    )
                    pode_pedir_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_pedir_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3
                    prompt = montar_prompt_acao(pode_pedir_truco, controller.pontos_truco, pode_pedir_envido, pode_pedir_flor, segundo_jogador)
                    acao = prompt_acao(prompt)
                    if (acao == 't' and pode_pedir_truco and etapa_truco >= 0 and (quem_pode_pedir_truco is None or quem_pode_pedir_truco == segundo_jogador)):
                        resultado, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, mao_encerrada = processar_acao_truco(
                            controller, segundo_jogador, primeiro_jogador, etapa_truco, truco_pode_ser_pedido, envido_pode_ser_pedido, quem_pode_pedir_truco, primeiro_da_partida)
                        if resultado:
                            segundo_jogador.mostrarMao()
                            while True:
                                prompt2 = f"{segundo_jogador.nome}, digite o número da carta para jogar (0 a {len(segundo_jogador.mao)-1}): "
                                acao2 = prompt_acao(prompt2)
                                if acao2.isdigit():
                                    carta_idx = int(acao2)
                                    if 0 <= carta_idx < len(segundo_jogador.mao):
                                        print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                                        break
                                    else:
                                        print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                                else:
                                    print("Opção inválida! Digite o número da carta.")
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                        else:
                            break
                    continue
                elif acao.isdigit():
                    carta_idx = int(acao)
                    if 0 <= carta_idx < len(segundo_jogador.mao):
                        print(f"Você escolheu: {segundo_jogador.mao[carta_idx].numero} de {segundo_jogador.mao[carta_idx].naipe}")
                        carta2 = segundo_jogador.jogarCarta(carta_idx)
                    else:
                        print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}.")
                        continue
                else:
                    print("Opção inválida! Digite T, E, R, F, L ou o número da carta.")
                    continue
                
            print(f'{primeiro_jogador.nome} jogou: {carta1.numero} de {carta1.naipe}')
            print(f'{segundo_jogador.nome} jogou: {carta2.numero} de {carta2.naipe}')
            
            # Determine o ganhador e ajusta a ordem para a próxima rodada
            ganhador_rodada, vencedor_mao = controller.jogar_rodada(carta1, carta2, primeiro_jogador, segundo_jogador)

            # Se alguém já venceu 2 rodadas, encerra imediatamente o loop de rodadas
            if controller.mao_decidida():
                vencedor_mao = controller.processar_fim_mao()
                if vencedor_mao:
                    print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
                    controller.mostrar_estado()
                    if vencedor_mao == controller.jogador2:
                        controller.definir_proximo_primeiro(controller.jogador2)
                    else:
                        controller.definir_proximo_primeiro(controller.jogador1)
                else:
                    print('\nA mão terminou empatada!')
                mao_encerrada = True
                break

            # Encerra a mão imediatamente se o mesmo jogador venceu as duas primeiras rodadas (2x0)
            if len(controller.historico_rodadas) == 2 and (controller.historico_rodadas[0] == controller.historico_rodadas[1]) and controller.historico_rodadas[0] in [1,2]:
                vencedor_mao = controller.processar_fim_mao()
                if vencedor_mao:
                    print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
                    controller.mostrar_estado()
                    if vencedor_mao == controller.jogador2:
                        controller.definir_proximo_primeiro(controller.jogador2)
                    else:
                        controller.definir_proximo_primeiro(controller.jogador1)
                else:
                    print('\nA mão terminou empatada!')
                mao_encerrada = True
                break

            # Alternância correta: quem venceu a rodada começa a próxima
            if ganhador_rodada == carta1:
                print(f'{primeiro_jogador.nome} venceu a rodada!')
                # Ordem permanece: primeiro_jogador continua começando
            elif ganhador_rodada == carta2:
                print(f'{segundo_jogador.nome} venceu a rodada!')
                # Inverte: segundo_jogador passa a ser o primeiro
                primeiro_jogador, segundo_jogador = segundo_jogador, primeiro_jogador
            elif ganhador_rodada == "Empate":
                print('Rodada empatada!')
                # Em caso de empate, quem começou continua começando
            else:
                print('Rodada empatada!')
                  
        if mao_encerrada:
            continue  # Encerra a mão atual e vai para a próxima mão

        # Só processa fim de mão se a mão não foi encerrada durante as rodadas
        vencedor_mao = controller.processar_fim_mao()
        if vencedor_mao:
            print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
            # Alternância fixa de quem começa a próxima mão
            if not hasattr(controller, 'alternar_primeiro'):
                controller.alternar_primeiro = (primeiro_da_partida == controller.jogador1)
            controller.alternar_primeiro = not controller.alternar_primeiro
            if controller.alternar_primeiro:
                controller.definir_proximo_primeiro(controller.jogador1)
            else:
                controller.definir_proximo_primeiro(controller.jogador2)
        elif len(controller.historico_rodadas) == 3 and controller.historico_rodadas.count(1) == controller.historico_rodadas.count(2):
            print('\nA mão terminou empatada!')
            controller.historico_rodadas = []  # Limpa histórico em caso de empate
        controller.mostrar_estado()
    
    print(f'\nFIM DE JOGO! Vencedor: {controller.determinar_vencedor().nome} com {controller.determinar_vencedor().pontos} pontos!')

def resolver_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido, primeiro_da_partida=None):
    """
    Resolve toda a lógica de Flor, Contra-Flor e Contra-Flor ao Resto.
    Retorna as flags (flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido) atualizadas.
    """
    flor_ja_pedida = True
    flor_pode_ser_pedida = False
    print(f"{quem_pediu.nome} pediu Flor!")
    if not quem_responde.checaFlor():
        print(f"{quem_responde.nome} não tem Flor! {quem_pediu.nome} ganha 3 pontos.")
        calcular_pontuacao(quem_pediu, 'flor', 3)  # Corrigido: atribui os pontos corretamente
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
            else:  # 34 ou mais
                bot_decision = 'contra-flor e o resto'

            if bot_decision == 'boa':
                print(f"Bot: É BOA! {quem_pediu.nome} ganha 3 pontos.")
                calcular_pontuacao(quem_pediu, 'flor', 3)
            elif bot_decision == 'contra-flor':
                print(f"Bot pediu Contra-Flor!")
                while True:
                    aceita = input(f"{quem_pediu.nome}, seu oponente pediu Contra-Flor (vale 6 pontos). Aceita [s], recusa [n] ou pede Contra-Flor ao Resto [r]? ").strip().lower()
                    if aceita == 's':
                        pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                        pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                        print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                        if pontos1 > pontos2:
                            calcular_pontuacao(quem_pediu, 'flor', 6)
                            print(f"{quem_pediu.nome} ganhou a Contra-Flor!")
                        elif pontos2 > pontos1:
                            calcular_pontuacao(quem_responde, 'flor', 6)
                            print(f"{quem_responde.nome} ganhou a Contra-Flor!")
                        else:
                            # Desempate: quem iniciou a mão vence
                            if primeiro_da_partida is not None:
                                calcular_pontuacao(primeiro_da_partida, 'flor', 6)
                                print(f"Empate na Contra-Flor! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha 6 pontos!")
                            else:
                                print(f"Empate na Contra-Flor!")
                        break
                    elif aceita == 'n':
                        print(f"{quem_pediu.nome} recusou a Contra-Flor! {quem_responde.nome} ganha 3 pontos.")
                        calcular_pontuacao(quem_responde, 'flor', 3)
                        break
                    elif aceita == 'r':
                        print(f"{quem_pediu.nome} pediu Contra-Flor ao Resto!")
                        pontos_bot = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                        if pontos_bot >= 31:  # Bot aceita se tem mão forte
                            print(f"Bot aceitou a Contra-Flor ao Resto!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                                    print(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                                else:
                                    print(f"Empate na Contra-Flor ao Resto!")
                        else:
                            print(f"Bot recusou a Contra-Flor ao Resto! {quem_pediu.nome} ganha 6 pontos.")
                            calcular_pontuacao(quem_pediu, 'flor', 6)
                        break
                    else:
                        print("Opção inválida! Digite 's', 'n' ou 'r'.")
        else:
            while True:
                resposta = input(f"{quem_responde.nome}, seu oponente pediu Flor! Você também tem Flor. Deseja pedir Contra-Flor [c], Contra-Flor ao Resto [r] ou desistir da flor [d]? ").strip().lower()
                if resposta == 'c':
                    print(f"{quem_responde.nome} pediu Contra-Flor!")
                    envido_pode_ser_pedido = False
                    if quem_pediu.nome == 'Bot':
                        pontos_bot = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                        if 20 <= pontos_bot <= 30:
                            print(f"Bot: É BOA! {quem_responde.nome} ganha 3 pontos.")
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        elif 31 <= pontos_bot <= 33:
                            print(f"Bot aceitou a Contra-Flor!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', 6)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', 6)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', 6)
                                    print(f"Empate na Contra-Flor! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha 6 pontos!")
                                else:
                                    print("Empate na Contra-Flor!")
                        else:
                            print(f"Bot pediu Contra-Flor ao Resto!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                                    print(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                                else:
                                    print("Empate na Contra-Flor ao Resto!")
                        break
                    else:
                        aceita = input(f"{quem_pediu.nome}, seu oponente pediu Contra-Flor (vale 6 pontos). Aceita? [s/n]: ").strip().lower()
                        if aceita == 's':
                            print(f"{quem_pediu.nome} aceitou a Contra-Flor!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', 6)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', 6)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', 6)
                                    print(f"Empate na Contra-Flor! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha 6 pontos!")
                                else:
                                    print("Empate na Contra-Flor!")
                        else:
                            print(f"{quem_pediu.nome} recusou a Contra-Flor! {quem_responde.nome} ganha 3 pontos.")
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        break
                elif resposta == 'r':
                    print(f"{quem_responde.nome} pediu Contra-Flor ao Resto!")
                    envido_pode_ser_pedido = False
                    if quem_pediu.nome == 'Bot':
                        pontos_bot = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                        if 20 <= pontos_bot <= 30:
                            print(f"Bot: É BOA! {quem_responde.nome} ganha 3 pontos.")
                            calcular_pontuacao(quem_responde, 'flor', 3)
                        elif 31 <= pontos_bot <= 33:
                            print(f"Bot aceitou a Contra-Flor ao Resto!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                                    print(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                                else:
                                    print("Empate na Contra-Flor ao Resto!")
                        else:
                            print(f"Bot recusou a Contra-Flor ao Resto! {quem_pediu.nome} ganha 6 pontos.")
                            calcular_pontuacao(quem_pediu, 'flor', 6)
                        break
                    else:
                        aceita_resto = input(f"{quem_pediu.nome}, seu oponente pediu Contra-Flor ao Resto. Aceita? [s/n]: ").strip().lower()
                        if aceita_resto == 's':
                            print(f"{quem_pediu.nome} aceitou a Contra-Flor ao Resto!")
                            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                            pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                            if pontos1 > pontos2:
                                calcular_pontuacao(quem_pediu, 'flor', pontos_resto)
                                print(f"{quem_pediu.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(quem_responde, 'flor', pontos_resto)
                                print(f"{quem_responde.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                            else:
                                # Desempate: quem iniciou a mão vence
                                if primeiro_da_partida is not None:
                                    calcular_pontuacao(primeiro_da_partida, 'flor', pontos_resto)
                                    print(f"Empate na Contra-Flor ao Resto! {primeiro_da_partida.nome} (quem iniciou a mão) vence e ganha {pontos_resto} pontos!")
                                else:
                                    print("Empate na Contra-Flor ao Resto!")
                        else:
                            print(f"{quem_pediu.nome} recusou a Contra-Flor ao Resto! {quem_responde.nome} ganha 6 pontos.")
                            calcular_pontuacao(quem_responde, 'flor', 6)
                        break
                elif resposta == 'd':
                    print(f"Heitor: É BOA! {quem_pediu.nome} ganha 3 pontos.")
                    calcular_pontuacao(quem_pediu, 'flor', 3)
                    break
                else:
                    print("Opção inválida! Digite 'c' para Contra-Flor, 'r' para Contra-Flor ao Resto ou Enter para aceitar a Flor.")
            envido_pode_ser_pedido = False
            return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido

if __name__ == '__main__':
    main()