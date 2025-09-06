import pygame
import os
import random
import time

pygame.init()

# ---------------------- CONFIGURAÇÃO ----------------------
TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)


# ---------------------- CLASSES ----------------------
class Passaro:
    IMGS = IMAGENS_PASSARO
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5
    GRAVIDADE = 0.5
    VELOCIDADE_PULO = -8
    VELOCIDADE_MAX = 12

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 0
        self.angulo = 0
        self.contagem_imagem = 0
        self.altura = y
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = self.VELOCIDADE_PULO
        self.altura = self.y

    def mover(self):
        self.velocidade += self.GRAVIDADE
        if self.velocidade > self.VELOCIDADE_MAX:
            self.velocidade = self.VELOCIDADE_MAX
        self.y += self.velocidade

        if self.velocidade < 0:
            self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()
        self.VELOCIDADE = 5

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return topo_ponto or base_ponto


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


# ---------------------- FUNÇÕES ----------------------
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (0, 0, 0))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()


def mostrar_game_over(tela, pontos):

    fonte_game_over = pygame.font.SysFont("arial", 70, bold=True)
    fonte_botao = pygame.font.SysFont("arial", 40, bold=True)

    # Mensagem GAME OVER
    texto = fonte_game_over.render("GAME OVER", True, (255, 0, 0))
    ret_texto = texto.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA // 2 - 50))
    tela.blit(texto, ret_texto)

    # Botão Reiniciar
    botao_largura, botao_altura = 200, 50
    botao_x = TELA_LARGURA // 2 - botao_largura // 2
    botao_y = TELA_ALTURA // 2 + 20
    pygame.draw.rect(tela, (0, 255, 0), (botao_x, botao_y, botao_largura, botao_altura))

    texto_botao = fonte_botao.render("RESTART", True, (0, 0, 0))
    ret_botao = texto_botao.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA // 2 + 45))
    tela.blit(texto_botao, ret_botao)

    pygame.display.update()
    return pygame.Rect(botao_x, botao_y, botao_largura, botao_altura)


# ---------------------- MAIN ----------------------
def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    iniciado = False
    velocidade_inicial = 5
    Cano.VELOCIDADE = velocidade_inicial
    Chao.VELOCIDADE = velocidade_inicial

    rodando = True
    while rodando:
        relogio.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()
                    iniciado = True

        if not iniciado:
            desenhar_tela(tela, passaros, canos, chao, pontos)
            continue

        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

            # aumenta velocidade só depois do 5º ponto
            if pontos > 5:
                Cano.VELOCIDADE = velocidade_inicial + (pontos - 5) // 2
                Chao.VELOCIDADE = velocidade_inicial + (pontos - 5) // 2

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        # ---------------------- GAME OVER ----------------------
        if len(passaros) == 0:
            botao = mostrar_game_over(tela, pontos)
            esperando_reinicio = True
            tempo_inicial = time.time()
            tempo_espera = 2  # segundos antes de permitir reiniciar

            while esperando_reinicio:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        quit()

                tempo_decorrido = time.time() - tempo_inicial
                if tempo_decorrido >= tempo_espera:
                    for evento in pygame.event.get():
                        if evento.type == pygame.MOUSEBUTTONDOWN:
                            if botao.collidepoint(evento.pos):
                                esperando_reinicio = False
                                main()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_SPACE:
                                esperando_reinicio = False
                                main()

        desenhar_tela(tela, passaros, canos, chao, pontos)


# ---------------------- EXECUTAR ----------------------
if __name__ == "__main__":
    main()
