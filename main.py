if __name__ == "__main__":
    lines = ""
    with open("input.txt") as file_input:
        lines = [line[:-1] for line in file_input.readlines()]
    test_cases, input = int(lines[0]), lines[1:]
    for case in range(test_cases):
        grid_height, grid_width, horizontal_hints_count, vertical_hints_count = [int(n) for n in input[0].split(' ')]
        # tbd

    
