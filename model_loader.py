import numpy as np
import fastText
from math import sqrt
from collections import namedtuple
import pickle
from os.path import isfile
Model = namedtuple("Model", "map matrix fastText_model own_model")


def normalize_vector(vector):
    """
    Return L2-normalized vector
    """
    norm = sum(value * value for value in vector)
    return vector / sqrt(norm)

def get_model(filename):

    pickled_filename = filename.replace('.vec', '.po')
    if isfile(pickled_filename):
        with open(pickled_filename,'rb') as f:
            return pickle.load(f)
    
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

    model = Model(wordmap, matrix_of_words, model, [])

    print 'Model pickled to:', pickled_filename
    with open(pickled_filename, 'wb') as f:
        pickle.dump(model, f)

    return model

def get_model_from_vector_list(filename):
    filename.replace('.bin', '.vec')

    pickled_filename = filename.replace('.vec', '.po')
    if isfile(pickled_filename):
        with open(pickled_filename,'rb') as f:
            return pickle.load(f)
    
    lines = ""
    with open(filename) as f:
        lines = [l[:-1] for l in f.readlines()]
    
    all_vectors = lines[1:]
    vectors, wordmap = [], {}
    model = {}
    idx = 0
    for line in all_vectors:
        values = line.split(' ')
        word, values = values[0], map(np.float32, values[1:-1])
        v = normalize_vector(np.array(values))
        wordmap[idx] = (word, v)
        vectors.append(v)
        model[word] = v
        idx += 1
        
    model = Model(wordmap, np.array(vectors), [], model)
    
    print 'Model pickled to:', pickled_filename
    with open(pickled_filename, 'wb') as f:
        pickle.dump(model, f)

    return model
    