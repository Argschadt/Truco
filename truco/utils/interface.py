"""
Módulo de interface para entrada e saída do usuário no Truco Gaúcho.
Responsável por exibir prompts, mensagens e coletar entradas.
"""

def mostrar_mao(jogador):
    print(f"\nMão de {jogador.nome}:")
    for idx, carta in enumerate(jogador.mao):
        print(f"  [{idx}] {carta.numero} de {carta.naipe}")

def mostrar_estado(controller):
    print(f"\nPlacar: {controller.jogador1.nome} {controller.jogador1.pontos} x {controller.jogador2.pontos} {controller.jogador2.nome}")

def prompt_acao(prompt):
    return input(prompt).strip().lower()

def mostrar_mensagem(msg):
    print(msg)

def mostrar_resultado_envido(quem_pediu, quem_responde, pontos1, pontos2):
    print(f"{quem_pediu.nome}: {pontos1} pontos de envido | {quem_responde.nome}: {pontos2} pontos de envido")

def mostrar_resultado_flor(quem_pediu, quem_responde, pontos1, pontos2):
    print(f"{quem_pediu.nome}: {pontos1} pontos de Flor | {quem_responde.nome}: {pontos2} pontos de Flor")

def mostrar_vencedor_rodada(nome):
    print(f"{nome} venceu a rodada!")

def mostrar_empate_rodada():
    print('Rodada empatada!')

def mostrar_vencedor_mao(nome, pontos):
    print(f'\n{nome} venceu a mão e ganhou {pontos} ponto(s)!')

def mostrar_mao_terminou_empatada():
    print('\nA mão terminou empatada!')

def mostrar_pedido_flor(quem_pediu):
    print(f"{quem_pediu.nome} pediu Flor!")

def mostrar_sem_flor(quem_responde, quem_pediu):
    print(f"{quem_responde.nome} não tem Flor! {quem_pediu.nome} ganha 3 pontos.")

def mostrar_pedido_contra_flor(quem_pediu, quem_responde):
    print(f"{quem_responde.nome} pediu Contra-Flor!")

def mostrar_pedido_contra_flor_ao_resto(quem_pediu, quem_responde):
    print(f"{quem_responde.nome} pediu Contra-Flor ao Resto!")

def mostrar_boa(nome):
    print(f"{nome}: É BOA!")

def prompt_aceite_contra_flor(nome):
    return input(f"{nome}, seu oponente pediu Contra-Flor (vale 6 pontos). Aceita [s], recusa [n] ou pede Contra-Flor ao Resto [r]? ").strip().lower()

def prompt_aceite_contra_flor_ao_resto(nome):
    return input(f"{nome}, seu oponente pediu Contra-Flor ao Resto (vale resto). Aceita? [s/n]").strip().lower()

def prompt_acao_flor(nome):
    return input(f"{nome}, seu oponente pediu Flor! Você também tem Flor. Deseja pedir Contra-Flor [c], Contra-Flor ao Resto [r] ou desistir da flor [d]? ").strip().lower()

def mostrar_desistiu_flor(nome):
    print(f"{nome} desistiu da flor!")

def mostrar_aceitou_contra_flor(nome):
    print(f"{nome} aceitou a Contra-Flor!")

def mostrar_aceitou_contra_flor_ao_resto(nome):
    print(f"{nome} aceitou a Contra-Flor ao Resto!")

def mostrar_recusou_contra_flor(nome, oponente):
    print(f"{nome} recusou a Contra-Flor! {oponente} ganha 3 pontos.")

def mostrar_recusou_contra_flor_ao_resto(nome, oponente):
    print(f"{nome} recusou a Contra-Flor ao Resto! {oponente} ganha 6 pontos.")

def mostrar_opcao_invalida(opcoes):
    print(f"Opção inválida! Digite uma das opções: {', '.join(opcoes)}.")
