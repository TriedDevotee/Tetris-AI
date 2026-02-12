import copy
import random
import tkinter as tk
import pygame as pg
import math

import pieces

HEIGHT = 660
WIDTH = 300

BOARD_WIDTH = 10
BOARD_HEIGHT = 22

FRAME_TIMER = 0
DAS_TIMER = 0
POST_LAND_TIMER = -1

PIECES_FALLING = False

CELL_SIZE = 30

DO_BASE_PIECES = True
AI_INSTANT_PLACE = True

BOARD = [[0 for i in range(BOARD_WIDTH)] for j in range(BOARD_HEIGHT)]

tetromino_bag = []

curr_falling = False

keys_held = {
    "Left" : False,
    "Right" : False,
    "Down" : False
}

key_timer = {
    "Left" : 0,
    "Right" : 0
}

current_piece = {
    "cells" : None,
    "color" : None,
    "x" : None,
    "y" : None,
}

def piece_collides(px, py, cells):
    for coordX, coordY in cells:
        borderX = px + coordX
        borderY = py + coordY

        if borderX < 0 or borderX >= BOARD_WIDTH:
            return True
        if borderY >= BOARD_HEIGHT:
            return True
        if borderY >= 0 and BOARD[borderY][borderX] != 0:
            return True
        
    return False

def get_piece_width(cells):
    max_x = 0

    for x, y in cells:
        if x > max_x:
            max_x = x
    
    return max_x + 1

def normalize(cells):
    min_x = min(x for x, y in cells)
    min_y = min(y for x, y in cells)

    return [(x - min_x, y - min_y) for x, y in cells]

def rotate_current_piece():
    rotated = [(-y, x) for x, y in current_piece["cells"]]

    rotated = normalize(rotated)

    if not piece_collides(current_piece["x"], current_piece["y"], rotated):
        current_piece["cells"] = rotated
    
    elif get_piece_width(rotated) + current_piece["x"] >= BOARD_WIDTH:
        current_piece["x"] = BOARD_WIDTH - get_piece_width(rotated)
        current_piece["cells"] = rotated

    
def on_key_press(event):
    if event.keysym in keys_held:
        keys_held[event.keysym] = True
    elif event.keysym == "Up":
        rotate_current_piece()
    elif event.keysym == "space":
        while curr_falling:
            update_curr_piece()

def on_key_release(event):
    if event.keysym in keys_held:
        keys_held[event.keysym] = False

def move_piece():
    if keys_held["Right"]:
        if not piece_collides(current_piece["x"] + 1, current_piece["y"], current_piece["cells"]):
            current_piece["x"] = min(current_piece["x"] + 1, BOARD_WIDTH - (get_piece_width(current_piece["cells"])))
    if keys_held["Left"]:
        if not piece_collides(current_piece["x"] - 1, current_piece["y"], current_piece["cells"]):
            current_piece["x"] = max(current_piece["x"] - 1, 0)
    if keys_held["Down"] and FRAME_TIMER % 1 == 0:
        update_curr_piece()

def fill_bag():
    global tetromino_bag

    pieces_to_pick = list(pieces.pieces.keys())

    if DO_BASE_PIECES:
        pieces_to_pick = pieces_to_pick[0:7]

    random.shuffle(pieces_to_pick)

    tetromino_bag = pieces_to_pick

def detect_for_lines(board=BOARD):
    lines_to_kill = []

    for y in range(BOARD_HEIGHT - 1, -1, -1):

        zero_count = 0

        for x in range(BOARD_WIDTH):
            if board[y][x] == 0:
                zero_count += 1

        if zero_count == 0:
            lines_to_kill.append(y)

    return lines_to_kill

def kill_lines():
    global BOARD

    lines_to_kill = detect_for_lines()

    for row in sorted(lines_to_kill):
        for y in range(row, 0, -1):
            BOARD[y] = BOARD[y-1].copy()
        BOARD[0] = [0] * BOARD_WIDTH

    
def add_new_piece():
    global current_piece

    if len(tetromino_bag) == 0:
        fill_bag()

    piece_index = tetromino_bag.pop()

    piece_data = pieces.pieces[piece_index]

    current_piece["cells"] = piece_data[:-1]
    current_piece["color"] = piece_data[-1]
    current_piece["x"] = 3
    current_piece["y"] = 0

def lock_piece():
    for x, y in current_piece["cells"]:
        x_index = current_piece["x"] + x
        y_index = current_piece["y"] + y

        if y_index >= 0:
            BOARD[y_index][x_index] = current_piece["color"]

