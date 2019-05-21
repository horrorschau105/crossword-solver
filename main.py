import numpy as np
from fastText import util
from Queue import PriorityQueue
from sys import argv, exit
from collections import namedtuple
from crossword_parser import get_crossword, VERTICAL, HORIZONTAL
from model_loader import get_model, normalize_vector, get_model_from_vector_list
from resolver import get_fitting_words, fit_pattern
from frequencies import get_frequencies
CrosswordInstance = namedtuple("CrosswordInstance", "rating crossword depth word_ranks")
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
    print 'Used words: '
    for hole in holes:
        print hole.clue, '\t', get_pattern_from_crossword(crossword_instance.crossword, hole.position)

    print 'Overall rank: ', sum(crossword_instance.word_ranks) / len(crossword_instance.word_ranks)

def ban100_log_norm(model, clue):
    global top100, freq_map
    subwords = [w for w in clue.split(' ') if w not in top100 and w in model.own_model]
    #subwords = [w for w in clue.split(' ') if w not in top100]
    return sum(model.own_model[w] / np.log(freq_map[w]) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def get_rating(crossword, depth, word_ranks):

    empties = sum(sum(1 for char in line if char == '.') for line in crossword)
    ranks_sum = sum(val * val for val in word_ranks) # bad words are bad
    #print empties, depth, word_ranks
    #return 10 * empties - 30 * ranks_sum - 2 * depth
    return empties - 3 * ranks_sum# - 2 * depth

def get_hash(grid):
    return hash(''.join(grid))

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
    
    MAX_WORDS_PER_HINT = 30
    fitting_words = [l[:MAX_WORDS_PER_HINT] for l in get_fitting_words(crossword, model, ban100_log_norm)]
    #WORST_SIMILARITY = 0.5
    #fitting_words = [[word for word in l if word.rank >= WORST_SIMILARITY] for l in get_fitting_words(crossword, model, ban100_log_norm) ]
    
    print 'all words count:', sum(len(l) for l in fitting_words) # ile tego jest
    solution_count = 0

    queue = PriorityQueue()
    empty_crossword = CrosswordInstance(get_rating(crossword.grid, 0, []), crossword.grid, 0, [])

    queue.put(empty_crossword)

    print 'Solving crossword...'
    MAX_SOLUTIONS = 100
    best_rank = 0
    best_crossword = None
    iterations = 0
    history = { get_hash(crossword.grid) }
    while queue.qsize() > 0:
        front = queue.get()

        iterations += 1
        if iterations % 1000 == 0:
            print iterations, front.rating, solution_count
        
        if front.depth == len(crossword.hints):
            #show_solution(front, crossword.hints)
            rank = sum(front.word_ranks)
            #print rank, best_rank
            if rank > best_rank:
                best_rank = rank
                best_crossword = front

            solution_count += 1
            if solution_count > MAX_SOLUTIONS:
                show_solution(best_crossword, crossword.hints)
                break
        else:
            """index = front.depth
            pattern = get_pattern_from_crossword(front.crossword, crossword.hints[index].position)
            has_good_pattern = [word for word in fitting_words[index] if fit_pattern(pattern, word.word)]
            for answer in has_good_pattern:
                new_crossword = write_into(front.crossword, answer.word, crossword.hints[index].position)
                rating = get_rating(new_crossword, front.depth + 1, front.word_ranks + [answer.rank])
                queue.put(CrosswordInstance(rating, new_crossword, front.depth + 1, front.word_ranks + [answer.rank]))
            """
            for index in range(len(fitting_words)):
                pattern = get_pattern_from_crossword(front.crossword, crossword.hints[index].position)

                if '.' in pattern:
                    has_good_pattern = [word for word in fitting_words[index] if fit_pattern(pattern, word.word)]
                    for answer in has_good_pattern:
                        new_crossword = write_into(front.crossword, answer.word, crossword.hints[index].position)

                        h = get_hash(new_crossword)
                        if h not in history:
                            history.add(h)
                            rating = get_rating(new_crossword, front.depth + 1, front.word_ranks + [answer.rank])
                            queue.put(CrosswordInstance(rating, new_crossword, front.depth + 1, front.word_ranks + [answer.rank]))
            

    """
    O skurwesyn, ale to idzie
    Spawac heure, musi byc dobra
    Posortowac dobrze dziury!
    """