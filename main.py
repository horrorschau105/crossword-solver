import fastText
import numpy as np
from fastText import util
from collections import namedtuple
from Queue import PriorityQueue

HolePosition = namedtuple("HolePosition", "x y direction length")
Hole = namedtuple("Hole", "position clue")
CrosswordInstance = namedtuple("CrosswordInstance", "rank crossword next_hole")
Answer = namedtuple("Answer", "word rank")

def compare_plain_holes(hole_position1, hole_position2):
    """
    Returns -1 if first hole_position is close to (0,0), 1 otherwise
    """

    if hole_position1.x < hole_position2.x:
        return -1
    if hole_position1.x == hole_position2.x and hole_position1.y < hole_position2.y:
        return -1
    return 1

def get_cells(hp):
    """
    Given position of hole, returns list of cells belonging to the hole
    """
    
    cells = []
    for i in range(hp.length):
        if hp.direction == 'vertical':
            cells.append((hp.x + i, hp.y))
        else:
            cells.append((hp.x, hp.y + i))

    return cells

def get_connected_holes(fixed, holes):
    """
    For fixed hole calculates, how many holes crosses the fixed hole.
    """

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
    for (id, rank) in ids:
        if len(wordmap[id][0]) == word_length:
            result_list.append(Answer(wordmap[id][0], rank))
    return result_list

def get_pattern_from_crossword(crossword, position):
    """
    For given crossword, returns pattern formed by written yet answers
    """
    result = []
    i,j = position.x, position.y
    for index in range(position.length):
        if position.direction == 'vertical':
            result.append(crossword[i + index][j])
        else:
            result.append(crossword[i][j + index])
    return ''.join(result)

def fit_pattern(pattern, word):
    """
    Checks if given word fits to the pattern
    """
    if len(pattern) != len(word):
        return False
    for i in range(len(pattern)):
        if pattern[i] != '.' and pattern[i] != word[i]:
            return False
    return True

def write_into(crossword, word, position):
    """
    Writes given word into crossword and returns it
    """
    i,j = position.x, position.y
    crossword = [list(row) for row in crossword]
    for index in range(position.length):
        if position.direction == 'vertical':
            crossword[i + index][j] = word[index]
        else:
            crossword[i][j + index] = word[index]
    return [''.join(row) for row in crossword]

def show_solution(crossword_instance, holes):
    """
    Prints crossword and final rank
    """
    print
    #for row in crossword_instance.crossword:
    #    print row.replace('#', '.')

    print 'Used words: ', [get_pattern_from_crossword(crossword_instance.crossword, hole.position) for hole in holes]
    print 'Overall rank: ', crossword_instance.rank

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
    clues_count = vhc + hhc

    fitting_words_for_holes = []

    for i in range(clues_count):
        fitting_words_for_holes.append(get_word_list(wordmap, find_nearest_words_ids_for_hint(f, holes[i].clue), holes[i].position.length))

    solution_count = 0

    queue = PriorityQueue()
    queue.put(CrosswordInstance(0, grid, 0))

    while not queue.empty():
        first = queue.get()

        if first.next_hole == clues_count:
            show_solution(first, holes)

            solution_count += 1
            if solution_count > 100000:
                break
            
        else:
            pattern = get_pattern_from_crossword(first.crossword, holes[first.next_hole].position)

            has_good_pattern = [word for word in fitting_words_for_holes[first.next_hole] if fit_pattern(pattern, word.word)]

            for word in has_good_pattern:
                new_crossword = write_into(first.crossword, word.word, holes[first.next_hole].position)
                queue.put(CrosswordInstance(first.rank - word.rank, new_crossword, first.next_hole + 1))