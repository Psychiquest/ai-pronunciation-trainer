import WordMetrics
from ortools.sat.python import cp_model
import numpy as np
from string import punctuation
from dtwalign import dtw_from_distance_matrix
import time

offset_blank = 1
TIME_THRESHOLD_MAPPING = 5.0

import string

# Function to calculate phoneme-based pronunciation accuracy
def calculate_pronunciation_accuracy_with_diff(real_and_transcribed_words_ipa):
    # Convert words to phonetic transcriptions
    target_phonemes = " ".join([item[0] for item in real_and_transcribed_words_ipa])
    spoken_phonemes = " ".join([item[1] for item in real_and_transcribed_words_ipa])

    # Get the diff result using Myers algorithm for phonemes
    diff_result = myers_diff_phonemes(target_phonemes, spoken_phonemes)

    match_count = 0
    penalty_count = 0
    clean_index = 1

    incorrect_words = 0
    is_current_word_incorrect = False

    total_words = len(target_phonemes.split(" "))

    for char in target_phonemes:   

        while clean_index < len(diff_result) and char == ' ' and diff_result[clean_index][1] != ' ':
            penalty_count += 1

            if clean_index < len(diff_result)-1 and diff_result[clean_index][0] == "DELETE" and diff_result[clean_index+1][0] == "INSERT":
                clean_index += 1

            clean_index += 1
   
        # Remove spaces from diff_result
        while clean_index < len(diff_result) and  diff_result[clean_index][1] == ' ':
            clean_index +=1
              
        # Check if current character is a space which means a new word
        if char == ' ':
            is_current_word_incorrect = False 

        # Check if current character is a punctuation, so just ignore it
        elif char in string.punctuation:
            pass # can be changed to match_string.append('1')
            clean_index += 1

        # Check if current character is a match
        elif clean_index < len(diff_result) and diff_result[clean_index][0] == 'MATCH':
            match_count += 1
            clean_index += 1

        # Check if current character is something else, and if it's not marked as incorrect word, mark it as incorrect
        else:
            if not is_current_word_incorrect:
                incorrect_words += 1
                is_current_word_incorrect = True

            if clean_index < len(diff_result)-1 and diff_result[clean_index][0] == "DELETE" and diff_result[clean_index+1][0] == "INSERT":
                clean_index+=1

            penalty_count += 1
            clean_index += 1

    accuracy = match_count*100 / (match_count+ penalty_count)
    return accuracy, incorrect_words, total_words


# Myers Diff Algorithm (adapted for phonemes)
def myers_diff_phonemes(a, b):
    n, m = len(a), len(b)
    max_d = n + m
    v = [0] * (2 * max_d + 1)
    trace = []

    for d in range(max_d + 1):
        trace.append(list(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1 + max_d] < v[k + 1 + max_d]):
                x = v[k + 1 + max_d]
            else:
                x = v[k - 1 + max_d] + 1

            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k + max_d] = x

            if x >= n and y >= m:
                return backtrack(trace, a, b, n, m)

    return []


# Myers Diff Algorithm
def myers_diff(a, b):
    n, m = len(a), len(b)
    max_d = n + m
    v = [0] * (2 * max_d + 1)
    trace = []

    for d in range(max_d + 1):
        trace.append(list(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1 + max_d] < v[k + 1 + max_d]):
                x = v[k + 1 + max_d]
            else:
                x = v[k - 1 + max_d] + 1

            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k + max_d] = x

            if x >= n and y >= m:
                return backtrack(trace, a, b, n, m)

    return []

