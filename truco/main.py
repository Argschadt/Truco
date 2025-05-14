from truco.core.game_controller import GameController

def main():
    print('Bem-vindo ao Truco Gaúcho!')
    nome1 = 'Heitor'
    nome2 = 'Bot'
    controller = GameController(nome1, nome2, bot=True)
    controller.reiniciar_mao()
    while not controller.fim_de_jogo():
        print(f'\nMão nova! Placar: {controller.jogador1.nome} {controller.jogador1.pontos} x {controller.jogador2.pontos} {controller.jogador2.nome}')
        controller.reiniciar_mao()
        while controller.rodada_atual <= 3:
            print(f'\nRodada {controller.rodada_atual}')
            controller.jogador1.mostrarMao()
            carta_idx = int(input(f'{controller.jogador1.nome}, escolha a carta (0, 1 ou 2): '))
            carta1 = controller.jogador1.jogarCarta(carta_idx)
            carta2 = controller.jogador2.jogarCarta(controller.cbr)
            print(f'{controller.jogador1.nome} jogou: {carta1.numero} de {carta1.naipe}')
            print(f'{controller.jogador2.nome} jogou: {carta2.numero} de {carta2.naipe}')
            ganhador = controller.jogar_rodada(carta1, carta2)
            if ganhador == controller.jogador1:
                print(f'{controller.jogador1.nome} venceu a rodada!')
            elif ganhador == controller.jogador2:
                print(f'{controller.jogador2.nome} venceu a rodada!')
            else:
                print('Rodada empatada!')
        vencedor_mao = controller.processar_fim_mao()
        if vencedor_mao:
            print(f'\n{vencedor_mao.nome} venceu a mão e ganhou {controller.pontos_truco} ponto(s)!')
        else:
            print('\nA mão terminou empatada!')
        controller.mostrar_estado()
    print(f'\nFIM DE JOGO! Vencedor: {controller.vencedor().nome}')

if __name__ == '__main__':
    main()