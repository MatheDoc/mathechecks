import random


def numerical_int(value: int) -> str:
    return f"{{1:NUMERICAL:={value}:0}}"


def random_matrix(rng: random.Random, rows: int, cols: int,
                  low: int = -9, high: int = 9) -> list[list[int]]:
    return [[rng.randint(low, high) for _ in range(cols)] for _ in range(rows)]


def matrix_to_latex(matrix: list[list[int]]) -> str:
    rows = [" & ".join(str(v) for v in row) for row in matrix]
    return r"\begin{pmatrix} " + r" \\ ".join(rows) + r" \end{pmatrix}"


def mat_add(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_sub(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def scalar_mul(s: int, a: list[list[int]]) -> list[list[int]]:
    return [[s * a[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_mul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    m = len(a)
    n = len(b[0])
    k = len(b)
    result = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            for p in range(k):
                result[i][j] += a[i][p] * b[p][j]
    return result


def transpose(a: list[list[int]]) -> list[list[int]]:
    m = len(a)
    n = len(a[0])
    return [[a[i][j] for i in range(m)] for j in range(n)]


def det_2x2(a: list[list[int]]) -> int:
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]


def det_3x3(a: list[list[int]]) -> int:
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def det_nxn(a: list[list[int]]) -> int:
    n = len(a)
    if n == 1:
        return a[0][0]
    if n == 2:
        return det_2x2(a)
    if n == 3:
        return det_3x3(a)
    result = 0
    for j in range(n):
        minor = [[a[i][k] for k in range(n) if k != j] for i in range(1, n)]
        sign = 1 if j % 2 == 0 else -1
        result += sign * a[0][j] * det_nxn(minor)
    return result


def random_invertible(rng: random.Random, n: int, *,
                      max_entry: int = 9,
                      steps_range: tuple[int, int] = (3, 6),
                      max_zeros: int | None = None) -> list[list[int]]:
    """Generate a random n×n integer matrix with det = ±1.

    Builds from identity via elementary row operations so that the
    determinant stays ±1 and all entries remain bounded.
    *max_zeros* limits how many zero entries the matrix may contain
    (default: at most n-1 zeros, i.e. less than one zero per row on average).
    """
    if max_zeros is None:
        max_zeros = n - 1

    for _ in range(500):
        a = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        num_steps = rng.randint(*steps_range)
        for _ in range(num_steps):
            i, j = rng.sample(range(n), 2)
            k = rng.choice([-2, -1, 1, 2])
            for col in range(n):
                a[i][col] += k * a[j][col]
        if rng.random() < 0.5:
            row = rng.randrange(n)
            a[row] = [-x for x in a[row]]
        if all(abs(a[i][j]) <= max_entry for i in range(n) for j in range(n)):
            # Reject trivial identity-like matrices
            flat = [a[i][j] for i in range(n) for j in range(n)]
            identity_flat = [1 if i == j else 0 for i in range(n) for j in range(n)]
            neg_identity_flat = [-1 if i == j else 0 for i in range(n) for j in range(n)]
            if flat == identity_flat or flat == neg_identity_flat:
                continue
            # Reject matrices with too many zeros
            zero_count = sum(1 for v in flat if v == 0)
            if zero_count > max_zeros:
                continue
            return a
    # Fallback: simple non-trivial matrix
    a = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    a[0][1] = 1
    return a


def inverse_nxn(a: list[list[int]]) -> list[list[int]]:
    """Compute the integer inverse of an n×n matrix with det = ±1.

    Uses cofactor expansion. Only valid when det(a) = ±1.
    """
    n = len(a)
    det = det_nxn(a)
    if abs(det) != 1:
        raise ValueError(f"Matrix is not Z-invertible (det={det})")

    cofactors = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [[a[r][c] for c in range(n) if c != j]
                     for r in range(n) if r != i]
            sign = 1 if (i + j) % 2 == 0 else -1
            cofactors[i][j] = sign * det_nxn(minor)

    # Transpose cofactors → adjugate, then multiply by 1/det (= det since det=±1)
    inv = [[det * cofactors[j][i] for j in range(n)] for i in range(n)]
    return inv


def entry_questions(matrix: list[list[int]]) -> tuple[list[str], list[str]]:
    """Return (fragen, antworten) in compact matrix format.

    fragen:  single item – shows the result matrix with named variables
    antworten: single item – variable assignments grouped by rows with <br>
    """
    rows = len(matrix)
    cols = len(matrix[0])

    # Build variable names: a, b, c, ... (max 26 for up to ~5×5)
    var_names: list[list[str]] = []
    idx = 0
    for i in range(rows):
        row_vars: list[str] = []
        for j in range(cols):
            row_vars.append(chr(ord("a") + idx))
            idx += 1
        var_names.append(row_vars)

    # Build the question: matrix with variable names
    latex_rows = [" & ".join(v for v in row) for row in var_names]
    var_matrix_latex = r"\begin{pmatrix} " + r" \\ ".join(latex_rows) + r" \end{pmatrix}"
    frage = f"Bestimme die Ergebnismatrix $ {var_matrix_latex} $."

    # Build the answer: variables with values, grouped by rows via <br>
    answer_parts: list[str] = []
    for i in range(rows):
        row_parts: list[str] = []
        for j in range(cols):
            var = var_names[i][j]
            val = matrix[i][j]
            row_parts.append(f"\\( {var}= \\){numerical_int(val)}")
        answer_parts.append("".join(row_parts))
    antwort = "<br>".join(answer_parts) + "<br>"

    return [frage], [antwort]
