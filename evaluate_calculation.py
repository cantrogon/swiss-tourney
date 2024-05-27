from itertools import combinations

import numpy as np
from scipy import stats
from tqdm import tqdm
from score_calculation import calculate_scores_from_matrix
from pairings import get_pairings_lp
import matplotlib.pyplot as plt

np.random.seed(42)


def compare_order(array1, array2):
    # Check if both arrays have the same length
    if len(array1) != len(array2):
        return False

    # Get the ranks of elements in both arrays
    ranks1 = np.argsort(np.argsort(array1))
    ranks2 = np.argsort(np.argsort(array2))

    # Check if the rank arrays are identical
    return np.array_equal(ranks1, ranks2), ranks1, ranks2


def measure_order_correlation(list1, list2):
    # Convert lists to numpy arrays for compatibility with scipy functions
    array1 = np.array(list1)
    array2 = np.array(list2)

    # Calculate Spearman's rank correlation coefficient
    correlation, p_value = stats.spearmanr(array1, array2)

    return correlation  # Returns the correlation coefficient


def get_win_perc(strength1, strength2):
    # assume strength range is 0-1
    # p = ((strength1 - strength2) / 2 + 0.5)
    p = strength1 / (strength1 + strength2)
    return p


def get_matrix_from_strengths(strength_list):
    n = len(strength_list)
    result_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result_matrix[i, j] = get_win_perc(strength_list[i], strength_list[j])
    return result_matrix


def randomly_fill_elements(matrix, fraction=0.5, fill_value=0):
    size = matrix.shape[0]
    flat_indices = np.random.choice(size * size, int(size * size * fraction), replace=False)
    i, j = np.unravel_index(flat_indices, matrix.shape)
    matrix[i, j] = fill_value
    matrix[j, i] = fill_value
    return matrix


def mutate_matrix(matrix):
    m = np.copy(matrix)
    randomly_fill_elements(m, fraction=0.7, fill_value=0.5)
    np.fill_diagonal(m, 0.5)
    return m


# player_strength = [1.0, 0.7, .64, .50, .40, .05]
# result_matrix = get_matrix_from_strengths(player_strength)
# print(result_matrix)

# mutated_matrix = mutate_matrix(result_matrix)
# print(mutated_matrix)

# calc_scores = calculate_scores_from_matrix(mutated_matrix)

# print(calc_scores)
# print("Ranking is correct:", compare_order(player_strength, calc_scores))


def run_test_removal(test_n, matrix_size):
    correct_list = []
    correlation_list = []
    for _ in tqdm(range(test_n)):
        source_strengths = np.random.rand(matrix_size)
        source_matrix = get_matrix_from_strengths(source_strengths)
        mutated_matrix = mutate_matrix(source_matrix)
        calc_scores = calculate_scores_from_matrix(mutated_matrix)
        is_correct = compare_order(source_strengths, calc_scores)[0]
        # print(is_correct)
        correct_list.append(is_correct)
        # print(calc_scores)
        order_correlation = measure_order_correlation(source_strengths, calc_scores)
        if not np.isnan(order_correlation): correlation_list.append(order_correlation)
    print(f"Number correct: {sum(correct_list)} / {test_n}")
    print(f"Average correlation: {len(correlation_list) and sum(correlation_list) / len(correlation_list)}")


# run_test_removal(100, 6)


def get_pairings_random(n):
    numbers = list(range(0, n))  # different from main code
    np.random.shuffle(numbers)
    pairings = [(numbers[i], numbers[i + 1]) for i in range(0, len(numbers) - 1, 2)]
    if n % 2 != 0:
        pairings.append((numbers[-1],))
    return pairings


def get_pairings_chain(initial_pairings, initial_outcomes):
    n = len(initial_pairings)
    new_pairings = [[] for _ in range(n)]
    for i, (pair, outcome) in enumerate(zip(initial_pairings, initial_outcomes)):
        winner = 0 if outcome[0] > outcome[1] else 1
        loser = winner * -1 + 1
        if i % 2 == 0:
            new_pairings[(i + 1) % n].append(pair[winner])
            new_pairings[i % n].append(pair[loser])
        else:
            new_pairings[i % n].append(pair[winner])
            new_pairings[(i + 1) % n].append(pair[loser])
    # for pair in new_pairings:
    # np.random.shuffle(pair)
    return new_pairings


