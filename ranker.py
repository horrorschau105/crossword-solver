from crossword_parser import get_crossword
from model_loader import get_model, get_model_from_vector_list
from solution_importer import get_solution
from sys import argv, exit
from resolver import get_fitting_words_for_single_clue
from numpy import std, mean
from frequencies import get_frequencies
from numpy import log
top100 = []
freq_map = {}
def ban100(model, clue):
    global top100
    subwords = clue.split(' ')
    return sum(model.own_model[w] for w in subwords if w not in top100) / len(subwords)
    
def ban100_log_norm(model, clue):
    global top100, freq_map
    subwords = [w for w in clue.split(' ') if w not in top100]
    return sum(model.own_model[w] / log(freq_map[w]) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)
    
def freq_log_norm(model, clue):
    global freq_map
    subwords = clue.split(' ')
    return sum(model.own_model[w] / log(freq_map[w]) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def freq_log_square_norm(model, clue):
    global freq_map
    subwords = clue.split(' ')
    return sum(model.own_model[w] / (log(freq_map[w]) ** 2) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def ban100_freq_log_square_norm(model, clue):
    global freq_map, top100
    subwords = [w for w in clue.split(' ') if w not in top100]
    return sum(model.own_model[w] / (log(freq_map[w]) ** 2) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)

def freq_loglog_norm(model, clue):
    global freq_map
    subwords = clue.split(' ')
    return sum(model.own_model[w] / log(log(freq_map[w])) if w in freq_map else model.own_model[w] for w in subwords ) / len(subwords)
    
def average(model, clue):
    subwords = clue.split(' ')
    return sum(model.own_model[w] for w in subwords) / len(subwords)
        
def fastText_sentence_vector(model, clue):
    return model.fastText_model.get_sentence_vector(clue)

def get_position_of_word(wanted, words):
    idx = 1
    for word in words:
        if word.word == wanted:
            return (idx, word.rank)
        idx += 1
    return idx, 0

if __name__ == "__main__":
    if len(argv) < 3:
        print "Usage: python ranker.py <model> <puzzle_name>"
        exit(0)

    model = get_model_from_vector_list(argv[1])

    freq_map, top100 = get_frequencies(100)
    
    #model = get_model(argv[1])
    crossword = get_crossword(argv[2] + '.crossword', argv[2] + '.solution')
    print "Testing model:", argv[1]
    tested_methods = [
        #fastText_sentence_vector, 
        #average, 
        ban100_freq_log_square_norm,
        #ban100, 
        freq_log_norm, 
        #freq_log_square_norm,
        #freq_loglog_norm, 
        ban100_log_norm
        ]

    for method in tested_methods:
        print method.__name__
        precision = 0.0
        positions, ranks = [], []
        #print 'Expected\t\tFirst 5 answers'
        for hint in crossword.hints:
            sentence_vector = method(model, hint.clue)
            words = get_fitting_words_for_single_clue(crossword, model, sentence_vector, hint.position.length, hint.clue)
            result = get_position_of_word(hint.answer, words)
            print hint.clue, hint.position.length, hint.answer, result#, '\t', [(word.word, word.rank) for word in words[:5]]
            #print hint
            #print hint.answer, result, [word.word for word in words[:5]]
            positions.append(result[0])
            ranks.append(result[1])
            precision += 1.0 / result[0]
        #print
        precision /= len(crossword.hints)
        print 'Precision:', round(precision,3) ,'Avg position:', round(mean(positions), 3), "\tAvg rank:", round(mean(ranks), 10), 
        print

    # TODO
    # * przerobic importer by zarl liste vectorow, a nie binaria
    # * napisac inne metody liczenia sentence_vector
