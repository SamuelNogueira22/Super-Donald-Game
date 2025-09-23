# Mario Adventures Game
# ''''''''Created by Samuel Nogueira''''''''

import pyxel

# Configurações
TILE_SIZE = 8       # cada tile tem 8 pixels
FASE_SIZE = 32      # sala tem 32 tiles de lado
FASE_PIXELS = FASE_SIZE * TILE_SIZE

class Moeda:
    def __init__(self, x, y):
        self.x = x  # Posição no MUNDO
        self.y = y  # Posição no MUNDO
        self.largura = 8
        self.altura = 8
        self.ativa = True # Para saber se ela deve ser desenhada e coletada

class Jogo:
    def __init__(self):
        # Inicialização do Pyxel
        
        pyxel.init(256, 256, title="Mario Adventures", fps=60)
        pyxel.load("../assets/jogo.pyxres")
        
        self.fase_x = 0
        self.fase_y = 0
        
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
        #Inicindo lista de Moedas
        self.moedas_coletadas = 0
        self.total_de_moedas = 0 # Um contador para o total
        self.jogo_ganho = False
        
        self.moedas_por_fase = {
        (0, 0): [ #Moeda 1
            Moeda(100, 150),
        ],
        
        (1, 0): [  #Moeda 2
            Moeda(50, 110),
        ],
        
        (2,0): [ #Moeda 3
            Moeda(145, 59)
        ],
        
        (3,0): [ #Moeda 4
            Moeda(140, 110)
        ],
        
        (4,0): [ #Moeda 5
            Moeda(115, 56)
        ],
        
        (5,0): [ #Moeda 6
            Moeda(150, 100)
        ],
        
        (6,0): [ #Moeda 7
            Moeda(120, 66)
        ],
        
        (7,0): [ #Moeda 8
            Moeda(140, 56)
        ],
        
        (1,1): [ #Moeda 9
            Moeda(160, 166)
        ],
        
        (2,1): [ #Moeda 10
            Moeda(90, 146)
        ],
        
        (3,1): [ #Moeda 11
            Moeda(140, 96)
        ],
        
        (4,1): [ #Moeda 12
            Moeda(130, 56)
        ],
        
        (5,1): [ #Moeda 13
            Moeda(120, 116)
        ],
        
        (6,1): [ #Moeda 14
            Moeda(140, 146)
        ],
        
        (7,1): [ #Moeda 15
            Moeda(160, 166)
        ]
    }

    # Conta o total de moedas no jogo para a condição de vitória
        for lista in self.moedas_por_fase.values():
            self.total_de_moedas += len(lista)

        self.tempo_vitoria = 0 #Variavel simpes pra controlar o tempo que a mensagem de vitoria aparece (5 segundos)        
        self.reset()
        
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
        if self.jogo_ganho:
        # Checa se já passaram 180 frames (3 segundos) desde a vitória
            if pyxel.frame_count > self.tempo_vitoria + 180:
                self.reset() # Reseta o jogo
            return # Trava todo o resto do update (jogador, física, etc.)
        
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
        
        if self.jogo_ganho:
            return
        
        fase_atual = (self.fase_x, self.fase_y)
        if fase_atual in self.moedas_por_fase:
            lista_moedas_da_fase = self.moedas_por_fase[fase_atual]

            for moeda in lista_moedas_da_fase:
                if moeda.ativa:
                # Colisão direta entre as coordenadas da tela
                    if (
                        self.jogador_x < moeda.x + moeda.largura and
                        self.jogador_x + self.jogador_largura > moeda.x and
                        self.jogador_y < moeda.y + moeda.altura and
                        self.jogador_y + self.jogador_altura > moeda.y
                    ):
                        moeda.ativa = False
                        self.moedas_coletadas += 1
                        pyxel.play(3, 8)

                        if self.moedas_coletadas >= self.total_de_moedas:
                            self.jogo_ganho = True
                            self.tempo_vitoria = pyxel.frame_count # Guarda o frame exato da vitória
                            #Para versão futura: Toca uma música de vitória por 3 segundos
                            # pyxel.playm(1, loop=False) 
                            return # Para o resto do update
                        
#----------------------------------------------------------------------------------------------------------------------------------------------------------
    #Lógica de deslocamento de fases (transição entre telas/tiles)