def do_round(matrix, pairings, strength_list):
    outcomes = []
    for p1, p2 in pairings:
        outcome = simulate_match(strength_list[p1], strength_list[p2])
        matrix[p1, p2] += outcome[0]
        matrix[p2, p1] += outcome[1]
        outcomes.append(outcome)
    return matrix, outcomes


def simulate_match(strength1, strength2):
    perc_1 = get_win_perc(strength1, strength2)
    perc_2 = 1 - perc_1
    # probabilities of 2-0, 2-1, 1-2 and 0-2
    probabilities = [perc_1 ** 2, 2 * perc_1 ** 2 * perc_2, 2 * perc_1 * perc_2 ** 2, perc_2 ** 2]
    outcomes = [(2, 0), (2, 1), (1, 2), (0, 2)]
    return outcomes[np.random.choice(range(len(outcomes)), p=probabilities)]


def mean_and_confint(values, confidence=0.95):
    filtered_values = np.array([value for value in values if value is not None])
    mean_value = np.mean(filtered_values)

    # Calculate the confidence interval
    sem = stats.sem(filtered_values)  # Standard error of the mean
    n = len(filtered_values)
    h = sem * stats.t.ppf((1 + confidence) / 2., n - 1)  # t-critical value * standard error
    conf_interval = (mean_value - h, mean_value + h)

    return mean_value, conf_interval


def run_test_rounds(matrix_size, max_iter=1000):
    player_strengths = np.random.rand(matrix_size)
    new_matrix = np.zeros((len(player_strengths), len(player_strengths)))

    for i in range(max_iter):
        if i != 1:
            pairings = get_pairings_random(matrix_size)
        else:
            pairings = get_pairings_chain(pairings, outcomes)
        _, outcomes = do_round(new_matrix, pairings, player_strengths)
        calc_scores = calculate_scores_from_matrix(new_matrix)
        is_correct = compare_order(player_strengths, calc_scores)[0]
        if (is_correct):
            return i + 1
    if (i == max_iter - 1):
        return None


def run_test_rounds_many(matrix_size, n_iter, max_round_iter=1000):
    successes = []
    for _ in tqdm(range(n_iter)):
        success = run_test_rounds(matrix_size, max_round_iter)
        successes.append(success)
    print(successes)
    max_threshold = max_round_iter * 1.5  # if not found after max_iter, use this as estimate
    print("None count:", f"{len([_ for s in successes if s is None])} / {len(successes)}")
    successes = [max_threshold if s is None else s for s in successes]
    print(mean_and_confint(successes))


# player_strength = [1.0, 0.7, .64, .50, .40, .05]


# run_test_rounds_many(6, 1000, 1000)

def current_calculation(matrix):
    player_count = matrix.shape[0]
    p = np.zeros(player_count)

    for i in range(player_count - 1):
        for j in range(i + 1, player_count):
            if matrix[i, j] > matrix[j, i]:
                p[i] += 1
    return p


def run_test_rounds_n_correlation(matrix_size, rounds=3, scoring_function=calculate_scores_from_matrix):
    player_strengths = np.random.rand(matrix_size)
    player_strengths = player_strengths / np.linalg.norm(player_strengths)
    new_matrix = np.zeros((len(player_strengths), len(player_strengths)))

    for i in range(rounds):
        if i == 0:
            pairings = get_pairings_random(matrix_size)
        elif i == 1:
            pairings = get_pairings_chain(pairings, outcomes)
        else:
            pairings = get_pairings_lp(calc_scores, new_matrix)
        # pairings = get_pairings_chain(pairings, outcomes)

        _, outcomes = do_round(new_matrix, pairings, player_strengths)
        calc_scores = scoring_function(new_matrix)
    correlation = measure_order_correlation(player_strengths, calc_scores)
    return correlation


def run_test_rounds_many_correlation(matrix_size, n_iter, scoring_function=calculate_scores_from_matrix):
    correlations = []
    for _ in tqdm(range(n_iter)):
        correlation = run_test_rounds_n_correlation(matrix_size, 3, scoring_function)
        correlations.append(correlation)
    # print(correlations)
    print(mean_and_confint(correlations))
    counts, bins = np.histogram(correlations)
    plt.hist(bins[:-1], bins, weights=counts)
    plt.show()


def winrate(matrix):
    player_count = matrix.shape[0]
    p = []
    for i in range(player_count):
        sum_wins = np.sum(matrix[i])
        sum_losses = np.sum(matrix[:,i])
        estimate = sum_wins / (sum_wins + sum_losses)
        p.append(estimate)
    return p

if __name__ == '__main__':
    run_test_rounds_many_correlation(64, 1000)
