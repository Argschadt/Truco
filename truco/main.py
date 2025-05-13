from baralho import Baralho
from carta import Carta
from jogador import Jogador
from jogo import Jogo
from cbr import Cbr
from cbr_updated import CbrUpdated
import random
import os

def reiniciarJogo():
    jogador1.resetar()
    jogador2.resetar()
    baralho.resetarBaralho()
    baralho.criarBaralho()
    baralho.embaralhar()
    jogador1.criarMao(baralho)
    jogador2.criarMao(baralho)
    jogo.resetarTrucoPontos()

def limpar():
    os.system("cls")

def border_msg(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    lines = msg.split('\n')
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print(box)

def pedirTruco():
    if(jogador1.pediuTruco is not True and jogador2.avaliarTruco(cbr)):
        jogador1.pediuTruco = True
        return True
    elif (jogador1.pediuTruco is True):
        print('Jogador pediu truco e o pedido foi aceito, escolha outra carta!')
    else:
        print('Jogador negou o truco!')
        return False

def aumentarTruco(quemPediu):
    if(quemPediu == jogador1):
        if(jogador2.pediuTruco == True):
            opcao = jogador2.avaliarAumentarTruco()
            
            if(opcao == 0):
                return
            
            elif(opcao == 1):
                return
            
            elif(opcao == 2):
                return
            
            return jogador2.avaliarTruco(cbr)
    elif (jogador1.pediuTruco == True):
        opcao = -1
        while(opcao < 0 or opcao > 2):
            print(f'[0] Aceitar\n[1] Fugir\n[2] Aumentar')
            opcao = int(input(f"\n{jogador2.nome} Qual opção você deseja? "))
            
            if(opcao == 0):
                return
                
            elif(opcao == 1):
                return
                
            elif(opcao == 2):
                return

def chamarJogadasBot():
    carta_jogador_02 = jogador2.jogarCarta(cbr)
    print(f">> {jogador2.nome} jogou a carta: ")
    carta_jogador_02.printarCarta()
    carta2 = Carta(carta_jogador_02.retornarNumero(), carta_jogador_02.retornarNaipe())

    return carta2

def sortear_primeiro_jogador(jogador1, jogador2):
    """Sorteia quem será o primeiro jogador da rodada inicial e ajusta os atributos."""
    jogadores = ["jogador1", "jogador2"]
    sorteado = random.choice(jogadores)
    if sorteado == "jogador1":
        jogador1.primeiro = True
        jogador1.ultimo = False
        jogador2.primeiro = False
        jogador2.ultimo = True
        print(f"Primeiro a jogar: {jogador1.nome}\n")
    elif sorteado == "jogador2":
        jogador2.primeiro = True
        jogador2.ultimo = False
        jogador1.primeiro = False
        jogador1.ultimo = True
        print(f"Primeiro a jogar: {jogador2.nome}\n")

def jogar_rodada(jogo, jogador1, jogador2, cbr, pontos_truco):
    carta_escolhida = 6
    carta1 = None
    carta2 = None
    # Escolha da carta se JOGADOR for o primeiro
    if jogador1.primeiro:
        while (carta_escolhida > len(jogador1.checaMao()) or int(carta_escolhida) <= 1):
            print(f"\n<< {jogador1.nome} - Jogador 1 >>")
            jogador1.mostrarOpcoes()
            carta_escolhida = int(input(f"\n{jogador1.nome} Qual carta você quer jogar? "))
            if (carta_escolhida < len(jogador1.checaMao()) and int(carta_escolhida) >= 0):
                carta_jogador_01 = jogador1.jogarCarta(carta_escolhida)
                pontos_truco = jogo.retornaTrucoPontos()
                break
            else:
                print('Selecione um valor válido!')
        carta1 = Carta(carta_jogador_01.retornarNumero(), carta_jogador_01.retornarNaipe())
        carta2 = chamarJogadasBot()
    # Escolha da carta se BOT for o primeiro
    elif jogador2.primeiro:
        carta2 = chamarJogadasBot()
        while (carta_escolhida > len(jogador1.checaMao()) or int(carta_escolhida) <= 1):
            print(f"\n<< {jogador1.nome} - Jogador 1 >>")
            jogador1.mostrarOpcoes()
            carta_escolhida = int(input(f"\n{jogador1.nome} Qual carta você quer jogar? "))
            if (carta_escolhida < len(jogador1.checaMao()) and int(carta_escolhida) >= 0):
                carta_jogador_01 = jogador1.jogarCarta(carta_escolhida)
                pontos_truco = jogo.retornaTrucoPontos()
                break
            else:
                print('Selecione um valor válido!')
        carta1 = Carta(carta_jogador_01.retornarNumero(), carta_jogador_01.retornarNaipe())
    ganhador = jogo.verificarGanhador(carta1, carta2)
    jogo.quemJogaPrimeiro(jogador1, jogador2, carta1, carta2, ganhador)
    jogo.adicionarPonto(jogador1, jogador2, carta1, carta2, ganhador)
    # Atualiza histórico
    if ganhador == carta1:
        jogo.historico_rodadas.append(1)
    elif ganhador == carta2:
        jogo.historico_rodadas.append(2)
    else:
        jogo.historico_rodadas.append(0)
    return pontos_truco

def processar_fim_mao(jogo, jogador1, jogador2, pontos_truco):
    h = jogo.historico_rodadas
    if len(h) == 3:
        if h[0] == 0:
            if h[1] == 1:
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
            elif h[1] == 2:
                jogador2.adicionarRodada(pontos_truco)
                print(f"\n{jogador2.nome} ganhou a rodada")
            else:
                if h[2] == 1:
                    jogador1.adicionarRodada(pontos_truco)
                    print(f"\n{jogador1.nome} ganhou a rodada")
                elif h[2] == 2:
                    jogador2.adicionarRodada(pontos_truco)
                    print(f"\n{jogador2.nome} ganhou a rodada")
                else:
                    print("\nA mão terminou empatada! Nenhum jogador recebe ponto de rodada.")
        elif h[1] == 0:
            if h[2] == 1:
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
            elif h[2] == 2:
                jogador2.adicionarRodada(pontos_truco)
                print(f"\n{jogador2.nome} ganhou a rodada")
            else:
                print("\nA mão terminou empatada! Nenhum jogador recebe ponto de rodada.")
        else:
            if jogador1.pontos > jogador2.pontos:
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
            elif jogador2.pontos > jogador1.pontos:
                jogador2.adicionarRodada(pontos_truco)
                print(f"\n{jogador2.nome} ganhou a rodada")
            else:
                print("\nA mão terminou empatada! Nenhum jogador recebe ponto de rodada.")
        reiniciarJogo()
        jogo.resetarHistoricoRodadas()
        border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.rodadas} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.rodadas} Pontos Acumulados")