#----------------------------------------------------------------------------------------------------------------------------------------------------------
    def desenha_cenario(self):

    # ---- LÓGICA DE TRANSIÇÃO HORIZONTAL (EIXO X) ----
    # Quando o jogador sai pela direita, avança a fase X
        if self.jogador_x >= 256: 
            self.fase_x += 1
            self.jogador_x = 0  # Reposiciona o jogador na esquerda
        
    # Quando o jogador volta pela esquerda, retorna a fase X
        if self.jogador_x < 0 and self.fase_x > 0:
            self.fase_x -= 1
            self.jogador_x = 255 # Reposiciona o jogador na direita

    # ---- LÓGICA DE TRANSIÇÃO VERTICAL (EIXO Y) ----
    # Quando o jogador cai da tela, avança a fase Y
        if self.jogador_y >= 256: 
            self.fase_y += 1
            self.jogador_y = 0  # Reposiciona o jogador no topo da nova tela
        
    # (Opcional) Se precisar que o jogador volte para a tela de cima
        if self.jogador_y < 0 and self.fase_y > 0:
            self.fase_y -= 1
            self.jogador_y = 255 # Reposiciona o jogador na base da tela anterior

    # --- DESENHO DO CENÁRIO ---
        x = 0
        y = 0
        tilemap = 0
        largura = 256
        altura = 256
    
    # 'u' (deslocamento horizontal) é calculado pela fase_x
        u = self.fase_x * 256 
    
    # 'v' (deslocamento vertical) é calculado pela fase_y
        v = self.fase_y * 256
    
    # Desenha o cenário na tela usando as coordenadas 'u' e 'v' calculadas
        pyxel.bltm(x, y, tilemap, u, v, largura, altura)
        
    #----------------------------------------------------------------------------------------------------------------------------------------------------------
    #Lógica de reset: cumpriu os objetivos = reinicia a partida automaticamente
    #----------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def reset(self):
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
        self.tempo_vitoria = 0 #Variavel simpes pra controlar o tempo que a mensagem de vitoria aparece (5 segundos)

    # Recria o dicionário de moedas do zero, restaurando todas elas onde estavam antes
        self.moedas_por_fase = {
        (0, 0): [ #Moeda 1
            Moeda(100, 150),
        ],
        
        (1, 0): [  #Moeda 2
            Moeda(50, 110),
        ],
        
        (2,0): [ #Moeda 3
            Moeda(145, 59)
        ],
        
        (3,0): [ #Moeda 4
            Moeda(140, 110)
        ],
        
        (4,0): [ #Moeda 5
            Moeda(115, 56)
        ],
        
        (5,0): [ #Moeda 6
            Moeda(150, 100)
        ],
        
        (6,0): [ #Moeda 7
            Moeda(120, 66)
        ],
        
        (7,0): [ #Moeda 8
            Moeda(140, 56)
        ],
        
        (1,1): [ #Moeda 9
            Moeda(160, 166)
        ],
        
        (2,1): [ #Moeda 10
            Moeda(90, 136)
        ],
        
        (3,1): [ #Moeda 11
            Moeda(130, 96)
        ],
        
        (4,1): [ #Moeda 12
            Moeda(130, 56)
        ],
        
        (5,1): [ #Moeda 13
            Moeda(120, 116)
        ],
        
        (6,1): [ #Moeda 14
            Moeda(140, 146)
        ],
        
        (7,1): [ #Moeda 15
            Moeda(160, 166)
        ]
    }

    # Recalcula o total de moedas
        for lista in self.moedas_por_fase.values():
            self.total_de_moedas += len(lista)
        
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    #função de desenho: mapeia e insere jogador, moedas e mensagem de vitória na tela
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def draw(self):
        pyxel.cls(2) #Faz o background ser roxo

        self.desenha_cenario()
        
        fase_atual = (self.fase_x, self.fase_y)
        if fase_atual in self.moedas_por_fase:
            lista_moedas_da_fase = self.moedas_por_fase[fase_atual]

            for moeda in lista_moedas_da_fase:
                if moeda.ativa:
                    # Desenha a moeda diretamente em sua coordenada (x, y) na tela
                    pyxel.blt(moeda.x, moeda.y, 1, 32, 0, 16, 16, 3)

        
        pyxel.blt(int(self.jogador_x), int(self.jogador_y), 0, 8, 16, 16, 16, 2) #desenha o mário
        
        #Mensagem de Vitória
        if self.jogo_ganho:
            texto = "PARABÉNS, VOCE VENCEU!"
            x_texto = (pyxel.width - len(texto) * 4) / 2
            y_texto = pyxel.height / 2 - 4
            pyxel.rect(x_texto - 4, y_texto - 4, len(texto) * 4 + 8, 16, 0)
            pyxel.text(x_texto, y_texto, texto, 7)
            
        #Exibição do contador de moedas na tela do jogo
        texto_contador = f"{self.moedas_coletadas}/{self.total_de_moedas}"

        # Posição do texto no canto superior esquerdo da tela
        pos_x_texto = 5
        pos_y_texto = 5

        # Desenha uma "sombra" preta para o texto
        pyxel.text(pos_x_texto + 1, pos_y_texto + 1, texto_contador, 0)
        # Desenha o texto principal em branco
        pyxel.text(pos_x_texto, pos_y_texto, texto_contador, 7)

        # Calcula a posição do ícone da moeda, para que ele apareça logo depois do texto
        pos_x_icone = 25
        pos_y_icone = pos_y_texto - 7


        # Desenha o ícone da moeda com o tamanho de 16x16
        pyxel.blt(
            pos_x_icone,
            pos_y_icone,  # Posição Y ajustada para o ícone maior
            1,                
            32, 0,            
            16, 16,           # Largura e Altura de 16x16
            3)                 # Cor transparente (Limpa o fundo verde do sprite)
        
            
# Inicia o jogo
Jogo()
