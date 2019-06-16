from numpy import float32
def get_frequencies(filename, k):
    lines = ""
    with open(filename) as f:
        lines = [line[:-1].replace(' ', '').split('\t') for line in f.readlines() ]

    freqs, banned = {}, []
    idx = 0
    for row in lines:
        word, freq = row[1], float32(row[2])
        if idx < k:
            banned.append(word)
        idx += 1
        freqs[word] = freq

    return freqs, banned