# Backtrack to determine matched and unmatched characters
def backtrack(trace, a, b, n, m):
    d = len(trace) - 1
    x, y = n, m
    result = []

    while d >= 0:
        v = trace[d]
        k = x - y
        max_d = len(v) // 2

        if k == -d or (k != d and v[k - 1 + max_d] < v[k + 1 + max_d]):
            prev_k = k + 1
        else:
            prev_k = k - 1

        prev_x = v[prev_k + max_d]
        prev_y = prev_x - prev_k

        while x > prev_x and y > prev_y:
            result.append(('MATCH', a[x - 1]))
            x -= 1
            y -= 1

        if x == prev_x:
            result.append(('INSERT', b[y - 1]))
            y -= 1
        elif y == prev_y:
            result.append(('DELETE', a[x - 1]))
            x -= 1

        d -= 1

    result.reverse()
    return result

# Function to generate a "0" or "1" string based on matches
def generate_match_string(a, b):
    # Remove punctuations
    a_clean = a
    b_clean = b

    # Get the diff result
    diff_result = myers_diff(a_clean, b_clean)
    
    match_string = []
    clean_index = 1

    for char in a:

        while clean_index < len(diff_result) and char == ' ' and diff_result[clean_index][1] != ' ':

            if clean_index < len(diff_result)-1 and diff_result[clean_index][0] == "DELETE" and diff_result[clean_index+1][0] == "INSERT":
                clean_index+=1

            clean_index += 1
        
        while clean_index < len(diff_result) and  diff_result[clean_index][1] == ' ':
            clean_index +=1
              
        if char == ' ':
            match_string.append(' ')
        elif char in string.punctuation:
            match_string.append('1')
            clean_index += 1
        elif clean_index < len(diff_result) and diff_result[clean_index][0] == 'MATCH':
            match_string.append('1')
            clean_index += 1
        else:
            if clean_index < len(diff_result)-1 and diff_result[clean_index][0] == "DELETE" and diff_result[clean_index+1][0] == "INSERT":
                clean_index+=1
            match_string.append('0')

            clean_index += 1

    return ''.join(match_string)


def get_word_distance_matrix(words_estimated: list, words_real: list) -> np.array:
    number_of_real_words = len(words_real)
    number_of_estimated_words = len(words_estimated)

    word_distance_matrix = np.zeros(
        (number_of_estimated_words+offset_blank, number_of_real_words))
    for idx_estimated in range(number_of_estimated_words):
        for idx_real in range(number_of_real_words):
            word_distance_matrix[idx_estimated, idx_real] = WordMetrics.edit_distance_python(
                words_estimated[idx_estimated], words_real[idx_real])

    if offset_blank == 1:
        for idx_real in range(number_of_real_words):
            word_distance_matrix[number_of_estimated_words,
                                 idx_real] = len(words_real[idx_real])
    return word_distance_matrix


def get_best_path_from_distance_matrix(word_distance_matrix):
    modelCpp = cp_model.CpModel()

    number_of_real_words = word_distance_matrix.shape[1]
    number_of_estimated_words = word_distance_matrix.shape[0]-1

    number_words = np.maximum(number_of_real_words, number_of_estimated_words)

    estimated_words_order = [modelCpp.NewIntVar(0, int(
        number_words - 1 + offset_blank), 'w%i' % i) for i in range(number_words+offset_blank)]

    # They are in ascending order
    for word_idx in range(number_words-1):
        modelCpp.Add(
            estimated_words_order[word_idx+1] >= estimated_words_order[word_idx])

    total_phoneme_distance = 0
    real_word_at_time = {}
    for idx_estimated in range(number_of_estimated_words):
        for idx_real in range(number_of_real_words):
            real_word_at_time[idx_estimated, idx_real] = modelCpp.NewBoolVar(
                'real_word_at_time'+str(idx_real)+'-'+str(idx_estimated))
            modelCpp.Add(estimated_words_order[idx_estimated] == idx_real).OnlyEnforceIf(
                real_word_at_time[idx_estimated, idx_real])
            total_phoneme_distance += word_distance_matrix[idx_estimated,
                                                           idx_real]*real_word_at_time[idx_estimated, idx_real]

    # If no word in time, difference is calculated from empty string
    for idx_real in range(number_of_real_words):
        word_has_a_match = modelCpp.NewBoolVar(
            'word_has_a_match'+str(idx_real))
        modelCpp.Add(sum([real_word_at_time[idx_estimated, idx_real] for idx_estimated in range(
            number_of_estimated_words)]) == 1).OnlyEnforceIf(word_has_a_match)
        total_phoneme_distance += word_distance_matrix[number_of_estimated_words,
                                                       idx_real]*word_has_a_match.Not()

    # Loss should be minimized
    modelCpp.Minimize(total_phoneme_distance)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_THRESHOLD_MAPPING
    status = solver.Solve(modelCpp)

    mapped_indices = []
    try:
        for word_idx in range(number_words):
            mapped_indices.append(
                (solver.Value(estimated_words_order[word_idx])))

        return np.array(mapped_indices, dtype=int)
    except:
        return []


