import pyxel

class Moeda:
    def __init__(self, x, y):
        self.x = x  # Posição no MUNDO
        self.y = y  # Posição no MUNDO
        self.largura = 8
        self.altura = 8
        self.ativa = True # Para saber se ela deve ser desenhada e coletada
