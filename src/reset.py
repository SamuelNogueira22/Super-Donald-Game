import pyxel
from moeda import Moeda
from inimigo import Inimigo
from mola import Mola

def jogo_reset(self):
    """Reseta o estado do jogo para uma nova partida."""
    print("--- RESETANDO O JOGO ---") 

    # Reseta a posição do jogador e da câmera
    self.fase_x = 0
    self.fase_y = 0
    self.jogador_x = 25
    self.jogador_y = 224
    self.jogador_vy = 0.0
    self.esta_no_chao = False

    # Reseta as moedas e a condição de vitória
    self.moedas_coletadas = 0
    self.total_de_moedas = 0
    self.jogo_ganho = False
    self.tempo_vitoria = 0

    self.jogador_morto = False
    self.tempo_morte = 0

    # Recria o dicionário de moedas do zero, restaurando todas elas onde estavam antes
    self.moedas_por_fase = {
        (0, 0): [ Moeda(100, 150) ],
        (1, 0): [ Moeda(50, 110) ],
        (2, 0): [ Moeda(145, 59) ],
        (3, 0): [ Moeda(140, 110) ],
        (4, 0): [ Moeda(115, 56) ],
        (5, 0): [ Moeda(150, 100) ],
        (6, 0): [ Moeda(120, 66) ],
        (7, 0): [ Moeda(140, 56) ],
        (1, 1): [ Moeda(160, 166) ],
        (2, 1): [ Moeda(90, 136) ],
        (3, 1): [ Moeda(150, 86) ],
        (4, 1): [ Moeda(130, 56) ],
        (5, 1): [ Moeda(120, 116) ],
        (6, 1): [ Moeda(140, 146) ],
        (7, 1): [ Moeda(160, 166) ],
    }

    self.inimigos_por_fase = {
        (0, 0): [ Inimigo(155, 158, "bomba") ],
        (2, 0): [ Inimigo(155, 128, "cogumelo_azul") ],
        (3, 0): [ Inimigo(155, 225, "cogumelo_vermelho") ],
        (5, 0): [ Inimigo(150, 225, "bomba") ],
        (6, 0): [ Inimigo(70, 225, "cogumelo_vermelho") ],
        (7, 0): [ Inimigo(70, 225, "cogumelo_azul") ],
        (1, 1): [ Inimigo(115, 215, "bomba") ],
        (3, 1): [ Inimigo(130, 160, "cogumelo_vermelho") ],
        (4, 1): [ Inimigo(100, 215, "cogumelo_azul") ],
        # (5, 1): [ Inimigo(100, 135, "bomba", raio_movimento=1) ],
        (6, 1): [ Inimigo(130, 200, "cogumelo_vermelho") ],
    }

    # Recalcula o total de moedas
    for lista in self.moedas_por_fase.values():
        self.total_de_moedas += len(lista)

    pyxel.playm(0, loop=True)

    self.molas_por_fase = {
        (7, 1): [ Mola(x=200, y=216) ]
    }