def update_curr_piece():
    global curr_falling, current_piece, PIECE_WIDTH, POST_LAND_TIMER

    if not piece_collides(current_piece["x"], current_piece["y"] + 1, current_piece["cells"]):
        current_piece["y"] += 1
    else:
        if POST_LAND_TIMER == -1:
            POST_LAND_TIMER = 20
        else:
            if POST_LAND_TIMER <= 0:
                lock_piece()
                curr_falling = False

                POST_LAND_TIMER = -1

def get_all_rotations(cells=current_piece["cells"]):
    rotations = []
    current = cells

    for _ in range(4):
        current = normalize(current)
        if current not in rotations:
            rotations.append(current)
        current = ([(-y, x) for x, y in current])
    
    return rotations

def get_lowest_point(x, cells):
    y=0
    while not piece_collides(x, y + 1,cells=cells):
        y += 1
    return y

def simulate_board(cells, x, y, color):
    new_board = copy.deepcopy(BOARD)

    for px, py in cells:
        if y + py >= 0:
            new_board[y+py][x+px] = color
    
    return new_board

def get_column_heights(board):
    heights = []
    for x in range(BOARD_WIDTH):
        min_height = 0
        for y in range(BOARD_HEIGHT):
            if board[y][x] != 0:
                min_height = BOARD_HEIGHT - y
                break
        heights.append(min_height)
    
    return heights

def count_holes(board):
    count = 0

    for x in range(BOARD_WIDTH):
        block_found = False

        for y in range(BOARD_HEIGHT):
            if board[y][x] != 0:
                block_found = True
            elif block_found:
                count += 1

    return count
        

def evaluate(board):
    heights = get_column_heights(board)
    holes = count_holes(board)
    bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range (BOARD_WIDTH - 1))
    lines = detect_for_lines(board)

    if DO_BASE_PIECES:
        height_weight = -0.510066
        hole_weight = -0.35663
        bumpiness_weight =  -0.184483
        lines_weight = +0.760666

    else:
        height_weight = -0.95
        hole_weight = -0.95
        bumpiness_weight = -0.40
        lines_weight = +1.5

    return (
        height_weight * sum(heights) +
        hole_weight * holes + 
        bumpiness_weight * bumpiness + 
        lines_weight * len(lines)
    )

def find_best_move(cells):
    best_score = -math.inf
    best_move = None
    best_xpos = 0

    for rotation in get_all_rotations(cells):
        for x_pos in range(BOARD_WIDTH):

            if piece_collides(x_pos, 0, rotation):
                continue

            y_pos = get_lowest_point(x_pos, rotation)
            new_board = simulate_board(
                rotation, 
                x_pos, 
                y_pos, 
                current_piece["color"])
            
            score = evaluate(new_board)

            if score > best_score:
                best_score = score
                best_move = (rotation, x_pos)

                best_xpos = x_pos

    print(f"Best move = {best_move} at position {best_xpos} with a score of {best_score}")

    return best_move




def draw_cell(start_x, start_y, color):
    px = start_x * CELL_SIZE
    py = start_y * CELL_SIZE

    canvas.create_rectangle(
        px,
        py,
        px + CELL_SIZE,
        py + CELL_SIZE,
        fill=color
    )

def draw_pieces():
    for y in range(BOARD_HEIGHT - 1, -1, -1):
        for x in range(BOARD_WIDTH):

            if BOARD[y][x] != 0:
                draw_cell(x, y, BOARD[y][x])
    
    if current_piece["cells"]:
        for x, y in current_piece["cells"]:
            draw_cell(
                current_piece["x"] + x,
                current_piece["y"] + y,
                current_piece["color"]
            )

def run_AI_game_loop():
    (rotation, x) = find_best_move(current_piece["cells"])

    current_piece["x"] = x
    current_piece["cells"] = rotation


    

def game_loop():
    global curr_falling, FRAME_TIMER, POST_LAND_TIMER

    canvas.delete("all")

    if (FRAME_TIMER % 1 == 0):
        if not curr_falling:
            add_new_piece()
            run_AI_game_loop()
            curr_falling = True
        else:
            update_curr_piece()

        kill_lines()
        
    #if (FRAME_TIMER % 2 == 0):
        #move_piece()

    draw_pieces()

    FRAME_TIMER += 1
    
    if POST_LAND_TIMER != 0:
        POST_LAND_TIMER -= 1

    root.after(10, game_loop)


root = tk.Tk()

root.title("Tetris")

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg="black")
canvas.pack()

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

pg.mixer.init()
pg.mixer.music.load("Tetris.mp3")
#pg.mixer.music.play(-1)

game_loop()

root.mainloop()