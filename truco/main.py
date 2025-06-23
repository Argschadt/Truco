from truco.utils.interface import mostrar_mao, mostrar_estado, prompt_acao, mostrar_mensagem, mostrar_resultado_envido, mostrar_resultado_flor, mostrar_vencedor_rodada, mostrar_empate_rodada, mostrar_vencedor_mao, mostrar_mao_terminou_empatada
from truco.core.game_controller import GameController
from truco.core.rules import calcular_pontuacao
from truco.core.acoes import processar_acao_truco, processar_acao_envido, resolver_flor
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

def turno_jogador_humano(primeiro_jogador, segundo_jogador, controller, estado, primeiro_da_partida, rodada):
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
                controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida)
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
    # Checa possibilidades de pedir envido, real envido, falta envido ou flor
    pode_pedir_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
    pode_pedir_real_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
    pode_pedir_falta_envido = rodada == 1 and estado['pode_envido'] and not estado['envido_pedido']
    pode_pedir_flor = estado['pode_flor'] and not estado['flor_pedida'] and primeiro_jogador.checaFlor() and len(primeiro_jogador.mao) == 3
    # 1. Flor
    if pode_pedir_flor and primeiro_jogador.pedir_flor(controller.cbr, controller):
        estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resolver_flor(primeiro_jogador, segundo_jogador, controller, calcular_pontuacao, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'], primeiro_da_partida)
        return None, estado, mao_encerrada
    # 2. Envido, Real Envido ou Falta Envido
    elif pode_pedir_envido and not estado['envido_pedido'] and primeiro_jogador.pedir_envido(controller.cbr, controller):
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'envido', 2, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return None, estado, mao_encerrada
    elif pode_pedir_real_envido and not estado['envido_pedido'] and hasattr(primeiro_jogador, 'pedir_real_envido') and primeiro_jogador.pedir_real_envido(controller.cbr):
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'real_envido', 3, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return None, estado, mao_encerrada
    elif pode_pedir_falta_envido and not estado['envido_pedido'] and hasattr(primeiro_jogador, 'pedir_falta_envido') and primeiro_jogador.pedir_falta_envido(controller.cbr):
        estado['envido_pedido'] = True
        estado['pode_envido'] = False
        pontos_falta = 15 - max(controller.jogador1.pontos, controller.jogador2.pontos)
        resultado = processar_acao_envido(controller, primeiro_jogador, segundo_jogador, 'falta_envido', pontos_falta, primeiro_da_partida)
        if isinstance(resultado, tuple) and len(resultado) == 7:
            _, _, _, _, estado['flor_pedida'], estado['pode_flor'], estado['pode_envido'] = resultado
        return None, estado, mao_encerrada
    # 3. Truco (bot só pede truco se for a vez dele)
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
            controller, primeiro_jogador, segundo_jogador, estado['truco_fase'], estado['pode_truco'], estado['pode_envido'], estado['vez_truco'], primeiro_da_partida)
        if resultado:
            return None, estado, mao_encerrada
    # 4. Jogar carta (bot escolhe automaticamente)
    carta_idx = primeiro_jogador.escolher_carta(controller.cbr, controller) if hasattr(primeiro_jogador, 'escolher_carta') else 0
    return carta_idx, estado, mao_encerrada

