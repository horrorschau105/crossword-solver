import numpy as np
from fastText import util
from Queue import PriorityQueue
from sys import argv, exit
from collections import namedtuple
from crossword_parser import get_crossword, VERTICAL, HORIZONTAL
from model_loader import get_model, normalize_vector
MAX_SOLUTIONS = 10
CrosswordInstance = namedtuple("CrosswordInstance", "rank crossword next_hole")
Answer = namedtuple("Answer", "word rank")

    

def find_nearest_words_ids_for_hint(all_vectors, model, text):
    """
    all_vectors is matrix with vectors
    model is loaded fastText model
    text is a sentence
    """

    hint_vector = normalize_vector(model.get_sentence_vector(text))

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
        if position.direction == VERTICAL:
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

if __name__ == "__main__":
    if len(argv) < 3:
        print "Usage: python main.py <model file> <crossword file>"
        print "eg. pythom main.py ../result/fil5.bin 5x5.crossword"
        exit(0)

    model_filename, crossword_filename = argv[1], argv[2]

    print "Loading model..."    
    
    model = get_model(model_filename)
    
    print "Parsing crossword..."
    
    crossword = get_crossword(crossword_filename)
    
    print 'Getting possible answers...'
    
    fitting_words_for_holes = []
    for i in range(len(crossword.hints)):
        clue = crossword.hints[i].clue
        position = crossword.hints[i].position
        fitting_words_for_holes.append(get_word_list(model.map, find_nearest_words_ids_for_hint(model.matrix, model.fastText_model, clue), position.length))

    # showing first 10 answers
    #for i in range(len(fitting_words_for_holes)):
    #    print holes[i].clue, ' '.join(ans.word for ans in fitting_words_for_holes[i][:10])

    solution_count = 0

    queue = PriorityQueue()
    queue.put(CrosswordInstance(0, crossword.grid, 0))

    print 'Solving crossword...'
    iterations = 0

    while not queue.empty():
        iterations += 1

        if iterations % 100 == 0:
            print iterations
        front = queue.get()

        if front.next_hole == len(crossword.hints):
            show_solution(front, crossword.hints)

            solution_count += 1
            if solution_count > MAX_SOLUTIONS:
                break
            
        else:
            pattern = get_pattern_from_crossword(front.crossword, crossword.hints[front.next_hole].position)

            has_good_pattern = [word for word in fitting_words_for_holes[front.next_hole] if fit_pattern(pattern, word.word)]

            for answer in has_good_pattern:
                new_crossword = write_into(front.crossword, answer.word, crossword.hints[front.next_hole].position)
                queue.put(CrosswordInstance(front.rank - answer.rank, new_crossword, front.next_hole + 1))