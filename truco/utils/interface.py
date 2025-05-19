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
