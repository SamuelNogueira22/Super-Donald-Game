import pyxel

class Inimigo:
    def __init__(self, x, y, tipo, raio_movimento=20):
        self.x_inicial = x
        self.y = y
        self.x = x
        self.largura = 16
        self.altura = 16
        self.tipo = tipo
        self.raio_movimento = raio_movimento
        self.velocidade_movimento = 1.5
        
        self.banco_imagem = 1
        if self.tipo == "cogumelo_vermelho": self.u, self.v = (0, 16)
        elif self.tipo == "cogumelo_azul": self.u, self.v = (0, 32)
        elif self.tipo == "bomba": self.u, self.v = (16, 32)

    def update(self):
        if self.tipo == "bomba" or self.tipo == "cogumelo_azul" or self.tipo == "cogumelo_vermelho":
            self.x = self.x_inicial + pyxel.sin(pyxel.frame_count * self.velocidade_movimento) * self.raio_movimento

    def draw(self, camera_x, camera_y):
        # Calcula a posição correta para desenhar na tela

        pyxel.blt(int(self.x), int(self.y), self.banco_imagem, self.u, self.v, self.largura, self.altura, 3)   
    
    