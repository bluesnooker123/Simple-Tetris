import random
import os
import pygame
from threading import Thread
from pygame import mixer
import ctypes

col = 10 
row = 20  
s_width = 800  
s_height = 750  
play_width = 300 
play_height = 600  
block_size = 30 
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50
filepath = os.getcwd() + '/highscore.txt'
fontpath = os.getcwd() + '/arcade.ttf'
fontpath_mario = os.getcwd() + '/mario.ttf'
strName = ""
bMusic = True
pygame.font.init()


S = [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']]
I = [['.....', '..0..', '..0..', '..0..', '..0..'], ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)] 
        self.rotation = 0 


def grid_create(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]

    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]  
                grid[y][x] = color

    return grid


def shape_format_convert(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format): 
        row = list(line)
        for j, column in enumerate(row):  
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) 

    return positions

def space_valid(piece, grid):
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    accepted_pos = [x for item in accepted_pos for x in item]
    formatted_shape = shape_format_convert(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True

def lost_check(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def shape_get():
    return Piece(5, 0, random.choice(shapes))

def text_middle_draw(text, size, color, surface):
    font = pygame.font.Font(fontpath, size, bold=False, italic=True)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))

def grid_draw(surface):
    r = g = b = 0
    grid_color = (r, g, b)

    for i in range(row):
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))


def rows_clear(grid, locked):
    increment = 0
    for i in range(len(grid) - 1, -1, -1):     
        grid_row = grid[i]                    
        if (0, 0, 0) not in grid_row:          
            increment += 1
            index = i                          
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]     
                except ValueError:
                    continue

    if increment > 0:
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                     
                new_key = (x, y + increment)
                locked[new_key] = locked.pop(key)

    return increment

def next_shape_draw(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)

    surface.blit(label, (start_x, start_y - 30))

def window_draw(surface, grid, score=0, last_score=0, bMusicTemp = True):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.Font(fontpath_mario, 65, bold=True)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))
    font = pygame.font.Font(fontpath, 30)
    label = font.render('SCORE   ' + str(score) , 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    surface.blit(label, (start_x, start_y + 200))

    bMusic = bMusicTemp
    if bMusic == True:
        label = font.render('Music   OFF', 1, (255, 255, 255))
    elif bMusic == False:
        label = font.render('Music   ON', 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    surface.blit(label, (start_x, start_y + 300))

    label = font.render('USER Name', 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 450)
    surface.blit(label, (start_x, start_y + 200))

    font = pygame.font.Font(fontpath, 25)
    label = font.render(strName, 1, (255, 255, 255))
    start_x = top_left_x + play_width + 70
    start_y = top_left_y + (play_height / 2 - 400)
    surface.blit(label, (start_x, start_y + 200))

    font = pygame.font.Font(fontpath, 30)
    label_hi = font.render('HIGHSCORE   ' + str(last_score), 1, (255, 255, 255))
    start_x_hi = top_left_x - 240
    start_y_hi = top_left_y + 200
    surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))

    font = pygame.font.Font(fontpath, 30)
    label_hi = font.render('u     Undo', 1, (255, 255, 255))
    start_x_hi = top_left_x - 240
    start_y_hi = top_left_y
    surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))

    font = pygame.font.Font(fontpath, 30)
    label_hi = font.render('r     Redo', 1, (255, 255, 255))
    start_x_hi = top_left_x - 240
    start_y_hi = top_left_y + 100
    surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))
    
    for i in range(row):
        for j in range(col):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    grid_draw(surface)
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

def score_update(new_score):
    score = max_score_get()

    with open(filepath, 'w') as file:
        if new_score > score:
            file.write(str(new_score))
        else:
            file.write(str(score))

def max_score_get():
    with open(filepath, 'r') as file:
        lines = file.readlines()     
        score = int(lines[0].strip()) 
    return score

def main(window):
    locked_positions = {}
    grid_create(locked_positions)
    change_piece = False
    run = True
    current_piece = shape_get()
    next_piece = shape_get()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.35
    level_time = 0
    score = 0
    bMusicTemp = bMusic
    last_score = max_score_get()
    pause=0
    last_block = []
    last_block_color = (0,0,0)
    flag_undo_pressed = 0

    while run:
        grid = grid_create(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not space_valid(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
                last_block = shape_format_convert(current_piece)
                last_block_color = current_piece.color
                flag_undo_pressed = 0
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mixer.init()
                    mixer.music.stop()
                    if bMusicTemp == True:
                        mixer.music.load("left.mp3")
                        mixer.music.play()
                    current_piece.x -= 1
                    if not space_valid(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    mixer.init()
                    mixer.music.stop()
                    if bMusicTemp == True:
                        mixer.music.load("right.mp3")
                        mixer.music.play()
                    current_piece.x += 1
                    if not space_valid(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    mixer.init()
                    mixer.music.stop()
                    if bMusicTemp == True:
                        mixer.music.load("down.mp3")
                        mixer.music.play()
                    current_piece.y += 1
                    if not space_valid(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    mixer.init()
                    mixer.music.stop()
                    if bMusicTemp == True:
                        mixer.music.load("up.mp3")
                        mixer.music.play()
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not space_valid(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                elif event.key == pygame.K_p:
                    pause = True
                elif event.key == pygame.K_s:
                    pause = False
                elif event.key == pygame.K_u:              
                    if flag_undo_pressed == 0:      
                        for i in range(len(last_block)):
                            x, y = last_block[i]
                            if y >= 0:
                                locked_positions[(x,y)] = (0,0,0)       
                    else:
                        ctypes.windll.user32.MessageBoxW(0, "You already pressed Undo button (u)", "Warning", 0)
                    flag_undo_pressed = 1                    
                elif event.key == pygame.K_r:              
                    if flag_undo_pressed == 1:      
                        for i in range(len(last_block)):
                            x, y = last_block[i]
                            if y >= 0:
                                grid[y][x] = last_block_color
                                locked_positions[(x,y)] = last_block_color                   
                    else:
                        ctypes.windll.user32.MessageBoxW(0, "You cann't use Redo button!\nBecause:\n- Maybe you already pressed Redo button (r)\n- Or you can only press redo button before next block is setup.", "Warning", 0)
                    flag_undo_pressed = 0                       
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bMusicTemp == True:
                    bMusicTemp = False
                elif bMusicTemp == False:
                    bMusicTemp = True

            if pause == True:
                pygame.time.delay(3000)

            if pause == False:
                pygame.time.delay(0)
                continue                  

        piece_pos = shape_format_convert(current_piece)

        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color
           
        if change_piece: 
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color  
            current_piece = next_piece
            next_piece = shape_get()
            change_piece = False
            score += rows_clear(grid, locked_positions) * 10 
            score_update(score)

            if last_score < score:
                last_score = score

        window_draw(window, grid, score, last_score, bMusicTemp)
        next_shape_draw(next_piece, window)
        pygame.display.update()

        if lost_check(locked_positions):
            run = False

    text_middle_draw('You Lost', 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000) 
    pygame.quit()

def main_menu(window):
    run = True
    
    while run:
        text_middle_draw('Press any key to begin', 50, (255, 255, 255), window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                main(window)

    pygame.quit()

if __name__ == '__main__':
    strName = input("Please input your name: ")

    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    main_menu(win)