def main():
    """
    Função principal que executa o loop do jogo Truco Gaúcho.
    """
    mostrar_mensagem('Bem-vindo ao Truco Gaúcho!')
    nome1 = 'Heitor'
    nome2 = 'Bot'
    controller = GameController(nome1, nome2, bot=True)
    
    # Sorteio para definir quem começa a primeira mão
    primeiro_da_partida = random.choice([controller.jogador1, controller.jogador2])
    controller.proximo_primeiro = primeiro_da_partida
    mostrar_mensagem(f'Quem começa a primeira mão: {primeiro_da_partida.nome}')

    def novo_estado_mao():
        return {
            'truco_fase': 0,  # 0: nada, 1: truco, 2: retruco, 3: vale quatro
            'pode_truco': True,
            'pode_envido': True,
            'pode_flor': True,
            'envido_pedido': False,
            'flor_pedida': False,
            'vez_truco': None,
        }

    while not controller.fim_de_jogo():
        # Exibe o estado atual do jogo e reinicia a mão
        mostrar_estado(controller)
        controller.reiniciar_mao()
        controller.historico_rodadas = []
        # Exibe as cartas do jogador humano antes de qualquer ação do bot
        if controller.jogador1.nome != 'Bot':
            mostrar_mao(controller.jogador1)
        elif controller.jogador2.nome != 'Bot':
            mostrar_mao(controller.jogador2)

        estado = novo_estado_mao()

        # Define quem começa a rodada (primeiro e segundo jogador)
        if hasattr(controller, 'proximo_primeiro') and controller.proximo_primeiro:
            primeiro, segundo = controller.proximo_primeiro, controller.jogador1 if controller.proximo_primeiro == controller.jogador2 else controller.jogador2
            controller.proximo_primeiro = None
        else:
            primeiro, segundo = controller.jogador1, controller.jogador2

        mao_encerrada = False
        # Loop das rodadas da mão (até 3 rodadas)
        for rodada in range(1, 4):
            if controller.mao_decidida():
                break
            mostrar_mensagem(f'\nRodada {rodada}')

            # Permite pedir truco novamente se a aposta estiver entre 2 e 3
            if 1 < controller.pontos_truco < 4:
                estado['pode_truco'] = True

            carta_idx = None
            # Turno do jogador da vez (humano ou bot)
            if primeiro == controller.jogador1:
                carta_idx, estado, mao_encerrada = turno_jogador_humano(
                    primeiro, segundo, controller, estado, primeiro_da_partida, rodada)
            else:
                carta_idx, estado, mao_encerrada = turno_jogador_bot(
                    primeiro, segundo, controller, estado, primeiro_da_partida, rodada)
                if carta_idx is not None:
                    mostrar_mensagem(f'{primeiro.nome} jogou: {primeiro.mao[carta_idx].numero} de {primeiro.mao[carta_idx].naipe}')
            if mao_encerrada:
                break
            # Jogada das cartas pelos jogadores
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
                    mostrar_mensagem(f'Você jogou: {segundo.mao[carta2].numero} de {segundo.mao[carta2].naipe}')
                else:
                    carta2 = segundo.jogarCarta(controller.cbr, controller)
            mostrar_mensagem(f'{primeiro.nome} jogou: {carta1.numero} de {carta1.naipe}')
            mostrar_mensagem(f'{segundo.nome} jogou: {carta2.numero} de {carta2.naipe}')

            # Processa o resultado da rodada
            ganhador_rodada, vencedor_mao = controller.jogar_rodada(carta1, carta2, primeiro, segundo)

            # Verifica se a mão foi decidida após a rodada
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

            # Alterna quem começa a próxima rodada, se necessário
            if ganhador_rodada == carta1:
                mostrar_mensagem(f'{primeiro.nome} venceu a rodada!')
            elif ganhador_rodada == carta2:
                mostrar_mensagem(f'{segundo.nome} venceu a rodada!')
                primeiro, segundo = segundo, primeiro
            elif ganhador_rodada == "Empate":
                mostrar_mensagem('Rodada empatada!')
            else:
                mostrar_mensagem('Rodada empatada!')

        if mao_encerrada:
            continue

        # Processa o fim da mão caso não tenha sido encerrada no loop
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

    # Exibe mensagem final do jogo
    mostrar_mensagem(f'\nFIM DE JOGO! Vencedor: {controller.determinar_vencedor().nome} com {controller.determinar_vencedor().pontos} pontos!')

if __name__ == '__main__':
    main()