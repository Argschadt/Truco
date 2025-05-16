from truco.core.game_controller import GameController
from truco.core.rules import calcular_pontuacao
import random

def main():
    print('Bem-vindo ao Truco Gaúcho!')
    #nome1 = input('Digite seu nome: ') or 'Jogador'
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
        # Exibe as cartas do jogador humano antes de qualquer ação do bot
        if controller.jogador1.nome != 'Bot':
            controller.jogador1.mostrarMao()
        elif controller.jogador2.nome != 'Bot':
            controller.jogador2.mostrarMao()

        # Flags de controle de propostas para a mão
        truco_etapa = 0  # 0: nada, 1: truco, 2: retruco, 3: vale quatro
        truco_pode_ser_pedido = True
        envido_pode_ser_pedido = True
        flor_pode_ser_pedida = True
        envido_ja_pedido = False
        flor_ja_pedida = False
        # NOVO: controle de quem pode pedir o próximo aumento do truco
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
            print(f'\nRodada {rodada}')
            # Verifica se ainda há cartas disponíveis para jogar
            if len(primeiro_jogador.mao) == 0 or len(segundo_jogador.mao) == 0:
                print("Não há mais cartas para esta rodada!")
                break

            # REMOVIDO: prompt especial de Envido/Flor quando o bot apenas joga carta
            # O prompt só deve aparecer se o bot pedir Truco (já está implementado no bloco correto abaixo)

            # --- PROMPTS DE TRUCO, ENVIDO, FLOR E AUMENTOS ---
            truco_pedido = False
            envido_pedido = False
            # NOVO: Permite pedir Retruco/Vale Quatro nas rodadas seguintes se o Truco foi aceito
            if controller.pontos_truco > 1 and controller.pontos_truco < 4:
                truco_pode_ser_pedido = True
            while True:
                # Controle de propostas Truco/Retruco/Vale Quatro
                pode_pedir_truco = False
                if truco_pode_ser_pedido:
                    if truco_etapa == 0 and controller.pontos_truco == 1:
                        pode_pedir_truco = True
                    elif truco_etapa == 1 and controller.pontos_truco == 2:
                        pode_pedir_truco = True
                    elif truco_etapa == 2 and controller.pontos_truco == 3:
                        pode_pedir_truco = True
                # Envido só pode ser pedido na primeira rodada e uma vez por mão
                # NOVO: Envido só pode ser pedido se NENHUM dos jogadores tiver Flor
                nenhum_tem_flor = not primeiro_jogador.checaFlor() and not segundo_jogador.checaFlor()
                pode_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido and nenhum_tem_flor
                # Flor só pode ser pedida se o jogador realmente tiver e uma vez por mão
                pode_flor = flor_pode_ser_pedida and not flor_ja_pedida and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3

                if primeiro_jogador == controller.jogador1:
                    primeiro_jogador.mostrarMao()
                    prompt = ""
                    if pode_pedir_truco:
                        if controller.pontos_truco == 1:
                            prompt += "[T]ruco"
                        elif controller.pontos_truco == 2:
                            prompt += "[T]ruco (Retruco)"
                        elif controller.pontos_truco == 3:
                            prompt += "[T]ruco (Vale Quatro)"
                    if pode_envido:
                        if prompt:
                            prompt += ", "
                        prompt += "[E]nvido"
                    if pode_flor:
                        if prompt:
                            prompt += ", "
                        prompt += "[F]lor"
                    if prompt:
                        prompt += " ou "
                    prompt += "digite o número da carta para jogar: "
                    acao = input(prompt).strip().lower()
                    if acao == 't' and pode_pedir_truco and (truco_etapa == 0 or quem_pode_pedir_truco is None or quem_pode_pedir_truco == primeiro_jogador):
                        controller.pedir_truco(primeiro_jogador)
                        truco_etapa += 1
                        truco_pode_ser_pedido = False  # Só pode pedir de novo se o adversário aceitar
                        print(f"{primeiro_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                        if segundo_jogador.aceitar_truco(controller.pontos_truco):
                            print(f"{segundo_jogador.nome} aceitou o Truco!")
                            truco_pode_ser_pedido = True  # Agora o adversário pode pedir o próximo nível
                            envido_pode_ser_pedido = False  # Não pode mais pedir Envido após aceitar Truco
                            quem_pode_pedir_truco = segundo_jogador  # Só quem aceitou pode pedir o próximo aumento
                            continue
                        else:
                            print(f"{segundo_jogador.nome} correu do Truco!")
                            vencedor = controller.aceitar_truco(False)
                            controller.resetar_apostas()
                            controller.pontos_truco = 1
                            print(f"{vencedor.nome} ganhou a mão!")
                            controller.historico_rodadas = []
                            controller.mostrar_estado()
                            mao_encerrada = True
                            # Alternância fixa de quem começa a próxima mão
                            if not hasattr(controller, 'alternar_primeiro'):
                                controller.alternar_primeiro = (primeiro_da_partida == controller.jogador1)
                            controller.alternar_primeiro = not controller.alternar_primeiro
                            if controller.alternar_primeiro:
                                controller.definir_proximo_primeiro(controller.jogador1)
                            else:
                                controller.definir_proximo_primeiro(controller.jogador2)
                            break
                    elif acao == 'e' and pode_envido:
                        controller.pedir_envido(primeiro_jogador)
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        print(f"{primeiro_jogador.nome} pediu Envido!")
                        if segundo_jogador.aceitar_envido(2):
                            print(f"{segundo_jogador.nome} aceitou o Envido!")
                            pontos1 = primeiro_jogador.calcular_pontos_envido()
                            pontos2 = segundo_jogador.calcular_pontos_envido()
                            print(f"{primeiro_jogador.nome}: {pontos1} pontos de envido | {segundo_jogador.nome}: {pontos2} pontos de envido")
                            if pontos1 > pontos2:
                                calcular_pontuacao(controller.jogador1, 'envido', 2)
                                print(f"{primeiro_jogador.nome} ganhou o Envido!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(controller.jogador2, 'envido', 2)
                                print(f"{segundo_jogador.nome} ganhou o Envido!")
                            else:
                                print("Empate no Envido!")
                        else:
                            print(f"{segundo_jogador.nome} recusou o Envido! {primeiro_jogador.nome} ganha 1 ponto.")
                            if controller.ultimo_envido == controller.jogador1:
                                calcular_pontuacao(controller.jogador1, 'envido', 1)
                            else:
                                calcular_pontuacao(controller.jogador2, 'envido', 1)
                        # NÃO chama controller.resetar_apostas() aqui!
                        continue
                    elif acao == 'f' and pode_flor:
                        flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(primeiro_jogador, segundo_jogador, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido)
                        continue
                    elif acao == 'f' and not pode_flor:
                        print("Você não tem Flor!")
                    elif acao.isdigit() and int(acao) >= 0 and int(acao) < len(primeiro_jogador.mao):
                        carta_idx = int(acao)
                        break
                    else:
                        print("Opção inválida! Digite T, E, F ou o número da carta.")
                else:
                    # Bot
                    pode_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                    pode_flor = flor_pode_ser_pedida and not flor_ja_pedida and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
                    if pode_pedir_truco and (truco_etapa == 0 or quem_pode_pedir_truco is None or quem_pode_pedir_truco == primeiro_jogador) and primeiro_jogador.pedir_truco():
                        controller.pedir_truco(primeiro_jogador)
                        truco_etapa += 1
                        truco_pode_ser_pedido = False
                        print(f"{primeiro_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                        # NOVO: Permite ao humano pedir Envido/Flor antes de aceitar o Truco
                        if rodada == 1 and (pode_envido or pode_flor):
                            prompt_antes = "Antes de responder ao Truco, deseja pedir "
                            opcoes_antes = []
                            # Só oferece Envido se nenhum dos dois tiver Flor
                            nenhum_tem_flor = not primeiro_jogador.checaFlor() and not segundo_jogador.checaFlor()
                            if pode_envido and nenhum_tem_flor:
                                opcoes_antes.append("[E]nvido")
                            if pode_flor:
                                opcoes_antes.append("[F]lor")
                            prompt_antes += " ou ".join(opcoes_antes) + "? (Digite E, F ou Enter para não pedir): "
                            acao_antes = input(prompt_antes).strip().lower()
                            if acao_antes == 'e' and pode_envido:
                                controller.pedir_envido(segundo_jogador)
                                envido_ja_pedido = True
                                envido_pode_ser_pedido = False
                                print(f"{segundo_jogador.nome} pediu Envido!")
                                if primeiro_jogador.aceitar_envido(2):
                                    print(f"{primeiro_jogador.nome} aceitou o Envido!")
                                    pontos1 = segundo_jogador.calcular_pontos_envido()
                                    pontos2 = primeiro_jogador.calcular_pontos_envido()
                                    print(f"{segundo_jogador.nome}: {pontos1} pontos de envido | {primeiro_jogador.nome}: {pontos2} pontos de envido")
                                    if pontos1 > pontos2:
                                        calcular_pontuacao(segundo_jogador, 'envido', 2)
                                        print(f"{segundo_jogador.nome} ganhou o Envido!")
                                    elif pontos2 > pontos1:
                                        calcular_pontuacao(primeiro_jogador, 'envido', 2)
                                        print(f"{primeiro_jogador.nome} ganhou o Envido!")
                                    else:
                                        print("Empate no Envido!")
                                else:
                                    print(f"{primeiro_jogador.nome} recusou o Envido! {segundo_jogador.nome} ganha 1 ponto.")
                                    if controller.ultimo_envido == segundo_jogador:
                                        calcular_pontuacao(segundo_jogador, 'envido', 1)
                                    else:
                                        calcular_pontuacao(primeiro_jogador, 'envido', 1)
                                # NÃO chama controller.resetar_apostas() aqui!
                                flor_pode_ser_pedida = False
                            elif acao_antes == 'f' and pode_flor:
                                flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido = resolver_flor(segundo_jogador, primeiro_jogador, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido)
                                # Após resolver Envido/Flor, volta ao pedido de Truco
                        resposta_truco = input(f"Seu oponente pediu Truco (vale {controller.pontos_truco} pontos). Aceita? [s/n]: ").strip().lower()
                        if resposta_truco == 's':
                            print(f"{segundo_jogador.nome} aceitou o Truco!")
                            truco_pode_ser_pedido = True
                            envido_pode_ser_pedido = False  # Não pode mais pedir Envido após aceitar Truco
                            quem_pode_pedir_truco = segundo_jogador  # Só quem aceitou pode pedir o próximo aumento
                        else:
                            print(f"{segundo_jogador.nome} correu do Truco!")
                            vencedor = controller.aceitar_truco(False)
                            controller.resetar_apostas()
                            controller.pontos_truco = 1
                            print(f"{vencedor.nome} ganhou a mão!")
                            controller.historico_rodadas = []
                            controller.mostrar_estado()
                            mao_encerrada = True
                            # Alternância fixa de quem começa a próxima mão
                            if not hasattr(controller, 'alternar_primeiro'):
                                controller.alternar_primeiro = (primeiro_da_partida == controller.jogador1)
                            controller.alternar_primeiro = not controller.alternar_primeiro
                            if controller.alternar_primeiro:
                                controller.definir_proximo_primeiro(controller.jogador1)
                            else:
                                controller.definir_proximo_primeiro(controller.jogador2)
                            break
                        break
                    elif pode_envido and not envido_ja_pedido and primeiro_jogador.pedir_envido():
                        controller.pedir_envido(primeiro_jogador)
                        envido_ja_pedido = True
                        envido_pode_ser_pedido = False
                        print(f"{primeiro_jogador.nome} pediu Envido!")
                        if segundo_jogador.aceitar_envido(2):
                            print(f"{segundo_jogador.nome} aceitou o Envido!")
                            pontos1 = primeiro_jogador.calcular_pontos_envido()
                            pontos2 = segundo_jogador.calcular_pontos_envido()
                            print(f"{primeiro_jogador.nome}: {pontos1} pontos de envido | {segundo_jogador.nome}: {pontos2} pontos de envido")
                            if pontos1 > pontos2:
                                calcular_pontuacao(controller.jogador2, 'envido', 2)
                                print(f"{primeiro_jogador.nome} ganhou o Envido!")
                            elif pontos2 > pontos1:
                                calcular_pontuacao(controller.jogador1, 'envido', 2)
                                print(f"{segundo_jogador.nome} ganhou o Envido!")
                            else:
                                print("Empate no Envido!")
                        else:
                            print(f"{segundo_jogador.nome} recusou o Envido! {primeiro_jogador.nome} ganha 1 ponto.")
                            if controller.ultimo_envido == controller.jogador1:
                                calcular_pontuacao(controller.jogador2, 'envido', 1)
                            else:
                                calcular_pontuacao(controller.jogador1, 'envido', 1)
                        break
                    elif pode_flor and primeiro_jogador.pedir_flor():
                        controller.pedir_flor(primeiro_jogador)
                        flor_ja_pedida = True
                        flor_pode_ser_pedida = False
                        print(f"{primeiro_jogador.nome} pediu Flor!")
                        if segundo_jogador.aceitar_flor():
                            print(f"{segundo_jogador.nome} aceitou a Flor!")
                            if controller.ultimo_flor == controller.jogador1:
                                calcular_pontuacao(controller.jogador2, 'flor', 3)
                            else:
                                calcular_pontuacao(controller.jogador1, 'flor', 3)
                            print(f"{primeiro_jogador.nome} ganha 3 pontos de Flor!")
                        else:
                            print(f"{segundo_jogador.nome} recusou a Flor! {primeiro_jogador.nome} ganha 3 pontos.")
                            if controller.ultimo_flor == controller.jogador1:
                                calcular_pontuacao(controller.jogador2, 'flor', 3)
                            else:
                                calcular_pontuacao(controller.jogador1, 'flor', 3)
                        break
                    else:
                        break
                # ...existing code...
            if mao_encerrada:
                break  # Sai do for rodada, inicia nova mão
            # Lógica com base em quem é o primeiro jogador
            if primeiro_jogador == controller.jogador1:  # Humano joga primeiro
                # Só mostra a mão se não for jogada automática
                if not ('carta_idx' in locals()):
                    primeiro_jogador.mostrarMao()
                # Se carta_idx já foi definido pelo input anterior, joga automaticamente
                if 'carta_idx' in locals():
                    carta1 = primeiro_jogador.jogarCarta(carta_idx)
                    carta2 = segundo_jogador.jogarCarta(controller.cbr)
                    del carta_idx  # Limpa para não afetar próximas rodadas
                else:
                    try:
                        carta_idx = int(input(f'{primeiro_jogador.nome}, escolha a carta (0 a {len(primeiro_jogador.mao)-1}): '))
                        # Validação do índice da carta
                        while carta_idx < 0 or carta_idx >= len(primeiro_jogador.mao):
                            print(f"Índice inválido! Escolha entre 0 e {len(primeiro_jogador.mao)-1}")
                            carta_idx = int(input(f'{primeiro_jogador.nome}, escolha a carta: '))
                    except ValueError:
                        print("Entrada inválida! Selecionando a primeira carta disponível.")
                        carta_idx = 0
                    carta1 = primeiro_jogador.jogarCarta(carta_idx)
                    carta2 = segundo_jogador.jogarCarta(controller.cbr)
            else:  # Bot joga primeiro
                # Bot escolhe carta primeiro
                carta1 = primeiro_jogador.jogarCarta(controller.cbr)
                print(f'{primeiro_jogador.nome} jogou: {carta1.numero} de {carta1.naipe}')
                # Mostra a mão do jogador humano
                segundo_jogador.mostrarMao()
                # Permite ao humano pedir truco/retruco/vale quatro, envido e flor antes de jogar
                pode_pedir_truco = False
                if truco_pode_ser_pedido:
                    if truco_etapa == 0 and controller.pontos_truco == 1:
                        pode_pedir_truco = True
                    elif truco_etapa == 1 and controller.pontos_truco == 2:
                        pode_pedir_truco = True
                    elif truco_etapa == 2 and controller.pontos_truco == 3:
                        pode_pedir_truco = True
                pode_envido = rodada == 1 and envido_pode_ser_pedido and not envido_ja_pedido
                pode_flor = flor_pode_ser_pedida and not flor_ja_pedida and segundo_jogador.checaFlor() and len(segundo_jogador.mao) == 3
                prompt = ""
                if pode_pedir_truco:
                    if controller.pontos_truco == 1:
                        prompt += "[T]ruco"
                    elif controller.pontos_truco == 2:
                        prompt += "[T]ruco (Retruco)"
                    elif controller.pontos_truco == 3:
                        prompt += "[T]ruco (Vale Quatro)"
                if pode_envido:
                    if prompt:
                        prompt += ", "
                    prompt += "[E]nvido"
                if pode_flor:
                    if prompt:
                        prompt += ", "
                    prompt += "[F]lor"
                if prompt:
                    prompt += " ou "
                prompt += f"digite o número da carta para jogar: "
                acao = input(prompt).strip().lower()
                if acao == 't' and pode_pedir_truco and (truco_etapa > 0 and quem_pode_pedir_truco == segundo_jogador):
                    controller.pedir_truco(segundo_jogador)
                    truco_pedido = True
                    truco_etapa += 1  # Atualiza etapa do truco
                    truco_pode_ser_pedido = False
                    print(f"{segundo_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                    resposta_bot = primeiro_jogador.aceitar_truco(controller.pontos_truco)
                    if resposta_bot:
                        print(f"{primeiro_jogador.nome} aceitou o Truco!")
                        envido_pode_ser_pedido = False  # Não pode mais pedir Envido após aceitar Truco
                        quem_pode_pedir_truco = primeiro_jogador  # Só quem aceitou pode pedir o próximo aumento
                        segundo_jogador.mostrarMao()
                        try:
                            carta_idx = int(input(f'{segundo_jogador.nome}, escolha a carta (0 a {len(segundo_jogador.mao)-1}): '))
                            while carta_idx < 0 or carta_idx >= len(segundo_jogador.mao):
                                print(f"Índice inválido! Escolha entre 0 e {len(segundo_jogador.mao)-1}")
                                carta_idx = int(input(f'{segundo_jogador.nome}, escolha a carta: '))
                        except ValueError:
                            print("Entrada inválida! Selecionando a primeira carta disponível.")
                            carta_idx = 0
                        carta2 = segundo_jogador.jogarCarta(carta_idx)
                    else:
                        print(f"{primeiro_jogador.nome} correu do Truco!")
                        vencedor = controller.aceitar_truco(False)
                        print(f"{vencedor.nome} ganhou a mão!")
                        controller.mostrar_estado()
                        mao_encerrada = True
                        # Alternância fixa de quem começa a próxima mão
                        if not hasattr(controller, 'alternar_primeiro'):
                            controller.alternar_primeiro = (primeiro_da_partida == controller.jogador1)
                        controller.alternar_primeiro = not controller.alternar_primeiro
                        if controller.alternar_primeiro:
                            controller.definir_proximo_primeiro(controller.jogador1)
                        else:
                            controller.definir_proximo_primeiro(controller.jogador2)
                        break
                elif acao == 'e' and pode_envido:
                    controller.pedir_envido(segundo_jogador)
                    envido_ja_pedido = True
                    envido_pode_ser_pedido = False
                    print(f"{segundo_jogador.nome} pediu Envido!")
                    if primeiro_jogador.aceitar_envido(2):
                        print(f"{primeiro_jogador.nome} aceitou o Envido!")
                        pontos1 = segundo_jogador.calcular_pontos_envido()
                        pontos2 = primeiro_jogador.calcular_pontos_envido()
                        print(f"{segundo_jogador.nome}: {pontos1} pontos de envido | {primeiro_jogador.nome}: {pontos2} pontos de envido")
                        if pontos1 > pontos2:
                            calcular_pontuacao(segundo_jogador, 'envido', 2)
                            print(f"{segundo_jogador.nome} ganhou o Envido!")
                        elif pontos2 > pontos1:
                            calcular_pontuacao(primeiro_jogador, 'envido', 2)
                            print(f"{primeiro_jogador.nome} ganhou o Envido!")
                        else:
                            print("Empate no Envido!")
                    else:
                        print(f"{primeiro_jogador.nome} recusou o Envido! {segundo_jogador.nome} ganha 1 ponto.")
                        if controller.ultimo_envido == segundo_jogador:
                            calcular_pontuacao(segundo_jogador, 'envido', 1)
                        else:
                            calcular_pontuacao(primeiro_jogador, 'envido', 1)
                    continue
                elif acao == 'f' and pode_flor:
                    controller.pedir_flor(segundo_jogador)
                    flor_ja_pedida = True
                    flor_pode_ser_pedida = False
                    print(f"{segundo_jogador.nome} pediu Flor!")
                    if not primeiro_jogador.checaFlor():
                        print(f"{primeiro_jogador.nome} não tem Flor! {segundo_jogador.nome} ganha 3 pontos.")
                        if controller.ultimo_flor == segundo_jogador:
                            calcular_pontuacao(segundo_jogador, 'flor', 3)
                        else:
                            calcular_pontuacao(primeiro_jogador, 'flor', 3)
                        envido_pode_ser_pedido = False
                        break
                    else:
                        # Ambos têm Flor: permitir Contra-Flor e Contra-Flor ao Resto para o humano
                        while True:
                            resposta_flor = input(f"{primeiro_jogador.nome}, seu oponente pediu Flor! Você também tem Flor. Deseja pedir Contra-Flor [c], Contra-Flor ao Resto [r] ou Enter para aceitar a Flor? ").strip().lower()
                            if resposta_flor == 'c':
                                print(f"{primeiro_jogador.nome} pediu Contra-Flor!")
                                envido_pode_ser_pedido = False
                                aceita_contraflor = input(f"{segundo_jogador.nome}, seu oponente pediu Contra-Flor (vale 6 pontos). Aceita? [s/n]: ").strip().lower()
                                if aceita_contraflor == 's':
                                    print(f"{segundo_jogador.nome} aceitou a Contra-Flor!")
                                    pontos1 = primeiro_jogador.calcular_pontos_flor() if hasattr(primeiro_jogador, 'calcular_pontos_flor') else primeiro_jogador.calcular_pontos_envido()
                                    pontos2 = segundo_jogador.calcular_pontos_flor() if hasattr(segundo_jogador, 'calcular_pontos_flor') else segundo_jogador.calcular_pontos_envido()
                                    print(f"{primeiro_jogador.nome}: {pontos1} pontos de Flor | {segundo_jogador.nome}: {pontos2} pontos de Flor")
                                    if pontos1 > pontos2:
                                        calcular_pontuacao(primeiro_jogador, 'flor', 6)
                                        print(f"{primeiro_jogador.nome} ganhou a Contra-Flor!")
                                    elif pontos2 > pontos1:
                                        calcular_pontuacao(segundo_jogador, 'flor', 6)
                                        print(f"{segundo_jogador.nome} ganhou a Contra-Flor!")
                                    else:
                                        print("Empate na Contra-Flor!")
                                else:
                                    print(f"{segundo_jogador.nome} recusou a Contra-Flor! {primeiro_jogador.nome} ganha 3 pontos.")
                                    calcular_pontuacao(primeiro_jogador, 'flor', 3)
                                break
                            elif resposta_flor == 'r':
                                print(f"{primeiro_jogador.nome} pediu Contra-Flor ao Resto!")
                                envido_pode_ser_pedido = False
                                aceita_resto = input(f"{segundo_jogador.nome}, seu oponente pediu Contra-Flor ao Resto. Aceita? [s/n]: ").strip().lower()
                                if aceita_resto == 's':
                                    print(f"{segundo_jogador.nome} aceitou a Contra-Flor ao Resto!")
                                    pontos1 = primeiro_jogador.calcular_pontos_flor() if hasattr(primeiro_jogador, 'calcular_pontos_flor') else primeiro_jogador.calcular_pontos_envido()
                                    pontos2 = segundo_jogador.calcular_pontos_flor() if hasattr(segundo_jogador, 'calcular_pontos_flor') else segundo_jogador.calcular_pontos_envido()
                                    print(f"{primeiro_jogador.nome}: {pontos1} pontos de Flor | {segundo_jogador.nome}: {pontos2} pontos de Flor")
                                    pontos_resto = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
                                    if pontos1 > pontos2:
                                        calcular_pontuacao(primeiro_jogador, 'flor', pontos_resto)
                                        print(f"{primeiro_jogador.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                                    elif pontos2 > pontos1:
                                        calcular_pontuacao(segundo_jogador, 'flor', pontos_resto)
                                        print(f"{segundo_jogador.nome} ganhou a Contra-Flor ao Resto e fez {pontos_resto} pontos!")
                                    else:
                                        print("Empate na Contra-Flor ao Resto!")
                                else:
                                    print(f"{segundo_jogador.nome} recusou a Contra-Flor ao Resto! {primeiro_jogador.nome} ganha 6 pontos.")
                                    calcular_pontuacao(primeiro_jogador, 'flor', 6)
                                break
                            elif resposta_flor == '':
                                print(f"{primeiro_jogador.nome} aceitou a Flor!")
                                pontos1 = primeiro_jogador.calcular_pontos_flor() if hasattr(primeiro_jogador, 'calcular_pontos_flor') else primeiro_jogador.calcular_pontos_envido()
                                pontos2 = segundo_jogador.calcular_pontos_flor() if hasattr(segundo_jogador, 'calcular_pontos_flor') else segundo_jogador.calcular_pontos_envido()
                                print(f"{primeiro_jogador.nome}: {pontos1} pontos de Flor | {segundo_jogador.nome}: {pontos2} pontos de Flor")
                                if pontos1 > pontos2:
                                    calcular_pontuacao(primeiro_jogador, 'flor', 3)
                                    print(f"{primeiro_jogador.nome} ganha 3 pontos de Flor!")
                                elif pontos2 > pontos1:
                                    calcular_pontuacao(segundo_jogador, 'flor', 3)
                                    print(f"{segundo_jogador.nome} ganha 3 pontos de Flor!")
                                else:
                                    print("Empate na Flor!")
                                break
                            else:
                                print("Opção inválida! Digite 'c' para Contra-Flor, 'r' para Contra-Flor ao Resto ou Enter para aceitar a Flor.")
                        break
            print(f'{primeiro_jogador.nome} jogou: {carta1.numero} de {carta1.naipe}')
            print(f'{segundo_jogador.nome} jogou: {carta2.numero} de {carta2.naipe}')
            
            # Determine o ganhador e ajusta a ordem para a próxima rodada
            ganhador, vencedor_mao = controller.jogar_rodada(carta1, carta2)

            # NOVO: Encerra a mão imediatamente se alguém venceu 2 rodadas
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

            # NOVO: Encerra a mão imediatamente se o mesmo jogador venceu as duas primeiras rodadas (2x0)
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
            if ganhador == carta1:
                print(f'{primeiro_jogador.nome} venceu a rodada!')
                # Ordem permanece: primeiro_jogador continua começando
            elif ganhador == carta2:
                print(f'{segundo_jogador.nome} venceu a rodada!')
                # Inverte: segundo_jogador passa a ser o primeiro
                primeiro_jogador, segundo_jogador = segundo_jogador, primeiro_jogador
            elif ganhador == "Empate":
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

def resolver_flor(quem_pediu, quem_responde, controller, calcular_pontuacao, flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido):
    """
    Resolve toda a lógica de Flor, Contra-Flor e Contra-Flor ao Resto.
    Retorna as flags (flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido) atualizadas.
    """
    flor_ja_pedida = True
    flor_pode_ser_pedida = False
    print(f"{quem_pediu.nome} pediu Flor!")
    if not quem_responde.checaFlor():
        print(f"{quem_responde.nome} não tem Flor! {quem_pediu.nome} ganha 3 pontos.")
        if controller.ultimo_flor == quem_pediu:
            calcular_pontuacao(quem_pediu, 'flor', 3)
        else:
            calcular_pontuacao(quem_responde, 'flor', 3)
        envido_pode_ser_pedido = False
        return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    else:
        # Ambos têm Flor
        if quem_responde.nome == 'Bot':
            # Bot sempre aceita a Flor (pode ser melhorado)
            print(f"Bot aceitou a Flor!")
            pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
            pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
            print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
            if pontos1 > pontos2:
                calcular_pontuacao(quem_pediu, 'flor', 3)
                print(f"{quem_pediu.nome} ganha 3 pontos de Flor!")
            elif pontos2 > pontos1:
                calcular_pontuacao(quem_responde, 'flor', 3)
                print(f"{quem_responde.nome} ganha 3 pontos de Flor!")
            else:
                print("Empate na Flor!")
            envido_pode_ser_pedido = False
            return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
        else:
            while True:
                resposta = input(f"{quem_responde.nome}, seu oponente pediu Flor! Você também tem Flor. Deseja pedir Contra-Flor [c], Contra-Flor ao Resto [r] ou Enter para aceitar a Flor? ").strip().lower()
                if resposta == 'c':
                    print(f"{quem_responde.nome} pediu Contra-Flor!")
                    envido_pode_ser_pedido = False
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
                            print("Empate na Contra-Flor!")
                    else:
                        print(f"{quem_pediu.nome} recusou a Contra-Flor! {quem_responde.nome} ganha 3 pontos.")
                        calcular_pontuacao(quem_responde, 'flor', 3)
                    break
                elif resposta == 'r':
                    print(f"{quem_responde.nome} pediu Contra-Flor ao Resto!")
                    envido_pode_ser_pedido = False
                    aceita = input(f"{quem_pediu.nome}, seu oponente pediu Contra-Flor ao Resto. Aceita? [s/n]: ").strip().lower()
                    if aceita == 's':
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
                            print("Empate na Contra-Flor ao Resto!")
                    else:
                        print(f"{quem_pediu.nome} recusou a Contra-Flor ao Resto! {quem_responde.nome} ganha 6 pontos.")
                        calcular_pontuacao(quem_responde, 'flor', 6)
                    break
                elif resposta == '':
                    print(f"{quem_responde.nome} aceitou a Flor!")
                    pontos1 = quem_pediu.calcular_pontos_flor() if hasattr(quem_pediu, 'calcular_pontos_flor') else quem_pediu.calcular_pontos_envido()
                    pontos2 = quem_responde.calcular_pontos_flor() if hasattr(quem_responde, 'calcular_pontos_flor') else quem_responde.calcular_pontos_envido()
                    print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")
                    if pontos1 > pontos2:
                        calcular_pontuacao(quem_pediu, 'flor', 3)
                        print(f"{quem_pediu.nome} ganha 3 pontos de Flor!")
                    elif pontos2 > pontos1:
                        calcular_pontuacao(quem_responde, 'flor', 3)
                        print(f"{quem_responde.nome} ganha 3 pontos de Flor!")
                    else:
                        print("Empate na Flor!")
                    break
                else:
                    print("Opção inválida! Digite 'c' para Contra-Flor, 'r' para Contra-Flor ao Resto ou Enter para aceitar a Flor.")
            envido_pode_ser_pedido = False
            return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido
    return flor_ja_pedida, flor_pode_ser_pedida, envido_pode_ser_pedido

if __name__ == '__main__':
    main()