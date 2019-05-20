from collections import namedtuple
from solution_importer import get_solution, Solution
VERTICAL = 'vertical'
HORIZONTAL = 'horizontal'
HolePosition = namedtuple("HolePosition", "x y direction length")
Hole = namedtuple("Hole", "position clue answer")
Crossword = namedtuple("Crossword", "grid hints")

def compare_plain_holes(hole_position1, hole_position2):
    """
    Returns -1 if first hole_position is close to (0,0), 1 otherwise
    """

    if hole_position1.x < hole_position2.x:
        return -1
    if hole_position1.x == hole_position2.x and hole_position1.y < hole_position2.y:
        return -1
    return 1


# def get_cells(hp):
#     """
#     Given position of hole, returns list of cells belonging to the hole
#     """
    
#     cells = []
#     for i in range(hp.length):
#         if hp.direction == VERTICAL:
#             cells.append((hp.x + i, hp.y))
#         else:
#             cells.append((hp.x, hp.y + i))

#     return cells

# def get_connected_holes(fixed, holes):
#     """
#     For fixed hole calculates, how many holes crosses the fixed hole.
#     """

#     count = 0
#     fixed_cells = get_cells(fixed.position)

#     for hole in holes:
#         if hole.position.direction == fixed.position.direction:
#             continue
        
#         for cell in get_cells(hole.position):
#             if cell in fixed_cells:
#                 count += 1
#                 break
 
#     return (-count, -fixed.position.length)

def get_positions(grid, h, w):
    """
    Returns all HolePositions for the grid
    """

    holes = []
    for i in range(h):
        for j in range(w):
            if (i == 0 or grid[i-1][j] == '#') and grid[i][j] == '.' :
                length = 0
                index = i
                while index < h and grid[index][j] == '.':
                    length += 1
                    index += 1
                if length > 1:
                    holes.append(HolePosition(i, j, VERTICAL, length))
            if (j == 0 or grid[i][j-1] == '#') and grid[i][j] == '.' :
                length = 0
                index = j
                while index < w and grid[i][index] == '.':
                    length += 1
                    index += 1
                if length > 1:
                    holes.append(HolePosition(i, j, HORIZONTAL, length))
    return holes


def get_crossword(filename, solution_filename = None):
    lines = ""
    solutions = []
    with open(filename) as file_input:
        lines = [line[:-1] for line in file_input.readlines()]
    
    
    h, w = [int(n) for n in lines[0].split(' ')]
    lines = lines[1:]
    grid, lines = lines[:h], lines[h:]
    hhc, lines = int(lines[0]), lines[1:] # horizontal hints and count
    horizontal_hints, lines = lines[:hhc], lines[hhc:]
    vhc, vertical_hints = int(lines[0]), lines[1:] # vertical hints and count

    positions = get_positions(grid, h, w)
    if len([key for key in positions if key.direction == VERTICAL]) != vhc or len([key for key in positions if key.direction == HORIZONTAL]) != hhc:
        print "Number of holes in crossword doesn't correspond to number of given hints!"
        exit(0)

    positions = sorted(positions, cmp=compare_plain_holes)
    
    if solution_filename is not None:
        solutions = get_solution(solution_filename)
    else:
        solutions = Solution(['' for i in range(hhc)], ['' for i in range(vhc)])

    holes = []
    v_idx, h_idx = 0, 0
    for position in positions:
        if position.direction == VERTICAL:
            holes.append(Hole(position, vertical_hints[v_idx], solutions.vertical[v_idx]))
            v_idx += 1
        else:
            holes.append(Hole(position, horizontal_hints[h_idx], solutions.horizontal[h_idx]))
            h_idx += 1

    #holes = sorted(holes, key=lambda hole: get_connected_holes(hole, holes))

    return Crossword(grid, holes)