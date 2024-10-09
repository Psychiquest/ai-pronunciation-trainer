import numpy as np

# ref from https://gitlab.com/-/snippets/1948157
# For some variants, look here https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python

# Pure python
def edit_distance_python2(a, b):
    # This version is commutative, so as an optimization we force |a|>=|b|
    if len(a) < len(b):
        return edit_distance_python(b, a)
    if len(b) == 0:  # Can deal with empty sequences faster
        return len(a)
    # Only two rows are really needed: the one currently filled in, and the previous
    distances = []
    distances.append([i for i in range(len(b)+1)])
    distances.append([0 for _ in range(len(b)+1)])
    # We can prefill the first row:
    costs = [0 for _ in range(3)]
    for i, a_token in enumerate(a, start=1):
        distances[1][0] += 1  # Deals with the first column.
        for j, b_token in enumerate(b, start=1):
            costs[0] = distances[1][j-1] + 1
            costs[1] = distances[0][j] + 1
            costs[2] = distances[0][j-1] + (0 if a_token == b_token else 1)
            distances[1][j] = min(costs)
        # Move to the next row:
        distances[0][:] = distances[1][:]
    return distances[1][len(b)]

#https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def edit_distance_python(seq1, seq2):
    # Ensure seq1 is the longer sequence for optimization
    if len(seq1) < len(seq2):
        return edit_distance_python(seq2, seq1)

    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    
    # Use a single row to save memory
    previous_row = range(size_y)
    for x in range(1, size_x):
        current_row = [x] + [0] * (size_y - 1)
        for y in range(1, size_y):
            insert = previous_row[y] + 1
            delete = current_row[y-1] + 1
            substitute = previous_row[y-1] + (seq1[x-1] != seq2[y-1])
            current_row[y] = min(insert, delete, substitute)
        previous_row = current_row

    return previous_row[-1]