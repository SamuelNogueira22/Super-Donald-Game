# Mario Adventures Game
# ''''''''Created by Samuel Nogueira''''''''

# imports internos

from moeda import Moeda
from inimigo import Inimigo
from mola import Mola
from levels import build_level_structs
from update import jogo_update
import update
from draw import jogo_draw
import draw
from reset import jogo_reset
import reset

# import da biblioteca

import pyxel

#Estados de Cena - Usados para apresentar telas do menu e jogo
Scene_title = 0
Scene_play = 1
Scene_tutorial = 2
Scene_credits = 3
Scene_pause = 4

# Tornar as constantes de cena disponíveis dentro do módulo update
import update
update.Scene_title = Scene_title
update.Scene_play = Scene_play
update.Scene_tutorial = Scene_tutorial
update.Scene_credits = Scene_credits
update.Scene_pause = Scene_pause

#Constantes para draw

draw.Scene_title = Scene_title
draw.Scene_play = Scene_play
draw.Scene_tutorial = Scene_tutorial
draw.Scene_credits = Scene_credits
draw.Scene_pause = Scene_pause

#Constantes para reset

reset.Scene_title = Scene_title
reset.Scene_play = Scene_play
reset.Scene_tutorial = Scene_tutorial
reset.Scene_credits = Scene_credits
reset.Scene_pause = Scene_pause

# Configurações
TILE_SIZE = 8       # cada tile tem 8 pixels
FASE_SIZE = 32      # sala tem 32 tiles de lado
FASE_PIXELS = FASE_SIZE * TILE_SIZE

    
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
        
        #Menu de Pausa
        
        self.pause_options = ["Continuar", "Menu"]
        self.pause_idx = 0
        
        # Inicializa moedas, inimigos e molas a partir do módulo levels
        self.moedas_por_fase, self.inimigos_por_fase, self.molas_por_fase = build_level_structs()

        # Conta o total de moedas no jogo para a condição de vitória
        self.total_de_moedas = sum(len(lista) for lista in self.moedas_por_fase.values())

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
        return jogo_update(self)
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
        
    # Se precisar que o jogador volte para a tela de cima
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
        return jogo_reset(self)
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    #função de desenho: mapeia e insere jogador, moedas e mensagem de vitória na tela
    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    
    def draw(self):
        return jogo_draw(self)
    # Inicia o jogo
Jogo()
