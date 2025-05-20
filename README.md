# Truco Gaudério

 ### Jogo Truco em Python

- **Jogadores:** Pode ser jogado 1v1.
- **Número de cartas:** 40 (Não possui 8, 9, 10, 13).
- **Distribuição de cartas:** Cada jogador recebe três cartas.
- **Objetivo:** Fazer 12 pontos para ganhar.
- **Sequência das cartas mais fortes:** A♠, A♣, 7♠, 7♦, 3, 2, A♦♥, 12, 11, 10, 7♣♥, 6, 5, 4.
- **Naipes:** ♣Paus, ♥Copas, ♠Espadas, ♦Ouros.

 ### Definições (Truco Gaudério):

- **Mão:** Cada jogador recebe três cartas.
- **Truco:** A qualquer momento, um jogador pode pedir truco para aumentar a aposta da rodada de 1 para 2 pontos. O adversário pode aceitar, recusar (dando 1 ponto ao desafiante) ou pedir "Retruco" aumentando para 3 pontos e depois o adversário pode pedir "Vale-Quatro" passando para 4 pontos.
- **Flor:** Se um jogador tiver três cartas do mesmo naipe, pode pedir "Flor", que vale 3 pontos. O adversário pode aceitar, pedir "Contra-Flor" (6 pontos) ou recusar.
- **Rodadas:** Cada mão é disputada em até três rodadas. Quem vencer duas, leva os pontos da mão.
- **Empate:** Em caso de empate em uma rodada, vence quem ganhou a rodada anterior. Se empatar a primeira, a próxima rodada desempata.
- **Pontuação:** O jogo é disputado até 30 pontos.

---

## Sobre o Código

O projeto é composto por módulos Python que implementam as regras do Truco Gaudério. As principais partes do código incluem:

- **Baralho e Cartas:** Classes responsáveis por criar e embaralhar o baralho, além de distribuir as cartas para os jogadores.
- **Jogador:** Classe que representa cada jogador, armazenando suas cartas e pontos.
- **Lógica do Jogo:** Funções que controlam o fluxo do jogo, como distribuição de cartas, definição da vira, manilhas, rodadas e contagem de pontos.
- **Interação:** O jogo pode ser jogado via terminal, onde o usuário escolhe as cartas e faz pedidos de truco, seis, nove e doze.

O código é modularizado para facilitar a manutenção e entendimento das regras do jogo.

---

## Como Rodar o Programa

1. **Pré-requisitos:**  
   - Ter o Python 3 instalado em sua máquina.

2. **Clonar o repositório ou baixar os arquivos:**  
   ```
   git clone https://github.com/Argschadt/Truco
   cd Truco
   ```

3. **Executar o jogo:**  
   No terminal, execute:
   ```
   python -m truco.main
   ```

4. **Siga as instruções exibidas no terminal para jogar.**
