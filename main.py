import fastText
from fastText import util
import numpy as np

def get_holes(grid, h, w):

    holes = {}
    for i in range(h):
        for j in range(w):
            if (i == 0 or grid[i-1][j] == '#') and grid[i][j] == '.' :
                length = 0
                index = i
                while index < h and grid[index][j] == '.':
                    length += 1
                    index += 1
                if length > 1:
                    holes[(i,j, 'vertical')] = length
            if (j == 0 or grid[i][j-1] == '#') and grid[i][j] == '.' :
                length = 0
                index = j
                while index < w and grid[i][index] == '.':
                    length += 1
                    index += 1
                if length > 1:
                    holes[(i,j, 'horizontal')] = length
    return holes

def find_nearest_words_ids_for_hint(model, text):
    """
    model is loaded fastText model
    text is a sentence
    """

    hint_vector = model.get_sentence_vector(text)
    all_vectors = model.get_output_matrix()

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
    for id in ids:
        if len(wordmap[id][0]) == word_length:
            result_list.append(wordmap[id][0])

    return result_list

if __name__ == "__main__":
    lines = ""
    with open("input.txt") as file_input:
        lines = [line[:-1] for line in file_input.readlines()]
    test_cases, input = int(lines[0]), lines[1:]
    for i in range(test_cases):
        h, w = [int(n) for n in input[0].split(' ')]
        input = input[1:]
        grid, input = input[:h], input[h:]
        hhc, input = int(input[0]), input[1:] # horizontal hints and count
        hh, input = input[:hhc], input[hhc:]
        vhc, vh = int(input[0]), input[1:] # vertical hints and count

        holes = get_holes(grid, h, w)
        if len([key for key in holes if key[2] == 'vertical']) != vhc or len([key for key in holes if key[2] == 'horizontal']) != hhc:
            print "Cos jest nie tak z krzyzowka"

    print "Loading model..."
    
    f = fastText.load_model("../result/fil1.bin")

    wordmap = {}
    index = 0
    for w in f.get_words():
        wordmap[index] = (w, f.get_word_vector(w))
        index += 1
    result_vector = find_nearest_words_ids_for_hint(f, "Sneezy, Grumpy or Happy")

    word_list = get_word_list(wordmap, [i[0] for i in result_vector], 5)

# okej, no to trzeba wypalic siec w takim razie

# solver ---> TBD

