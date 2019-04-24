import fastText
import numpy as np
from fastText import util
from collections import namedtuple

HolePosition = namedtuple("HolePosition", "x y direction length")
Hole = namedtuple("Hole", "position clue")

def compare_plain_holes(hole_position1, hole_position2):
    if hole_position1.x < hole_position2.x:
        return -1
    if hole_position1.x == hole_position2.x and hole_position1.y < hole_position2.y:
        return -1
    return 1

def get_cells(hp):
    cells = []
    for i in range(hp.length):
        if hp.direction == 'vertical':
            cells.append((hp.x + i, hp.y))
        else:
            cells.append((hp.x, hp.y + i))

    return cells

def get_connected_holes(fixed, holes):

    count = 0
    fixed_cells = get_cells(fixed.position)

    for hole in holes:
        if hole.position.direction == fixed.position.direction:
            continue
        
        for cell in get_cells(hole.position):
            if cell in fixed_cells:
                count += 1
                break
 
    return (count, -fixed.position.length)

def get_positions(grid, h, w):
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
                    holes.append(HolePosition(i, j, 'vertical', length))
            if (j == 0 or grid[i][j-1] == '#') and grid[i][j] == '.' :
                length = 0
                index = j
                while index < w and grid[i][index] == '.':
                    length += 1
                    index += 1
                if length > 1:
                    holes.append(HolePosition(i, j, 'horizontal', length))
    return holes

def find_nearest_words_ids_for_hint(model, text):
    """
    model is loaded fastText model
    text is a sentence
    """

    hint_vector = model.get_sentence_vector(text)
    all_vectors = model.get_output_matrix()

    similarity_vector = np.matmul(all_vectors, hint_vector)

    result_vector = []
    index = 0
    for result in similarity_vector:
        result_vector.append( (index, result))
        index += 1

    return sorted(result_vector, key=lambda tuple: -tuple[1])

def get_word_list(wordmap, ids, word_length):
    """
    wordmap is a map int -> string
    ids is a list of ids
    word_length is a length of word to fit it into crossword
    """

    result_list = []

    for (id, _) in ids:
        if len(wordmap[id][0]) == word_length:
            result_list.append(wordmap[id][0])

    return result_list

if __name__ == "__main__":
    print "Loading model..."    
    
    f = fastText.load_model("../result/fil5.bin")

    wordmap = {}
    index = 0
    for w in f.get_words():
        wordmap[index] = (w, f.get_word_vector(w))
        index += 1

    print "Parsing crossword..."
    lines = ""

    with open("input.txt") as file_input:
        lines = [line[:-1] for line in file_input.readlines()]
    
    h, w = [int(n) for n in lines[0].split(' ')]
    lines = lines[1:]
    grid, lines = lines[:h], lines[h:]
    hhc, lines = int(lines[0]), lines[1:] # horizontal hints and count
    hh, lines = lines[:hhc], lines[hhc:]
    vhc, vh = int(lines[0]), lines[1:] # vertical hints and count

    positions = get_positions(grid, h, w)
    if len([key for key in positions if key.direction == 'vertical']) != vhc or len([key for key in positions if key.direction == 'horizontal']) != hhc:
        print "Cos jest nie tak z krzyzowka"

    sorted_positions = sorted(positions, cmp=compare_plain_holes)

    holes = []
    v_idx, h_idx = 0, 0
    for position in sorted_positions:
        if position.direction == 'vertical':
            holes.append(Hole(position, vh[v_idx]))
            v_idx += 1
        else:
            holes.append(Hole(position, hh[h_idx]))
            h_idx += 1

    holes = sorted(holes, key=lambda hole: get_connected_holes(hole, holes))
    for hole in holes:
        word_list = get_word_list(wordmap, find_nearest_words_ids_for_hint(f, hole.clue), hole.position.length)
        print word_list[:10]

# pomysl na solver:
# * przesortuj hasla po stopniu ich uwiklania malejaco
# * pilotazowo: wpisz jedno slowo w pierwsza dziure i pusc A*
# * jak nie pyknie, to nastepne
# * ryzyko jest takie, ze pojedyncza iteracja A* zajmie duzo czasu

# siec wypalona, trzeba nieco posprzatac i solver napisac