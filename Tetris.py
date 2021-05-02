import pygame as pg
from random import randrange, choice
from copy import deepcopy
import sys

W, H = 10, 20
TILE = 35
GAME_RES = W * TILE, H * TILE
RES = 600, 760
fps = 60

grid = [pg.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figure_pos = [ [(-1,0),(-2,0),(0,0),(1,0)],
              [(0,0),(-1,0),(0,-1),(1,-1)],
              [(0,0),(-1,-1),(0,-1),(1,0)],
              [(-1,0),(0,1),(-1,-1),(-1,1)],
              [(0,0),(0,-1),(0,1),(-1,1)],
              [(0,0),(-1,0),(0,-1),(0,1)],
              [(0,0),(0,-1),(-1,-1),(-1,0)] ]

figures = [ [pg.Rect(x + W // 2, y + 1, 1, 1) for x, y in f_pos] for f_pos in figure_pos ]
figure_rect = pg.Rect(0, 0, TILE - 2, TILE - 2)
nextfig_rect = pg.Rect(0, 0, TILE - 2, TILE - 2)

pg.init()
sc = pg.display.set_mode(RES)
game_sc = pg.Surface(GAME_RES)
clock = pg.time.Clock()

counter, fall_speed, speed_limit = 0, 80, 2000
field = [[0 for i in range(W)] for j in range(H)]

bg = pg.image.load('bckg.jpg').convert()
bg = pg.transform.scale(bg, RES)

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
#fig_color = (20,255,20)

main_font = pg.font.Font('TetrisFont.ttf', 45)
font = pg.font.Font('TetrisFont.ttf', 35)

title_tetris = main_font.render('TETRIS', True, pg.Color('darkorange'))
title_score = font.render('score :', True, pg.Color('darkorange'))
title_record = font.render('record :', True, pg.Color('purple'))

score = 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500 }
lines = 0

get_color = lambda: ( randrange(60, 256), randrange(100, 256), randrange(60, 256) )
color = get_color()

pg.mixer.music.load('tetrissong.wav')
pg.mixer.music.play(-1)


def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return True
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x] != 0:
        return True
    return False


def get_record():
    try:
        with open('record.txt') as f:
            return f.read()
    except FileNotFoundError :
        with open('record.txt', 'w') as f:
            f.write('0')


def set_record(record, score):
    rec = max(int(record), score)
    with open('record.txt', 'w') as f:
        f.write(str(rec))


while True:
    dx = 0
    rotate = False
    record = get_record()

    sc.blit(bg,(0,0))
    sc.blit(game_sc, (20,20))
    game_sc.fill(pg.Color('darkslategrey'))

    # delay for full lines
    for i in range(lines):
        pg.time.delay(200)
    # control
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                dx = -1
            elif event.key == pg.K_RIGHT:
                dx = 1
            elif event.key == pg.K_UP:
                rotate = True
            elif event.key == pg.K_DOWN:
                speed_limit = 100
            elif event.key == pg.K_1:
                pg.mixer.music.pause()
            elif event.key == pg.K_2:
                pg.mixer.music.unpause()
            elif event.key == pg.K_3:
                pg.mixer.music.set_volume(0.3)

    # moving on OX
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if check_borders():
            figure = deepcopy(figure_old)
            break

    # moving on OY
    counter += fall_speed
    if counter > speed_limit:
        counter = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if check_borders():
                for j in range(4):
                    field[figure_old[j].y][figure_old[j].x] = color #pg.Color('white')
                figure = deepcopy(next_figure)
                next_figure = deepcopy(choice(figures))
                color = get_color()
                speed_limit = 2000
                break

    # rotation
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            delta_x = figure[i].y - center.y
            delta_y = figure[i].x - center.x
            figure[i].x = center.x - delta_x
            figure[i].y = center.y + delta_y
            if check_borders():
                figure = deepcopy(figure_old)
                break

    # chek lines
    lines = 0
    for i in range(H - 1, -1, -1):
        if not field[i].count(0):
            field.pop(i)
            field.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            lines += 1
            fall_speed += 3
    # compute the score
    score += scores[lines]

    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pg.draw.rect(game_sc,color, figure_rect)

    # draw field
    for i in range(H):
        for j in range(W):
            if field[i][j] != 0 :
                figure_rect.x, figure_rect.y = j * TILE, i * TILE
                pg.draw.rect(game_sc, field[i][j], figure_rect)

    # draw grid
    [pg.draw.rect(game_sc, (100, 100, 100), i_rect, 1) for i_rect in grid]

    # draw next figure
    for i in range(4):
        nextfig_rect.x = next_figure[i].x * TILE + 310
        nextfig_rect.y = next_figure[i].y * TILE + 200
        pg.draw.rect(sc, color, nextfig_rect)

    # draw titles
    sc.blit(title_tetris, (400, 0))
    sc.blit(title_score, (420, 600))
    sc.blit(font.render(str(score), True, pg.Color('white')), (420, 650)  )
    sc.blit(title_record, (420, 470) )
    sc.blit(font.render(record, True, pg.Color('gold') ), (420, 520))


    # game over
    for i in range(W):
        if not field[0][i] == 0:
            set_record(record, score)
            counter, fall_speed, speed_limit = 0, 80, 2000
            field = [[0 for i in range(W)] for j in range(H)]
            score = 0
            for i_rect in grid:
                pg.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20,20) )
                pg.display.flip()
                clock.tick(200)

    pg.display.flip()
    clock.tick(fps)



