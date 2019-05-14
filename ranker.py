from crossword_parser import get_crossword
from model_loader import get_model
from solution_importer import get_solution
from sys import argv, exit
from resolver import get_fitting_words_for_single_clue
from numpy import std, mean

def average(model, clue):
    subwords = clue.split(' ')
    return sum(model.fastText_model.get_word_vector(w) for w in subwords) / len(subwords)
        
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

    model = get_model(argv[1])
    crossword = get_crossword(argv[2] + '.crossword', argv[2] + '.solution')
    
    #fitting_words = get_fitting_words(crossword, model, model.fastText_model.get_sentence_vector)

    #for i in range(len(fitting_words)):
    #    print crossword.hints[i].clue, [w[0] for w in fitting_words[i]][:5]

    tested_methods = [fastText_sentence_vector, average]

    for method in tested_methods:
        print method.__name__
        positions, ranks = [], []
        for hint in crossword.hints:
            sentence_vector = method(model, hint.clue)
            words = get_fitting_words_for_single_clue(crossword, model, sentence_vector, hint.position.length)
            result = get_position_of_word(hint.answer, words)

            positions.append(result[0])
            ranks.append(result[1])

        print 'Avg position:', round(mean(positions), 3), "st. dev.:", round(std(positions),3), "\tAvg rank:", round(mean(ranks), 3), "std:", round(std(ranks), 3)

    # TODO
    # * zaimportowac liste czestosci slow
    # * przerobic importer by zarl liste vectorow, a nie binaria
    # * napisac inne metody liczenia sentence_vector