if __name__ == '__main__':
    jogo = Jogo()
    baralho = Baralho()
    baralho.embaralhar() # Voltar a embaralhar para o jogo funcionarnormalmente.
    baralho.embaralhar() # Voltar a embaralhar para o jogo funcionarnormalmente.
    cbr = CbrUpdated()

    truco_aceito = False
    truco_fugiu = False
    pontos_truco = 0
    carta1 = 0
    carta2 = 0
    ganhador = 0

    nome = str(input("Nome Jogador 1: "))
    jogador1 = jogo.criarJogador(nome, baralho)

    nome = str(input("Nome Jogador 2: "))
    jogador2 = jogo.criarBot(nome, baralho)
    
    #Sorteio pra ver quem joga na primeira rodada
    if jogador1.rodadas == 0 and jogador2.rodadas == 0:
        if jogador1.pontos == 0 and jogador2.pontos == 0:
            sortear_primeiro_jogador(jogador1, jogador2)

    while True:
        truco_fugiu = False
        ocultar_rodadas = False
        pontos_truco = jogar_rodada(jogo, jogador1, jogador2, cbr, pontos_truco)
        # Fim de mão: verifica se acabou as cartas
        if not(jogador1.checaMao()) and not(jogador2.checaMao()):
            ocultar_rodadas = True
            processar_fim_mao(jogo, jogador1, jogador2, pontos_truco)
        
        # Fim de rodada: vitória normal
        if (jogador1.pontos == 2 or jogador2.pontos == 2):
            ocultar_rodadas = True
            if jogador1.pontos == 2:
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
                reiniciarJogo()
            elif jogador2.pontos == 2:
                jogador2.adicionarRodada(pontos_truco)
                print(f"\n{jogador2.nome} ganhou a rodada")
                reiniciarJogo()
            print(jogador1.rodadas)
            border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.rodadas} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.rodadas} Pontos Acumulados")
        
        # Fim de rodada: empate de mão (cada um venceu uma rodada e a terceira empatou)
        elif (not(jogador1.checaMao()) and not(jogador2.checaMao()) and jogador1.pontos == 1 and jogador2.pontos == 1):
            ocultar_rodadas = True
            print("\nA mão terminou empatada! Nenhum jogador recebe ponto de rodada.")
            reiniciarJogo()
            border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.rodadas} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.rodadas} Pontos Acumulados")
        
        # Fim de rodada: fuga ou fim de cartas (vitória por pontos)
        elif (not(jogador1.checaMao()) and not(jogador2.checaMao()) or truco_fugiu is True):
            ocultar_rodadas = True
            if truco_fugiu is True:
                print(f'pontos truco:: {pontos_truco} | {jogo.retornaTrucoPontos()}')
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
                reiniciarJogo()
            elif jogador1.pontos > jogador2.pontos:
                jogador1.adicionarRodada(pontos_truco)
                print(f"\n{jogador1.nome} ganhou a rodada")
                reiniciarJogo()
            elif jogador2.pontos > jogador1.pontos:
                jogador2.adicionarRodada(pontos_truco)
                print(f"\n{jogador2.nome} ganhou a rodada")
                reiniciarJogo()
            border_msg(f"Jogador 1 - {jogador1.nome}: {jogador1.rodadas} Pontos Acumulados\nJogador 2 - {jogador2.nome}: {jogador2.rodadas} Pontos Acumulados")

        if (ocultar_rodadas is False):
            border_msg(f"Jogador 1 - {jogador1.nome}: Venceu {jogador1.pontos} Rodada(s)\nJogador 2 - {jogador2.nome}: Venceu {jogador2.pontos} Rodada(s)")

        jogo.quemIniciaRodada(jogador1, jogador2)

        if jogador1.rodadas >= 12:
            print(f"\n{jogador1.nome} ganhou o jogo")
            break

        elif jogador2.rodadas >= 12:
            print(f"\n{jogador2.nome} ganhou o jogo")
            break
'''
To do:
- Implementar classificação das cartas para o bot;
- Implementar envido;
- Implementar real envido;
- Implementar falta envido;
- Implementar negação do envido
- Checar funcionamento do Truco
'''