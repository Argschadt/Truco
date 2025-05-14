import unittest
from truco.models.baralho import Baralho
from truco.bots.bot import Bot

class TestBot(unittest.TestCase):
    def setUp(self):
        self.baralho = Baralho()
        self.baralho.embaralhar()
        self.bot = Bot('BotTest')
        self.bot.criarMao(self.baralho)

    def test_criar_mao(self):
        self.assertEqual(len(self.bot.mao), 3)
        self.assertEqual(len(self.bot.indices), 3)
        self.assertIsInstance(self.bot.forcaMao, int)

    def test_pedir_truco(self):
        # Força a mão para garantir o teste
        self.bot.forcaMao = 45
        self.assertTrue(self.bot.pedir_truco())
        self.bot.forcaMao = 20
        self.assertFalse(self.bot.pedir_truco())

    def test_aceitar_truco(self):
        self.bot.forcaMao = 30
        self.assertTrue(self.bot.aceitar_truco(3))
        self.bot.forcaMao = 10
        self.assertFalse(self.bot.aceitar_truco(3))

    def test_pedir_envido(self):
        # Força duas cartas do mesmo naipe
        self.bot.mao[0].naipe = 'ESPADAS'
        self.bot.mao[1].naipe = 'ESPADAS'
        self.bot.mao[2].naipe = 'OUROS'
        self.assertTrue(self.bot.pedir_envido())
        self.bot.mao[1].naipe = 'COPAS'
        self.assertFalse(self.bot.pedir_envido())

    def test_aceitar_envido(self):
        # Força pontos de envido
        self.bot.calcular_pontos_envido = lambda: 27
        self.assertTrue(self.bot.aceitar_envido(2))
        self.bot.calcular_pontos_envido = lambda: 10
        self.assertFalse(self.bot.aceitar_envido(2))

    def test_pedir_flor(self):
        self.bot.flor = True
        self.assertTrue(self.bot.pedir_flor())
        self.bot.flor = False
        self.assertFalse(self.bot.pedir_flor())

    def test_aceitar_flor(self):
        self.assertTrue(self.bot.aceitar_flor())

    def test_decidir_correr_mao_de_onze(self):
        self.bot.forcaMao = 10
        self.assertTrue(self.bot.decidir_correr_mao_de_onze())
        self.bot.forcaMao = 30
        self.assertFalse(self.bot.decidir_correr_mao_de_onze())

    def test_resetar_estado_mao(self):
        self.bot.resetar_estado_mao()
        self.assertEqual(self.bot.mao, [])
        self.assertEqual(self.bot.maoRank, [])
        self.assertEqual(self.bot.indices, [])
        self.assertEqual(self.bot.pontuacaoCartas, [])
        self.assertEqual(self.bot.forcaMao, 0)
        self.assertFalse(self.bot.flor)
        self.assertFalse(self.bot.pediuTruco)
        self.assertEqual(self.bot.rodadas, 0)
        self.assertEqual(self.bot.invido, 0)

if __name__ == '__main__':
    unittest.main()
