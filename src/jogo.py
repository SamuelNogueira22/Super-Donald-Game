#Duck Adventures Game
#''''''''Created by Samuel Nogueira''''''''

import pyxel

class Jogo:
    def __init__(self):
        # Tamanho e título do jogo
        pyxel.init(256, 256, title="Duck Adventures", fps=60)

        # Aqui eu carrego as imagens que criei pelo pyxel editor na pasta /assets
        pyxel.load("../assets/jogo.pyxres")

        # Posição inicial do jogador
        self.jogador_x = 25
        self.jogador_y = 235

        # Variaveis para a física do jogo, se jogador não esta no chão, ele vai ser puxado pra baixo
        self.jogador_vy = 0  # Velocidade vertical (vy)
        self.esta_no_chao = False

        pyxel.run(self.update, self.draw)

    def update(self):
        # --- Configurações de movimentos ---
        velocidade_h = 2
        if pyxel.btn(pyxel.KEY_LEFT) and self.jogador_x > 0:
            self.jogador_x -= velocidade_h
        if pyxel.btn(pyxel.KEY_RIGHT) and self.jogador_x < pyxel.width - 16:
            self.jogador_x += velocidade_h

        #Aplicar a gravidade constantemente
        self.jogador_vy += 0.5

        #Se o jogador está no chão e clica em espaço, ele da o pulo
        if pyxel.btnp(pyxel.KEY_SPACE) and self.esta_no_chao:
            self.jogador_vy = -10  # Força do pulo grande

        #Se o jogador está no chão e clicar seta pra cima, da um pequeno impulso
        if pyxel.btnp(pyxel.KEY_UP) and self.esta_no_chao:
            self.jogador_vy = -5   # Força do pulo pequeno

        #Seta pra baixo pra descidas
        if pyxel.btn(pyxel.KEY_DOWN):
            self.jogador_vy += 0.8 # Aumenta a velocidade de queda

        self.jogador_y += self.jogador_vy

        #    Define a "linha" do chão em y=230.
        if self.jogador_y > 230:
            self.jogador_y = 230
            self.jogador_vy = 0
            self.esta_no_chao = True
        else:
            self.esta_no_chao = False

    def draw(self):
        pyxel.cls(12)#Define cor de Fundo azul
        pyxel.bltm(0, 245, 0, 0, 0, 256, 256)#É o que pega meus desenhos do Painel de edição do pyxel
        pyxel.blt(self.jogador_x, self.jogador_y, 0, 0, 40, 16, 24, 0)#Pega o personagem do painel do pyxel

# Inicia o jogo
Jogo()