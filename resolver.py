import numpy as np
from model_loader import normalize_vector
from crossword_parser import VERTICAL
from collections import namedtuple
Answer = namedtuple("Answer", "word rank")

def find_nearest_words_ids_for_vector(all_vectors, model, vector):
    """
    all_vectors is matrix with vectors
    model is loaded fastText model
    vector is a sentence vector
    """

    hint_vector = normalize_vector(vector)

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

def get_fitting_words(crossword, model, method):
    fitting_words = []
    for hint in crossword.hints:
        clue = hint.clue
        length = hint.position.length
        sentence_vector = method(model, clue)
        fitting_words.append(
            get_fitting_words_for_single_clue(crossword, model, sentence_vector, length))
            

    return fitting_words
    
def get_fitting_words_for_single_clue(crossword, model, sentence_vector, length):
    return get_word_list(model.map, find_nearest_words_ids_for_vector(model.matrix, model.fastText_model, sentence_vector), length)
