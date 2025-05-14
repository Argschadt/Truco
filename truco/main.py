from truco.core.game_controller import GameController

def main():
    print('Bem-vindo ao Truco Gaúcho!')
    #nome1 = input('Digite seu nome: ') or 'Jogador'
    nome1 = 'Heitor'
    nome2 = 'Bot'
    controller = GameController(nome1, nome2, bot=True)
    
    # Inicializa o jogo
    controller.reiniciar_mao()
    
    while not controller.fim_de_jogo():
        print(f'\nMão nova! Placar: {controller.jogador1.nome} {controller.jogador1.pontos} x {controller.jogador2.pontos} {controller.jogador2.nome}')
        controller.reiniciar_mao()
        
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
                
            # --- PROMPTS DE TRUCO, ENVIDO, FLOR E AUMENTOS ---
            # Só pode pedir truco se ainda não foi pedido nesta mão
            truco_pedido = False
            envido_pedido = False
            while True:
                if controller.pontos_truco < 12 and not truco_pedido:
                    # Só pode pedir truco se não foi pedido nesta mão
                    # E só pode pedir retruco/vale quatro se o adversário pediu o truco anterior
                    pode_pedir_truco = True
                    if controller.pontos_truco > 1 and controller.ultimo_truco == primeiro_jogador:
                        pode_pedir_truco = False
                    if primeiro_jogador == controller.jogador1:
                        primeiro_jogador.mostrarMao()
                        pode_envido = rodada == 1 and not envido_pedido
                        pode_flor = primeiro_jogador.flor and len(primeiro_jogador.mao) == 3
                        prompt = "[T]ruco"
                        if controller.pontos_truco == 2:
                            prompt = "[T]ruco (Retruco)"
                        elif controller.pontos_truco == 3:
                            prompt = "[T]ruco (Vale Quatro)"
                        if not pode_pedir_truco:
                            prompt = prompt.replace("[T]ruco", "(Truco já pedido por você)")
                        if pode_envido:
                            prompt += ", [E]nvido"
                        if pode_flor:
                            prompt += ", [F]lor"
                        prompt += " ou digite o número da carta para jogar: "
                        acao = input(prompt).strip().lower()
                        if acao == 't' and pode_pedir_truco:
                            controller.pedir_truco(primeiro_jogador)
                            truco_pedido = True
                            print(f"{primeiro_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                            if segundo_jogador.aceitar_truco(controller.pontos_truco):
                                print(f"{segundo_jogador.nome} aceitou o Truco!")
                            else:
                                print(f"{segundo_jogador.nome} correu do Truco!")
                                vencedor = controller.aceitar_truco(False)
                                print(f"{vencedor.nome} ganhou a mão!")
                                controller.historico_rodadas = []  # Limpa histórico para não dar pontos extras
                                controller.mostrar_estado()
                                mao_encerrada = True
                                break  # Sai do while True
                            # Após pedir truco, não pode pedir mais nada
                            break
                        elif acao == 'e' and pode_envido:
                            controller.pedir_envido(primeiro_jogador)
                            envido_pedido = True
                            print(f"{primeiro_jogador.nome} pediu Envido!")
                            if segundo_jogador.aceitar_envido(2):
                                print(f"{segundo_jogador.nome} aceitou o Envido!")
                                pontos1 = primeiro_jogador.calcular_pontos_envido()
                                pontos2 = segundo_jogador.calcular_pontos_envido()
                                print(f"{primeiro_jogador.nome}: {pontos1} pontos de envido | {segundo_jogador.nome}: {pontos2} pontos de envido")
                                if pontos1 > pontos2:
                                    print(f"{primeiro_jogador.nome} ganhou o Envido!")
                                    controller.jogador1.pontos += 2
                                elif pontos2 > pontos1:
                                    print(f"{segundo_jogador.nome} ganhou o Envido!")
                                    controller.jogador2.pontos += 2
                                else:
                                    print("Empate no Envido!")
                            else:
                                print(f"{segundo_jogador.nome} recusou o Envido! {primeiro_jogador.nome} ganha 1 ponto.")
                                controller.jogador1.pontos += 1
                            # Após Envido, volta para o prompt de truco/normal
                            continue
                        elif acao == 'f' and pode_flor:
                            controller.pedir_flor(primeiro_jogador)
                            print(f"{primeiro_jogador.nome} pediu Flor!")
                            if segundo_jogador.aceitar_flor():
                                print(f"{segundo_jogador.nome} aceitou a Flor!")
                                print(f"{primeiro_jogador.nome} ganha 3 pontos de Flor!")
                                controller.jogador1.pontos += 3
                            else:
                                print(f"{segundo_jogador.nome} recusou a Flor! {primeiro_jogador.nome} ganha 3 pontos.")
                                controller.jogador1.pontos += 3
                            break
                        elif acao == 'f' and not pode_flor:
                            print("Você não tem Flor!")
                        elif acao.isdigit() and int(acao) >= 0 and int(acao) < len(primeiro_jogador.mao):
                            carta_idx = int(acao)
                            break
                        else:
                            print("Opção inválida! Digite T, E, F ou o número da carta.")
                    else:
                        pode_envido = rodada == 1 and not envido_pedido
                        pode_flor = primeiro_jogador.flor and len(primeiro_jogador.mao) == 3
                        if not truco_pedido and primeiro_jogador.pedir_truco():
                            controller.pedir_truco(primeiro_jogador)
                            truco_pedido = True
                            print(f"{primeiro_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                            if segundo_jogador.aceitar_truco(controller.pontos_truco):
                                print(f"{segundo_jogador.nome} aceitou o Truco!")
                            else:
                                print(f"{segundo_jogador.nome} correu do Truco!")
                                vencedor = controller.aceitar_truco(False)
                                print(f"{vencedor.nome} ganhou a mão!")
                                controller.historico_rodadas = []  # Limpa histórico para não dar pontos extras
                                controller.mostrar_estado()
                                mao_encerrada = True
                                break  # Sai do while True
                            break
                        elif pode_envido and not envido_pedido and primeiro_jogador.pedir_envido():
                            controller.pedir_envido(primeiro_jogador)
                            envido_pedido = True
                            print(f"{primeiro_jogador.nome} pediu Envido!")
                            if segundo_jogador.aceitar_envido(2):
                                print(f"{segundo_jogador.nome} aceitou o Envido!")
                                pontos1 = primeiro_jogador.calcular_pontos_envido()
                                pontos2 = segundo_jogador.calcular_pontos_envido()
                                print(f"{primeiro_jogador.nome}: {pontos1} pontos de envido | {segundo_jogador.nome}: {pontos2} pontos de envido")
                                if pontos1 > pontos2:
                                    print(f"{primeiro_jogador.nome} ganhou o Envido!")
                                    controller.jogador2.pontos += 2
                                elif pontos2 > pontos1:
                                    print(f"{segundo_jogador.nome} ganhou o Envido!")
                                    controller.jogador1.pontos += 2
                                else:
                                    print("Empate no Envido!")
                            else:
                                print(f"{segundo_jogador.nome} recusou o Envido! {primeiro_jogador.nome} ganha 1 ponto.")
                                controller.jogador2.pontos += 1
                            continue
                        elif pode_flor and primeiro_jogador.pedir_flor():
                            controller.pedir_flor(primeiro_jogador)
                            print(f"{primeiro_jogador.nome} pediu Flor!")
                            if segundo_jogador.aceitar_flor():
                                print(f"{segundo_jogador.nome} aceitou a Flor!")
                                print(f"{primeiro_jogador.nome} ganha 3 pontos de Flor!")
                                controller.jogador2.pontos += 3
                            else:
                                print(f"{segundo_jogador.nome} recusou a Flor! {primeiro_jogador.nome} ganha 3 pontos.")
                                controller.jogador2.pontos += 3
                            break
                        else:
                            break
                else:
                    break
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
                # Permite ao humano pedir truco/retruco/vale quatro antes de jogar, se ainda não foi pedido nesta rodada
                pode_pedir_truco = not truco_pedido and controller.pontos_truco < 12
                prompt = "[T]ruco" if pode_pedir_truco else ""
                if controller.pontos_truco == 2 and pode_pedir_truco:
                    prompt = "[T]ruco (Retruco)"
                elif controller.pontos_truco == 3 and pode_pedir_truco:
                    prompt = "[T]ruco (Vale Quatro)"
                if prompt:
                    prompt += " ou "
                prompt += f"digite o número da carta para jogar: "
                acao = input(prompt).strip().lower()
                if acao == 't' and pode_pedir_truco:
                    controller.pedir_truco(segundo_jogador)
                    truco_pedido = True
                    print(f"{segundo_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                    resposta_bot = primeiro_jogador.aceitar_truco(controller.pontos_truco)
                    if resposta_bot:
                        print(f"{primeiro_jogador.nome} aceitou o Truco!")
                        # Após aceitar, permite novo prompt de retruco/vale quatro antes de jogar a carta
                        segundo_jogador.mostrarMao()
                        pode_pedir_truco = controller.pontos_truco < 12
                        prompt = "[T]ruco" if pode_pedir_truco else ""
                        if controller.pontos_truco == 2 and pode_pedir_truco:
                            prompt = "[T]ruco (Retruco)"
                        elif controller.pontos_truco == 3 and pode_pedir_truco:
                            prompt = "[T]ruco (Vale Quatro)"
                        if prompt:
                            prompt += " ou "
                        prompt += f"digite o número da carta para jogar: "
                        acao2 = input(prompt).strip().lower()
                        if acao2 == 't' and pode_pedir_truco:
                            controller.pedir_truco(segundo_jogador)
                            truco_pedido = True
                            print(f"{segundo_jogador.nome} pediu Truco! (vale {controller.pontos_truco} pontos)")
                            resposta_bot2 = primeiro_jogador.aceitar_truco(controller.pontos_truco)
                            if resposta_bot2:
                                print(f"{primeiro_jogador.nome} aceitou o Truco!")
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
                                break
                        elif acao2.isdigit() and int(acao2) >= 0 and int(acao2) < len(segundo_jogador.mao):
                            carta_idx = int(acao2)
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                        else:
                            print("Opção inválida! Digite T ou o número da carta.")
                            carta_idx = 0
                            carta2 = segundo_jogador.jogarCarta(carta_idx)
                    else:
                        print(f"{primeiro_jogador.nome} correu do Truco!")
                        vencedor = controller.aceitar_truco(False)
                        print(f"{vencedor.nome} ganhou a mão!")
                        controller.mostrar_estado()
                        mao_encerrada = True
                        break
                    continue
                elif acao.isdigit() and int(acao) >= 0 and int(acao) < len(segundo_jogador.mao):
                    carta_idx = int(acao)
                    carta2 = segundo_jogador.jogarCarta(carta_idx)
                else:
                    print("Opção inválida! Digite T ou o número da carta.")
                    carta_idx = 0
                    carta2 = segundo_jogador.jogarCarta(carta_idx)
            
            print(f'{primeiro_jogador.nome} jogou: {carta1.numero} de {carta1.naipe}')
            print(f'{segundo_jogador.nome} jogou: {carta2.numero} de {carta2.naipe}')
            
            # Determine o ganhador e ajusta a ordem para a próxima rodada
            ganhador, vencedor_mao = controller.jogar_rodada(carta1, carta2)

            # NOVO: Se alguém venceu a mão, encerra imediatamente
            if vencedor_mao:
                print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
                controller.mostrar_estado()
                if vencedor_mao == controller.jogador2:
                    controller.definir_proximo_primeiro(controller.jogador2)
                else:
                    controller.definir_proximo_primeiro(controller.jogador1)
                mao_encerrada = True
                break  # Sai do for rodada, inicia nova mão

            # Verifica se algum jogador já venceu 2 rodadas e encerra a mão
            if controller.historico_rodadas.count(1) == 2 or controller.historico_rodadas.count(2) == 2:
                vencedor_mao = controller.processar_fim_mao()
                if vencedor_mao:
                    print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
                    if vencedor_mao == controller.jogador2:
                        controller.definir_proximo_primeiro(controller.jogador2)
                    else:
                        controller.definir_proximo_primeiro(controller.jogador1)
                else:
                    print('\nA mão terminou empatada!')
                controller.mostrar_estado()
                break  # Sai do for rodada, inicia nova mão

            if ganhador == carta1:
                print(f'{primeiro_jogador.nome} venceu a rodada!')
                # Ordem permanece a mesma para a próxima rodada (vencedor começa)
            elif ganhador == carta2:
                print(f'{segundo_jogador.nome} venceu a rodada!')
                # Inverte a ordem para a próxima rodada (vencedor começa)
                primeiro_jogador, segundo_jogador = segundo_jogador, primeiro_jogador
            else:
                print('Rodada empatada!')
                # Em caso de empate, quem começou continua começando
                  
        if mao_encerrada:
            continue  # Encerra a mão atual e vai para a próxima mão
        
        vencedor_mao = controller.processar_fim_mao()
        if vencedor_mao:
            print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
            # Define quem começa a próxima mão
            if vencedor_mao == controller.jogador2:  # Se o bot venceu
                controller.definir_proximo_primeiro(controller.jogador2)
            else:
                controller.definir_proximo_primeiro(controller.jogador1)
        else:
            print('\nA mão terminou empatada!')
        controller.mostrar_estado()
    
    print(f'\nFIM DE JOGO! Vencedor: {controller.determinar_vencedor().nome} com {controller.determinar_vencedor().pontos} pontos!')

if __name__ == '__main__':
    main()