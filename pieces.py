pieces = {
    "SQUARE" : (
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
        "yellow"
    ),

    "LINE" : (
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        "cyan"
    ),

    "T_BLOCK" : (
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 0),
        "purple"
    ),

    "LEFT_SQUIGGLY" : (
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 1),
        "red"
    ),

    "RIGHT_SQUIGGLY" : (
        (0, 1),
        (1, 0),
        (1, 1),
        (2, 0),
        "lime"
    ),

    "LEFT_L" : (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        "blue"
    ),

    "RIGHT_L" : (
        (0, 0),
        (1, 0),
        (1, 1),
        (1, 2),
        "orange"
    )
}

def get_pieces_cells(input_piece):
    return pieces[input_piece]