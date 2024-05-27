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


def power_iteration(matrix, iterations=1000, damping_factor=1-(1/12)**2):
    """Compute the dominant eigenvector using the power iteration method."""
    n = matrix.shape[0]
    b_k = np.random.rand(n)
    b_k = normalize_vector(b_k)

    for _ in range(iterations):
        # print(b_k)
        # Apply the damping factor
        b_k1 = (damping_factor * np.dot(matrix, b_k)) + ((1 - damping_factor) / n)
        b_k1 = normalize_vector(b_k1)
        # Check convergence (optional)
        if np.allclose(b_k, b_k1):
            return b_k1

        b_k = b_k1

    return b_k


def transform_win_loss_ratio(A):
    """Turns number of wins and losses into percentage."""
    A = np.array(A)
    A_transpose = A.T
    A_plus_AT = A + A_transpose
    # transformed_A = np.divide(A, A_plus_AT, out=np.zeros(A.shape), where=(A_plus_AT != 0))
    # transformed_A = np.divide(A, A + A_transpose, where=(A + A_transpose != 0))
    transformed_A = np.divide(A, A + A_transpose, out=np.full_like(A, 0.5), where=(A + A_transpose) != 0)
    # np.fill_diagonal(transformed_A, np.diag(A))
    return transformed_A


def calculate_scores(data, num_players, offset=0.01):
    matrix = initialize_matrix(num_players)

    for d in data:
        update_matrix(matrix, *d)

    return calculate_scores_from_matrix(matrix, offset)


def calculate_scores_from_matrix(matrix, offset=0.01, damping_factor=0.85):
    matrix = transform_win_loss_ratio(matrix)

    # Normalise columns
    norms = np.linalg.norm(matrix, axis=0)

    np.divide(matrix, norms, out=matrix, where=(norms != 0))
    if np.isnan(matrix).any():
        breakpoint()
    # Normalise rows
    # norms = np.linalg.norm(matrix, axis=1)
    # np.divide(matrix, norms, out=matrix, where=(norms != 0))

    matrix += offset
    rankings = power_iteration(matrix, damping_factor=1-(1/12)**2)
    # print("Rankings:", rankings)

    return rankings
