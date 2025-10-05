import pyxel

class Mola:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largura = 16
        self.altura = 16
        
        # Coordenadas do seu sprite da mola (como você informou)
        self.banco_imagem = 1 # Assumindo que está no banco de imagens 1
        self.u, self.v = (0, 48)
    def draw(self):
        # A mola é armazenada por fase com coordenadas LOCAIS (0..255),
        # então desenhamos diretamente na tela sem aplicar offset de câmera.
        pyxel.blt(int(self.x), int(self.y), self.banco_imagem, self.u, self.v, self.largura, self.altura, 3)