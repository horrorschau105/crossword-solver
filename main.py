import numpy as np
from fastText import util
from Queue import PriorityQueue
from sys import argv, exit
from collections import namedtuple
from crossword_parser import get_crossword, VERTICAL, HORIZONTAL
from model_loader import get_model, normalize_vector, get_model_from_vector_list
from resolver import get_fitting_words, fit_pattern
from frequencies import get_frequencies
import time
CrosswordInstance = namedtuple("CrosswordInstance", "rating crossword depth word_ranks")
HoleWithWords = namedtuple("HoleWithWords", "position words clue")

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
    print 'Used words: '
    for hole in holes:
        print hole.clue, get_pattern_from_crossword(crossword_instance.crossword, hole.position)

    print 'Overall rank: ', sum(crossword_instance.word_ranks) / len(crossword_instance.word_ranks)

def ban100_log_norm(model, clue, freq_map, top100):
    words = [w for w in clue.lower().replace('.', '').replace(',', '').split(' ') if w != ' ']
    subwords = [w for w in words if w not in top100 and w in model.own_model]
    return sum(model.own_model[w] / np.log(freq_map[w]) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def get_hash(grid):
    return hash(''.join(grid))

def match_words_to_holes(crossword, model, method, freq_map, top100):
    words = get_fitting_words(crossword, model, method, freq_map, top100)
    result = []
    for index in range(len(crossword.hints)):
        result.append(HoleWithWords(crossword.hints[index].position, words[index], crossword.hints[index].clue))
    return result

def get_entanglement_value(fixed_hole, holes):
    crossings = 0
    position = fixed_hole.position
    fixed_cells = { (position.x + idx, position.y) for idx in range(position.length) } if fixed_hole.position.direction == VERTICAL \
        else { (position.x, position.y + idx) for idx in range(position.length) }

    for hole in holes:
        for index in range(hole.position.length):
            if hole.position.direction == VERTICAL:
                if (hole.position.x + index, hole.position.y) in fixed_cells:
                    crossings += 1
                    break
            else:
                if (hole.position.x, hole.position.y + index) in fixed_cells:
                    crossings += 1
                    break

    return (crossings, sum(w.rank for w in fixed_hole.words[:5]))

def get_most_entangled_word(source, network):
    best_rank = (0, 0)
    best_hole = None
    for hole in source:
        hole_rank = get_entanglement_value(hole, network)
        if hole_rank > best_rank:
            best_rank = hole_rank
            best_hole = hole
    return best_hole

def order_holes(holes):
    first_hole = get_most_entangled_word(holes, holes)
    result = [first_hole]
    holes.remove(first_hole)

    while len(holes) > 0:
        next_hole = get_most_entangled_word(holes, result)
        result.append(next_hole)
        holes.remove(next_hole)

    return result

def get_rating(crossword, depth, word_ranks):
    ranks_sum = sum(val * val for val in word_ranks)
    return 15 - ranks_sum - 10 * min(word_ranks + [1]) # poki co kwadrat dziala calkiem spoko

if __name__ == "__main__":
    if len(argv) < 3:
        print "Usage: python main.py <vector file> <crossword file>"
        print "eg. pythom main.py fil5.vec 5x5.crossword"
        exit(0)

    model_filename, crossword_filename = argv[1], argv[2]

    print "Loading model..."    
    
    model = get_model_from_vector_list(model_filename)
    
    print "Parsing crossword..."

    crossword = get_crossword(crossword_filename)

    print "Importing word frequences..."

    freq_map, top100 = get_frequencies(100)
    
    print 'Getting possible answers...'
    
    fitting_words_for_holes = order_holes( match_words_to_holes(crossword, model, ban100_log_norm, freq_map, top100))

    #MAX_WORDS_PER_HINT = 200
    #fitting_words = [l.words[:MAX_WORDS_PER_HINT] for l in fitting_words_for_holes]
    WORST_SIMILARITY = 0.4
    fitting_words = [[word for word in l.words if word.rank >= WORST_SIMILARITY] for l in fitting_words_for_holes]

    print 'Solving crossword...'
    queue = PriorityQueue()
    empty_crossword = CrosswordInstance(get_rating(crossword.grid, 0, []), crossword.grid, 0, [])
    queue.put(empty_crossword)
    #MAX_SOLUTIONS = 1000
    MAX_ITERATIONS_WITHOUT_BETTER_SOLUTION = 20000
    last_iteration_with_solution = 0
    solution_count = 0
    best_rank = 0
    best_crossword = None
    iterations = 0
    best_crossword_value = 0
    while queue.qsize() > 0:
        front = queue.get()
        
        iterations += 1
        if iterations % 1000 == 0:
            print iterations, front.rating, queue.qsize(), solution_count, best_crossword_value
        
        if front.depth == len(crossword.hints):
            rank = sum(front.word_ranks)
            if rank > best_rank:
                best_rank = rank
                best_crossword = front
                best_crossword_value = sum(front.word_ranks) / len(front.word_ranks)
                print 'Found better solution:', best_crossword_value, 'in iteration:', iterations
                last_iteration_with_solution = iterations

            solution_count += 1
            if best_crossword_value > 0 and last_iteration_with_solution + MAX_ITERATIONS_WITHOUT_BETTER_SOLUTION < iterations:
                break
        else:
            index = front.depth
            pattern = get_pattern_from_crossword(front.crossword, fitting_words_for_holes[index].position)
            has_good_pattern = [word for word in fitting_words[index] if fit_pattern(pattern, word.word)]
            for answer in has_good_pattern:
                new_crossword = write_into(front.crossword, answer.word, fitting_words_for_holes[index].position)
                rating = get_rating(new_crossword, front.depth + 1, front.word_ranks + [answer.rank])
                queue.put(CrosswordInstance(rating, new_crossword, front.depth + 1, front.word_ranks + [answer.rank]))
    print 'Total iterations', iterations
    show_solution(best_crossword, fitting_words_for_holes)

    # w jaki sposob konczyc przeszukiwanie? 10000 rozwiazan bez poprawy?