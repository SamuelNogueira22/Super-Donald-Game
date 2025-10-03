# Mario Adventures Game
# ''''''''Created by Samuel Nogueira''''''''

import pyxel

#Estados de Cena
Scene_title = 0
Scene_play = 1
Scene_tutorial = 2
Scene_credits = 3

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
    
    
class Jogo:
    def __init__(self):
        # Inicialização do Pyxel
        
        pyxel.init(256, 256, title="Mario Adventures", fps=60)
        pyxel.load("../assets/jogo.pyxres")
        
        #Aqui é possivel carregar a partitura da trilha sonora do mario original em formatio MML
        parte1_mml = "T100>e16e8e8c16e8g4<g4>c8.<g8.e8.a8b8a+16a8g16.>e16g16.a8f16g8e8c16d16<b8.>c8.<g8.e8.a8b8a+16a8g16.>e16g16.a8f16g8e8c16d16<b4&b16>g16f+16f16d+8e8<g+16a16>c8<a16>c16d8.g16f+16f16d+8e8>c8c16c4.<g16f+16f16d+8e8<g+16a16>c8<a16>c16d8.d+8.d8.c2&c8g16f+16f16d+8e8<g+16a16>c8<a16>c16d8.g16f+16f16d+8e8>c8c16c4.<g16f+16f16d+8e8<g+16a16>c8<a16>c16d8.d+8.d8.c2"
        parte2_mml = "<d16d8d8d16d8g4<g4>g8.e8.c8.f8g8f+16f8c16.>c16e16.f8d16e8c8<a16b16g8.g8.e8.c8.f8g8f+16f8c16.>c16e16.f8d16e8c8<a16b16g8.c8.g8.>c8<f8.>c16c16c16<f8c8.e8.g16>c4.&c16<g8c8.g8.>c8<f8.>c16c16c16<f8c8g+8.a+8.>c8.<g16g8c8c8.g8.>c8<f8.>c16c16c16<f8c8.g8.g16>c4.&c16<g8c8.g8.>c8<f8.>c16c16c16<f8c8g+8.a+8.>c8."

        # Pyxel tem limitação de tamanho para cargera MML, por isso dividi em dois
        pyxel.sounds[0].mml(parte1_mml)
        pyxel.sounds[1].mml(parte2_mml)

        # Cria a MÚSICA 0, que toca o SOM 0 e DEPOIS o SOM 1 em sequência
        pyxel.musics[0].set([0, 1], [], [], [])

        # Toca a música
        pyxel.playm(0, loop=True)
        
        #Efeitos sonoros
        som_moeda_mml = "t60 v12 o5 l16 b->e"
        som_vitoria_mml = "t120 v12 o5 l16 gg>c<b-ag>c<b-agf4"
        som_morte_mml = "t120 v12 o5 l8 c>g<f+fe-e<b-4"
        self.fase_x = 0
        self.fase_y = 0
        
        pyxel.sounds[8].mml(som_moeda_mml)    # Som da Moeda no espaço 8
        pyxel.sounds[9].mml(som_vitoria_mml)   # Som da Vitória no espaço 9
        pyxel.sounds[10].mml(som_morte_mml)   # Som da Morte no espaço 10
        
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
        
        self.scene = Scene_title
        #Menu
        
        self.menu_options = ["Jogar", "Tutorial", "Creditos", "Sair"]
        self.menu_idx = 0
        self.enter_hold = 0
        
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
        
        '''''''''''''''Tela de Menu'''''''''''''''''
        if self.scene == Scene_title:
            #Setas para navegar o menu e enter pra confirmar
            if pyxel.btnp(pyxel.KEY_UP):
                self.menu_idx = (self.menu_idx - 1) % len(self.menu_options)
            
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.menu_idx = (self.menu_idx + 1) % len(self.menu_options)
                    
            if pyxel.btnp(pyxel.KEY_RETURN):
                opt = self.menu_options[self.menu_idx]
                if opt == "Jogar":
                    self.scene = Scene_play
                    pyxel.playm(0, loop=True)
                elif opt == "Tutorial":
                    self.scene = Scene_tutorial
                elif opt == "Creditos":
                    self.scene = Scene_credits
                elif opt == "Sair":
                    pyxel.quit()
            return

            # Tutorial/Creditos: Enter volta ao menu
        if self.scene in (Scene_tutorial, Scene_credits):
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.scene = Scene_title
            return
        
        '''''''''''''''Tela de Jogo'''''''''''''''''
        if self.jogo_ganho:
        # Checa se já passaram 180 frames (3 segundos) desde a vitória
            if pyxel.frame_count > self.tempo_vitoria + 180:
                pyxel.stop() #Para a música de fundo
                pyxel.play(0, 9) #Toca o som de vitória
                self.reset() # Reseta o jogo
                return
        if self.jogador_morto:
            if pyxel.frame_count > self.tempo_morte + 120:
                pyxel.stop() #Para a música de fundo
                pyxel.play(0, 10) #Toca o som de morte 
                self.reset()
            return # Trava todo o resto do update (jogador, física, etc.)
        
        fase_atual = (self.fase_x, self.fase_y)
        inimigos_nesta_fase = self.inimigos_por_fase.get(fase_atual, [])
        
        for inimigo in inimigos_nesta_fase:
            inimigo.update()
        
        # Checa colisão
            jx, jy = self.jogador_x, self.jogador_y
            if (jx < inimigo.x + inimigo.largura and
                jx + self.jogador_largura > inimigo.x and
                jy < inimigo.y + inimigo.altura and
                jy + self.jogador_altura > inimigo.y):
                self.jogador_morto = True
                self.tempo_morte = pyxel.frame_count
                return
        
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
                        pyxel.play(1, 8) # Toca o som da moeda

                        if self.moedas_coletadas >= self.total_de_moedas:
                            self.jogo_ganho = True
                            self.tempo_vitoria = pyxel.frame_count # Guarda o frame exato da vitória 
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

        self.jogador_morto = False
        self.tempo_morte = 0
        
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
            Moeda(150, 86)
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
        
        self.inimigos_por_fase = {
        (0, 0): [ Inimigo(155, 158, "bomba") ],
        (2, 0): [ Inimigo(155, 128, "cogumelo_azul") ],
        (3, 0): [ Inimigo(155, 225, "cogumelo_vermelho") ],
        (5, 0): [ Inimigo(150, 225, "bomba") ],
        (6, 0): [ Inimigo(70, 225, "cogumelo_vermelho") ],
        (7, 0): [ Inimigo(70, 225, "cogumelo_azul") ],
        (1, 1): [ Inimigo(130, 215, "bomba") ],
        (3, 1): [ Inimigo(130, 160, "cogumelo_vermelho") ],
        (4, 1): [ Inimigo(100, 215, "cogumelo_azul") ],
        (5, 1): [ Inimigo(100, 135, "bomba", raio_movimento=1)],
        (6, 1): [ Inimigo(130, 200, "cogumelo_vermelho") ],
        
    }

    # Recalcula o total de moedas
        for lista in self.moedas_por_fase.values():
            self.total_de_moedas += len(lista)
        pyxel.playm(0, loop=True)
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    #função de desenho: mapeia e insere jogador, moedas e mensagem de vitória na tela
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def draw(self):
        if self.scene == Scene_title:
            #Tela de Menu Simples
            pyxel.cls(0)
            titulo = "MARIO ADVENTURES"
            hint = "Pressione ENTER para Jogar"
            subt = "by Samuel Nogueira"
            dica = "Setas: navegar | Enter: confirmar"
            pyxel.text((pyxel.width - len(titulo)*4)//2, 90, titulo, 7)
            pyxel.text((pyxel.width - len(subt)*4)//2, 105, subt, 6)

            # Opções do menu (com destaque)
            y0 = 130
            for i, opt in enumerate(self.menu_options):
                sel = (i == self.menu_idx)
                txt = f"> {opt} <" if sel else f"  {opt}  "
                cor = 10 if sel else 7
                pyxel.text((pyxel.width - len(txt)*4)//2, y0 + i*10, txt, cor)

            pyxel.text((pyxel.width - len(dica)*4)//2, 210, dica, 5)
            return
        
        if self.scene == Scene_tutorial:
            pyxel.cls(1)
            linhas = [
                "TUTORIAL",
                "",
                "- Setas: mover",
                "- Espaco/Seta Cima: pular",
                "- Colete todas as moedas",
                "- Evite os inimigos",
                "",
                "ENTER para voltar",
            ]
            for i, ln in enumerate(linhas):
                pyxel.text((pyxel.width - len(ln)*4)//2, 60 + i*12, ln, 7 if i==0 else 6)
            return

        if self.scene == Scene_credits:
            pyxel.cls(1)
            linhas = [
                "CREDITOS",
                "",
                "Codigo e Level Design:",
                "Samuel Nogueira",
                "",
                "Feito com Pyxel",
                "",
                "Jogo feito com propositos educacionais,",
                " quaisquer semelhancas com a realidade sao mera coincidencia",
                "",
                "ENTER para voltar",
            ]
            for i, ln in enumerate(linhas):
                pyxel.text((pyxel.width - len(ln)*4)//2, 60 + i*12, ln, 7 if i==0 else 6)
            return
        
        pyxel.cls(2) #Faz o background ser roxo

        self.desenha_cenario()
        
        fase_atual = (self.fase_x, self.fase_y)
        if fase_atual in self.moedas_por_fase:
            lista_moedas_da_fase = self.moedas_por_fase[fase_atual]

            for moeda in lista_moedas_da_fase:
                if moeda.ativa:
                    # Desenha a moeda diretamente em sua coordenada (x, y) na tela
                    pyxel.blt(moeda.x, moeda.y, 1, 32, 0, 16, 16, 3)

        
        if not self.jogador_morto:
            pyxel.blt(int(self.jogador_x), int(self.jogador_y), 0, 8, 16, 16, 16, 2) # Desenha o jogador
        
        #Mensagem de Vitória
        if self.jogo_ganho:
            texto = "PARABENS, VOCE VENCEU!"
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
        
        camera_x = self.fase_x * 256
        camera_y = self.fase_y * 256
        fase_atual = (self.fase_x, self.fase_y)
        for inimigo in self.inimigos_por_fase.get(fase_atual, []):
            inimigo.draw(camera_x, camera_y)
        
        
        if self.jogador_morto:
            texto = "VOCE PERDEU!"
            x_texto = (pyxel.width - len(texto) * 4) / 2
            y_texto = pyxel.height / 2 - 4
            pyxel.rect(x_texto - 4, y_texto - 4, len(texto) * 4 + 8, 16, 0)
            pyxel.text(x_texto, y_texto, texto, 8)
            
# Inicia o jogo
Jogo()
