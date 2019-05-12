import numpy as np
import fastText
from math import sqrt
from collections import namedtuple
Model = namedtuple("Model", "map matrix fastText_model")


def normalize_vector(vector):
    """
    Return L2-normalized vector
    """
    norm = sum(value * value for value in vector)
    return vector / sqrt(norm)

def get_model(filename):

    model = fastText.load_model(filename)

    wordmap = {}
    index = 0
    vectors = []
    for w in model.get_words():
        v = normalize_vector(model.get_word_vector(w))
        wordmap[index] = (w, v)
        vectors.append(v)
        index += 1

    matrix_of_words = np.array(vectors)

    return Model(wordmap, matrix_of_words, model)
