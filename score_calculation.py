import numpy as np


def initialize_matrix(n):
    """Initialize an n x n matrix with zeros."""
    return np.zeros((n, n))


def update_matrix(matrix, winner, loser, win_ratio=1, lose_ratio=0):
    """Update the matrix for a match result."""
    matrix[winner][loser] += win_ratio
    matrix[loser][winner] += lose_ratio


def normalize_vector(v):
    """Normalize a vector."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def power_iteration(matrix, iterations=100, damping_factor=0.85):
    """Compute the dominant eigenvector using the power iteration method."""
    n = matrix.shape[0]
    b_k = np.random.rand(n)
    # b_k = np.ones(n)
    b_k = normalize_vector(b_k)

    for i in range(iterations):
        # print(b_k)
        # Apply the damping factor
        b_k1 = (damping_factor * np.dot(matrix, b_k)) + ((1 - damping_factor) / n)
        b_k1 = normalize_vector(b_k1)

        # Check convergence
        if np.allclose(b_k, b_k1):
            print("Converge:", i)
            return b_k1

        b_k = b_k1

    print("Converge:", i)
    return b_k


def transform_win_loss_ratio(A):
    """Turns number of wins and losses into percentage."""
    A = np.array(A).astype(float)
    A_transpose = A.T
    transformed_A = np.divide(A, A + A_transpose, out=np.full_like(A, 0.5), where=(A + A_transpose) != 0)
    # transformed_A = np.divide(A, A + A_transpose, out=np.full_like(A, 0), where=(A + A_transpose) != 0)
    return transformed_A


def calculate_scores(data, num_players, offset=0.01):
    matrix = get_matrix_from_matches(data, num_players)
    return calculate_scores_from_matrix(matrix, offset)

def get_matrix_from_matches(matches, num_players):
    matrix = initialize_matrix(num_players)
    for d in matches:
        update_matrix(matrix, *d)
    return matrix

def calculate_scores_from_matrix(matrix, offset=0.01, damping_factor=0.85):
    matrix = np.array(matrix)

    # print(matrix)
    matrix = transform_win_loss_ratio(matrix)
    # print(matrix)

    # Normalise columns
    norms = np.linalg.norm(matrix, axis=0)
    np.divide(matrix, norms, out=matrix, where=(norms != 0))

    # Normalise rows
    # norms = np.linalg.norm(matrix, axis=1)
    # np.divide(matrix, norms, out=matrix, where=(norms != 0))

    matrix += offset
    rankings = power_iteration(matrix, damping_factor=0.85)
    # print("Rankings:", rankings)

    return rankings
