import pyxel

# Placeholders para as constantes de cena (serão sobrescritas por jogo.py)
# Evita erro de isn't defined

Scene_title = None
Scene_play = None
Scene_tutorial = None
Scene_credits = None
Scene_pause = None


def jogo_update(self):
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
    
    # ----------  PAUSE ----------
    if self.scene == Scene_play and pyxel.btnp(pyxel.KEY_P):
        self.scene = Scene_pause
        self.pause_idx = 0
        return  # não avança a lógica neste frame

    if self.scene == Scene_pause:
        # Alterna seleção (só 2 opções) com seta cima/baixo
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_DOWN):
            self.pause_idx = 1 - self.pause_idx
        # P retoma rápido
        if pyxel.btnp(pyxel.KEY_P):
            self.scene = Scene_play
            return
        # Enter confirma
        if pyxel.btnp(pyxel.KEY_RETURN):
            opt = self.pause_options[self.pause_idx]
            if opt == "Continuar":
                self.scene = Scene_play
            else:  # "Menu"
                self.reset()
                self.scene = Scene_title
            return
        return  # congelado enquanto pausado
    
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
        if self.fase_y == 0 and self.colisao_vertical_pixels(int(self.jogador_y - 1)):
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
    fase_atual = (self.fase_x, self.fase_y)
    jogador_mundo_x = self.jogador_x + (self.fase_x * 256)
    jogador_mundo_y = self.jogador_y + (self.fase_y * 256)
    
    for mola in self.molas_por_fase.get(fase_atual, []):
        # Converte posição da mola (local à fase) para coordenadas do MUNDO
        mola_mundo_x = mola.x + (self.fase_x * 256)
        mola_mundo_y = mola.y + (self.fase_y * 256)

        # Checa se o jogador está caindo sobre a mola (colisão AABB simplificada)
        if (self.jogador_vy >= 0 and
            jogador_mundo_x + self.jogador_largura > mola_mundo_x and
            jogador_mundo_x < mola_mundo_x + mola.largura and
            jogador_mundo_y + self.jogador_altura > mola_mundo_y and
            jogador_mundo_y + self.jogador_altura < mola_mundo_y + 8):  # Tolerância para "pisar"

            # Dá um super pulo!
            self.jogador_vy = self.jump_force * 2.5  # Ajuste o '2.5' para mais ou menos altura
            self.esta_no_chao = False
            pyxel.play(3, 8)  # Som de "boing" (canal 3, som no slot 8)
            break