# Mario Adventures Game
# ''''''''Created by Samuel Nogueira''''''''

import pyxel

# Configurações
TILE_SIZE = 8       # cada tile tem 8 pixels
FASE_SIZE = 32      # sala tem 32 tiles de lado
FASE_PIXELS = FASE_SIZE * TILE_SIZE

class Jogo:
    def __init__(self):
        # Inicialização do Pyxel
        
        pyxel.init(256, 256, title="Mario Adventures", fps=60)
        pyxel.load("../assets/jogo.pyxres")
        self.fase = 0

        # Posição e física
        
        self.jogador_x = 25
        self.jogador_y = 224
        self.jogador_vy = 0.0
        self.esta_no_chao = False

        # Tamanho e cor de plataforma
        self.cor_plataforma = 0  # Preto é a definição de solidez
        self.jogador_largura = 16
        self.jogador_altura = 16

        # Constantes de movimento
        self.jump_force = -10        # A força do pulo é negativa porque y cresce pra baixo aqui
        self.gravidade = 0.5          # Gravidade por frame
        self.velocidade_pulo = 0.8      # Extra quando segura ↓

        # Input helpers (para detecção de borda e buffer)
        self.jump_key_prev = False          # Estado da tecla no frame anterior
        self.jump_buffer_max = 6            # frames de "buffer" (p.ex. 6 frames = ~0.1s)
        self.jump_buffer_timer = 0

        # Coyote time (permite pular logo após sair do chão)
        self.coyote_time_max = 6            # frames de tolerância
        self.coyote_timer = 0

        #Câmera
        self.camera_x = 0
        self.camera_y = 0
        
        # Música
        pyxel.playm(0, loop=True)

        # Start
        pyxel.run(self.update, self.draw)

        #Definições de colisão:
    
    def safe_pget(self, x, y):
        xi = int(x)
        yi = int(y)
        if xi < 0 or yi < 0 or xi >= pyxel.width or yi >= pyxel.height:
            return None
        return pyxel.pget(xi, yi)

    def colisao_horizontal_pixels(self, px):
        """Retorna True se qualquer pixel na coluna 'px' que cruza a altura do jogador for sólido."""
        for y in range(int(self.jogador_y), int(self.jogador_y + self.jogador_altura)):
            if self.safe_pget(px, y) == self.cor_plataforma:
                return True
        return False

    def colisao_vertical_pixels(self, py):
        """Retorna True se qualquer pixel na linha 'py' que cruza a largura do jogador for sólido."""
        for x in range(int(self.jogador_x), int(self.jogador_x + self.jogador_largura)):
            if self.safe_pget(x, py) == self.cor_plataforma:
                return True
        return False

    # -----------------------
    # Correção de posição
    # -----------------------
    #Função pro jogador ficar sempre acima do bloco (na parte preta)
    def corrige_posicao_y(self, subindo: bool):
        
        max_steps = self.jogador_altura + 2

        if subindo:
            for _ in range(max_steps):
                if not self.colisao_vertical_pixels(int(self.jogador_y - 1)):
                    break
                self.jogador_y += 1
        else:
            for _ in range(max_steps):
                if not self.colisao_vertical_pixels(int(self.jogador_y + self.jogador_altura)):
                    break
                self.jogador_y -= 1

    
    def update(self):
        # --- Entrada: leitura de tecla de pulo (detecção de borda) ---
        jump_now = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP)
        # Detecta press (borda de subida). Isso não depende de btnp.
        if jump_now and not self.jump_key_prev:
            # Preenche o buffer: caso o player aperte pouco antes de pousar
            self.jump_buffer_timer = self.jump_buffer_max

        #Movimento horizontal
        velocidade_h = 2
        movimento_x = 0
        
        if pyxel.btn(pyxel.KEY_LEFT):
            movimento_x = -velocidade_h
        if pyxel.btn(pyxel.KEY_RIGHT):
            movimento_x = velocidade_h

        if movimento_x != 0:
            if movimento_x < 0:
                teste_x = int(self.jogador_x - 1)
            else:
                teste_x = int(self.jogador_x + self.jogador_largura)

            if self.colisao_horizontal_pixels(teste_x):
                movimento_x = 0

        self.jogador_x += movimento_x

        # ---gravidade ---
        self.jogador_vy += self.gravidade
        
        if pyxel.btn(pyxel.KEY_DOWN):
            self.jogador_vy += self.velocidade_pulo  # Acelera a descida se segurando ↓

        # --- Colisão vertical---
        if self.jogador_vy > 0:
            # Caindo: checa a linha logo abaixo dos pés
            
            if self.colisao_vertical_pixels(int(self.jogador_y + self.jogador_altura)):
                # Tocou o chão
                
                self.jogador_vy = 0
                self.esta_no_chao = True
                self.corrige_posicao_y(subindo=False)
                
            else:
                self.esta_no_chao = False

        elif self.jogador_vy < 0:
            # Subindo: checa a linha logo acima da cabeça
            if self.colisao_vertical_pixels(int(self.jogador_y - 1)):
                self.jogador_vy = 0
                self.corrige_posicao_y(subindo=True)

        # --- Atualiza timers de coyote e buffer com base no estado do chão ---
        if self.esta_no_chao:
            self.coyote_timer = self.coyote_time_max
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # Se houver buffer de pulo, tenta executar o pulo enquanto houver coyote time
        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            # Executa o pulo
            self.jogador_vy = self.jump_force
            self.esta_no_chao = False
            # limpa timers/buffer
            self.jump_buffer_timer = 0
            self.coyote_timer = 0

        # Aplica o movimento vertical final
        self.jogador_y += self.jogador_vy

        # Decrementa o buffer de pulo (se houver)
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # Atualiza o estado anterior da tecla de pulo
        self.jump_key_prev = jump_now
        

    def desenha_cenario(self):

        # Descobre a fase do jogador e ajusta a posição
        if self.jogador_x > 256: 
            self.fase  = self.fase + 1 # Aumenta a fase
            self.jogador_x = 0  # Volta o personagem para a esquerda da tela
            
        if self.jogador_x < 0 and self.fase > 0:
            self.fase -= 1
            self.jogador_x = 256
        x = 0
        y = 0
        tilemap = 0
        u = self.fase * 256 # Cada fase tem 256 de largura no tilemap
        v = 0
        largura = 256
        altura = 256


        pyxel.bltm(x,y,tilemap,u,v,largura,altura) #desenha cenário
        #print     (x,y,tilemap,u,v,largura,altura)
        #print(u)
        
    
    def draw(self):
        pyxel.cls(2) #Faz o background ser roxo

        self.desenha_cenario()
        
        pyxel.blt(int(self.jogador_x), int(self.jogador_y), 0, 8, 16, 16, 16, 2) #desenha o mário e atualiza ele com base na câmera

# Inicia o jogo
Jogo()
