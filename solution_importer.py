from collections import namedtuple
Solution = namedtuple("Solution", "horizontal vertical")
def get_solution(filename):
    v = ""
    answers = []
    with open(filename) as f:
        lines = f.readlines()
        v, answers = lines[0], lines[1:]

    v = int(v.split(' ')[0])
    return Solution([w[:-1] for w in answers[:v]], [w[:-1] for w in answers[v:]]) 