def get_resulting_string(mapped_indices: np.array, words_estimated: list, words_real: list) -> list:
    mapped_words = []
    mapped_words_indices = []
    WORD_NOT_FOUND_TOKEN = '-'
    number_of_real_words = len(words_real)
    for word_idx in range(number_of_real_words):
        position_of_real_word_indices = np.where(
            mapped_indices == word_idx)[0].astype(int)

        if len(position_of_real_word_indices) == 0:
            mapped_words.append(WORD_NOT_FOUND_TOKEN)
            mapped_words_indices.append(-1)
            continue

        if len(position_of_real_word_indices) == 1:
            mapped_words.append(
                words_estimated[position_of_real_word_indices[0]])
            mapped_words_indices.append(position_of_real_word_indices[0])
            continue
        # Check which index gives the lowest error
        if len(position_of_real_word_indices) > 1:
            error = 99999
            best_possible_combination = ''
            best_possible_idx = -1
            for single_word_idx in position_of_real_word_indices:
                idx_above_word = single_word_idx >= len(words_estimated)
                if idx_above_word:
                    continue
                error_word = WordMetrics.edit_distance_python(
                    words_estimated[single_word_idx], words_real[word_idx])
                if error_word < error:
                    error = error_word*1
                    best_possible_combination = words_estimated[single_word_idx]
                    best_possible_idx = single_word_idx

            mapped_words.append(best_possible_combination)
            mapped_words_indices.append(best_possible_idx)
            continue

    return mapped_words, mapped_words_indices


def get_best_mapped_words(words_estimated: list, words_real: list) -> list:

    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)

    start = time.time()
    mapped_indices = get_best_path_from_distance_matrix(word_distance_matrix)

    duration_of_mapping = time.time()-start
    # In case or-tools doesn't converge, go to a faster, low-quality solution
    if len(mapped_indices) == 0 or duration_of_mapping > TIME_THRESHOLD_MAPPING+0.5:
        mapped_indices = (dtw_from_distance_matrix(
            word_distance_matrix)).path[:len(words_estimated), 1]

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)

    return mapped_words, mapped_words_indices


# Faster, but not optimal
def get_best_mapped_words_dtw(words_estimated: list, words_real: list) -> list:

    from dtwalign import dtw_from_distance_matrix
    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)
    mapped_indices = dtw_from_distance_matrix(
        word_distance_matrix).path[:-1, 0]

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)
    return mapped_words, mapped_words_indices


def getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word):
    is_leter_correct = [None]*len(real_word)
    for idx, letter in enumerate(real_word):
        if letter == transcribed_word[idx] or letter in punctuation:
            is_leter_correct[idx] = 1
        else:
            is_leter_correct[idx] = 0
    return is_leter_correct


def parseLetterErrorsToHTML(word_real, is_leter_correct):
    word_colored = ''
    correct_color_start = '*'
    correct_color_end = '*'
    wrong_color_start = '-'
    wrong_color_end = '-'
    for idx, letter in enumerate(word_real):
        if is_leter_correct[idx] == 1:
            word_colored += correct_color_start + letter+correct_color_end
        else:
            word_colored += wrong_color_start + letter+wrong_color_end
    return word_colored
