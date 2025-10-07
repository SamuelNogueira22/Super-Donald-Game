import pyxel

# Placeholders para as constantes de cena (serão sobrescritas por jogo.py)
# Evita erro de isn't defined
Scene_title = None
Scene_play = None
Scene_tutorial = None
Scene_credits = None
Scene_pause = None

def jogo_draw(self):
    if self.scene == Scene_title:
        pyxel.blt(0, 0, 2, 0, 0, 256, 256)
        titulo = ''
        hint = "Pressione ENTER para Jogar"
        subt =  ''
        dica = ''
        pyxel.text((pyxel.width - len(titulo)*4)//2, 90, titulo, 7)
        pyxel.text((pyxel.width - len(subt)*4)//2, 105, subt, 6)

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
            "- P: pausar",
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

    pyxel.cls(2)  # background

    self.desenha_cenario()

    fase_atual = (self.fase_x, self.fase_y)
    if fase_atual in self.moedas_por_fase:
        lista_moedas_da_fase = self.moedas_por_fase[fase_atual]
        for moeda in lista_moedas_da_fase:
            if moeda.ativa:
                pyxel.blt(moeda.x, moeda.y, 1, 32, 0, 16, 16, 3)

    if not self.jogador_morto:
        pyxel.blt(int(self.jogador_x), int(self.jogador_y), 0, 8, 16, 16, 16, 2)

    if self.jogo_ganho:
        texto = "PARABENS, VOCE VENCEU!"
        x_texto = (pyxel.width - len(texto) * 4) / 2
        y_texto = pyxel.height / 2 - 4
        pyxel.rect(x_texto - 4, y_texto - 4, len(texto) * 4 + 8, 16, 0)
        pyxel.text(x_texto, y_texto, texto, 7)

    texto_contador = f"{self.moedas_coletadas}/{self.total_de_moedas}"
    pos_x_texto = 5
    pos_y_texto = 5
    pyxel.text(pos_x_texto + 1, pos_y_texto + 1, texto_contador, 0)
    pyxel.text(pos_x_texto, pos_y_texto, texto_contador, 7)

    pos_x_icone = 25
    pos_y_icone = pos_y_texto - 7
    pyxel.blt(pos_x_icone, pos_y_icone, 1, 32, 0, 16, 16, 3)

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

    if self.scene == Scene_pause:
        pyxel.rect(64, 86, 128, 84, 0)
        pyxel.rectb(64, 86, 128, 84, 7)
        pyxel.text(64 + (128 - 6*4)//2, 94, "PAUSA", 7)
        for i, opt in enumerate(self.pause_options):
            sel = (i == self.pause_idx)
            txt = f"> {opt} <" if sel else f"  {opt}  "
            cor = 10 if sel else 7
            pyxel.text(64 + (128 - len(txt)*4)//2, 112 + i*14, txt, cor)
        pyxel.text(72, 86+84-12, "Setas: mover  Enter: OK", 5)

    camera_x = self.fase_x * 256
    camera_y = self.fase_y * 256
    fase_atual = (self.fase_x, self.fase_y)
    for mola in self.molas_por_fase.get(fase_atual, []):
        mola.draw()