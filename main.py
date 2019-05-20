import numpy as np
from fastText import util
from Queue import PriorityQueue
from sys import argv, exit
from collections import namedtuple
from crossword_parser import get_crossword, VERTICAL, HORIZONTAL
from model_loader import get_model, normalize_vector, get_model_from_vector_list
from resolver import get_fitting_words, fit_pattern
from frequencies import get_frequencies
MAX_SOLUTIONS = 10
CrosswordInstance = namedtuple("CrosswordInstance", "rank crossword next_hole")
HoleWithPossibilities = namedtuple("HoleWithPossibilities", "hole list")
top100 = []
freq_map = {}

def get_pattern_from_crossword(crossword, position):
    """
    For given crossword, returns pattern formed by written yet answers
    """
    result = []
    i,j = position.x, position.y
    for index in range(position.length):
        if position.direction == VERTICAL:
            result.append(crossword[i + index][j])
        else:
            result.append(crossword[i][j + index])
    return ''.join(result)


def write_into(crossword, word, position):
    """
    Writes given word into crossword and returns it
    """
    i,j = position.x, position.y
    crossword = [list(row) for row in crossword]
    for index in range(position.length):
        if position.direction == VERTICAL:
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

def ban100_log_norm(model, clue):
    global top100, freq_map
    subwords = [w for w in clue.split(' ') if w not in top100 and w in model.own_model]
    return sum(model.own_model[w] / np.log(freq_map[w]) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def order(possibilities):
    # tutaj zalutować jakieś fajne sortowanie dziur, by bylo szybko
    return possibilities

if __name__ == "__main__":
    if len(argv) < 3:
        print "Usage: python main.py <model file> <crossword file>"
        print "eg. pythom main.py ../result/fil5.bin 5x5.crossword"
        exit(0)

    model_filename, crossword_filename = argv[1], argv[2]

    print "Loading model..."    
    
    model = get_model_from_vector_list(model_filename)
    
    print "Parsing crossword..."

    crossword = get_crossword(crossword_filename)

    print "Importing word frequences..."

    freq_map, top100 = get_frequencies(100)
    
    print 'Getting possible answers...'
    
    possibilities = []
    idx = 0
    for fitting in get_fitting_words(crossword, model, ban100_log_norm):
        possibilities.append(HoleWithPossibilities(crossword.hints[idx], fitting))
        print crossword.hints[idx].clue, fitting[0].rank
        idx += 1
    
    possibilities = order(possibilities)

    #MAX_POSSIBILITIES = 30
    #WORST_SIMILARITY = (min(arr.list[MAX_POSSIBILITIES].rank for arr in possibilities))
    #print 'Worst similarity:', WORST_SIMILARITY

    WORST_SIMILARITY = 0.5
    solution_count = 0

    queue = PriorityQueue()
    queue.put(CrosswordInstance(0, crossword.grid, 0))

    print 'Solving crossword...'
    iterations = 0

    while not queue.empty():
        iterations += 1

        if iterations % 1000 == 0:
            print iterations
        front = queue.get()

        #print front.crossword

        if front.next_hole == len(crossword.hints):
            show_solution(front, crossword.hints)

            solution_count += 1
            if solution_count > MAX_SOLUTIONS:
                break
            
        else:
            pattern = get_pattern_from_crossword(front.crossword, crossword.hints[front.next_hole].position)

            has_good_pattern = [word for word in possibilities[front.next_hole].list if fit_pattern(pattern, word.word) and word.rank >= WORST_SIMILARITY]

            for answer in has_good_pattern:
                new_crossword = write_into(front.crossword, answer.word, crossword.hints[front.next_hole].position)
                queue.put(CrosswordInstance(front.rank - answer.rank, new_crossword, front.next_hole + 1))

    # TODO 
    # * alez to laguje (340k opcji i bez rozwiazania)
    # * przywroc sortowanie pozycji wg uwiklania