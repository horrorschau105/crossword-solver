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

def get_word_list(wordmap, ids, word_length, clue):
    """
    wordmap is a map int -> string
    ids is a list of ids
    word_length is a length of word to fit it into crossword
    """

    result_list = []
    clue = clue.split(' ')
    for (id, rank) in ids:
        word = wordmap[id][0]
        if len(word) == word_length and \
            word.lower() == word \
            and all(char not in word for char in ['.', ',', ':', '?', '/', '!']) \
            and word not in clue :
            
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

def get_fitting_words(crossword, model, method, freq_map, banned_words):
    fitting_words = []
    for hint in crossword.hints:
        clue = hint.clue.replace('.', '').replace(',', '').lower()
        length = hint.position.length
        sentence_vector = method(model, clue, freq_map, banned_words)
        fitting_words.append(
            get_fitting_words_for_single_clue(crossword, model, sentence_vector, length, clue))

    return fitting_words
    
def get_fitting_words_for_single_clue(crossword, model, sentence_vector, length, clue):
    return get_word_list(model.map, 
    find_nearest_words_ids_for_vector(model.matrix, model.fastText_model, sentence_vector), length,
    clue)
