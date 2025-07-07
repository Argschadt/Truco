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

## Estrutura do Projeto

```
Truco/
│
├── truco/
│   ├── main.py                # Ponto de entrada do jogo, executa o loop principal.
│   │
│   ├── core/                  # Núcleo da lógica do jogo.
│   │   ├── acoes.py           # Lida com ações especiais (Truco, Envido, Flor, etc).
│   │   ├── game_controller.py # Controlador principal, gerencia estados e jogadores.
│   │   ├── game_loop.py       # Gerencia o fluxo de cada rodada/mão.
│   │   ├── game_runner.py     # Executa o loop principal do jogo.
│   │   ├── jogo.py            # Criação de jogadores, bots e lógica de pontuação.
│   │   ├── rules.py           # Regras e hierarquia das cartas.
│   │   ├── turnos.py          # Gerencia turnos e prompts de ação.
│   │   └── utils.py           # Funções auxiliares para configuração e estados.
│   │
│   ├── bots/                  # Inteligência artificial e lógica dos bots.
│   │   ├── bot.py             # Classe principal do bot, tomada de decisão.
│   │   ├── cbr.py             # Bot baseado em Case-Based Reasoning (CBR) simples.
│   │   └── cbr_updated.py     # Versão avançada do CBR, usa cbrkit e bancos de dados.
│   │
│   ├── models/                # Modelos de dados do jogo.
│   │   ├── baralho.py         # Classe Baralho, cria e embaralha cartas.
│   │   ├── carta.py           # Classe Carta, representa cada carta e suas operações.
│   │   ├── jogador.py         # Classe Jogador, representa o jogador humano.
│   │   └── modelo_registro.py # Estrutura de dados para registrar o estado da mão.
│   │
│   ├── utils/                 # Utilitários e interface.
│   │   ├── interface.py       # Funções de entrada/saída no terminal.
│   │   ├── pontos.py          # Tabelas de valores das cartas, manilhas e envido.
│   │   └── functions.py       # (Vazio/reservado para utilitários futuros)
│   │
│   └── requirements.txt       # Dependências específicas do módulo.
│
├── dbtrucoimitacao_maos.csv                   # Base de dados de mãos para CBR.
├── dbtrucoimitacao_maos_cbrkit_jogadorMao_1.csv # Base de dados de mãos (jogador 1).
├── dbtrucoimitacao_maos_cbrkit_jogadorMao_2.csv # Base de dados de mãos (jogador 2).
├── modelo_registro.csv                        # Estrutura de registro de estados das mãos.
├── manual_truco.pdf                           # Manual de regras do Truco Gaúcho.
├── requirements.txt                           # Dependências globais do projeto.
├── README.md                                  # Documentação do projeto.
└── truco.cmd                                  # Script para rodar o jogo no Windows.
```

## Função dos Arquivos

- **truco/main.py**: Inicia o jogo, configura o controlador e executa o loop principal.
- **truco/core/**: Implementa toda a lógica do jogo, regras, controle de rodadas, ações e estados.
- **truco/bots/**: Implementa bots com inteligência artificial, incluindo lógica baseada em CBR e integração com bancos de dados de partidas.
- **truco/models/**: Define as entidades do jogo (cartas, baralho, jogadores, modelo de registro de jogadas).
- **truco/utils/**: Funções auxiliares, interface de usuário e tabelas de pontuação.
- **dbtrucoimitacao_maos*.csv**: Bases de dados para aprendizado e tomada de decisão dos bots.
- **modelo_registro.csv**: Estrutura de dados para registrar o estado de cada mão/jogada.
- **manual_truco.pdf**: Manual detalhado das regras do Truco Gaúcho.
- **requirements.txt**: Lista de dependências necessárias para rodar o projeto.
- **truco.cmd**: Script para facilitar a execução do jogo no Windows.

## Como Rodar o Programa

1. **Pré-requisitos:**
   - Ter o Python 3 instalado em sua máquina.
2. **Clonar o repositório ou baixar os arquivos:**
   ```
   git clone https://github.com/Argschadt/Truco
   cd Truco
   ```
3. **Instalar dependências:**
   ```
   pip install -r requirements.txt
   ```
4. **Executar o jogo:**
   No terminal, execute:
   ```
   python -m truco.main
   ```
5. **Siga as instruções exibidas no terminal para jogar.**
