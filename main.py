import fastText

def get_holes(grid, h, w):

    holes = {}
    for i in range(h):
        for j in range(w):
            #print i, '-', j
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

class Crossword:


    def __init__(self, number):
        print(number)

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

"""
Pomysl 1:
wez wszystkie slowa z hasla, ich wektory i ciupnij srednia (lub tf-idf), 
a nastepnie przeiteruj po istniejacych i wez najblizszy
Pomysl 2: Doc2Vec
Pomysl 3: ./fasttext print-sentence-vector
"""