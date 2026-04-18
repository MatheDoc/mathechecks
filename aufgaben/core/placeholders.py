from aufgaben.core.tolerances import (
    ANALYSIS_CALC_DECIMALS,
    ANALYSIS_CALC_TOLERANCE,
    STOCHASTIK_CALC_DECIMALS,
    STOCHASTIK_CALC_TOLERANCE,
)


def _format_number(value: float, decimals: int = 2, decimal_comma: bool = True) -> str:
    text = f"{value:.{decimals}f}"
    if decimal_comma:
        text = text.replace(".", ",")
    return text


def numerical(
    value: float,
    tolerance: float = 0.01,
    points: int = 1,
    decimals: int = 2,
    decimal_comma: bool = True,
) -> str:
    value_str = _format_number(value, decimals=decimals, decimal_comma=decimal_comma)
    tolerance_str = _format_number(tolerance, decimals=decimals, decimal_comma=decimal_comma)
    return f"{{{points}:NUMERICAL:={value_str}:{tolerance_str}}}"


def numerical_analysis_calc(
    value: float,
    points: int = 1,
    decimal_comma: bool = True,
) -> str:
    return numerical(
        value=value,
        tolerance=ANALYSIS_CALC_TOLERANCE,
        points=points,
        decimals=ANALYSIS_CALC_DECIMALS,
        decimal_comma=decimal_comma,
    )


def numerical_stochastik_calc(
    value: float,
    points: int = 1,
    decimal_comma: bool = True,
) -> str:
    return numerical(
        value=value,
        tolerance=STOCHASTIK_CALC_TOLERANCE,
        points=points,
        decimals=STOCHASTIK_CALC_DECIMALS,
        decimal_comma=decimal_comma,
    )


def mc(options: list[str], correct_index: int, points: int = 1) -> str:
    entries: list[str] = []
    for index, option in enumerate(options):
        marker = "=" if index == correct_index else ""
        entries.append(f"~{marker}{option}")
    return f"{{{points}:MC:{''.join(entries)}}}"


# ---------------------------------------------------------------------------
# NUMERICAL_OPT — Zahlenfeld mit „existiert nicht"-Option
# ---------------------------------------------------------------------------

def numerical_opt(
    value: float,
    tolerance: float = 0.01,
    points: int = 1,
    decimals: int = 2,
    decimal_comma: bool = True,
) -> str:
    """Numerisches Feld, das auch 'existiert nicht' als Antwort erlaubt."""
    value_str = _format_number(value, decimals=decimals, decimal_comma=decimal_comma)
    tolerance_str = _format_number(tolerance, decimals=decimals, decimal_comma=decimal_comma)
    return f"{{{points}:NUMERICAL_OPT:={value_str}:{tolerance_str}}}"


def numerical_opt_none(points: int = 1) -> str:
    """'Existiert nicht' ist die korrekte Antwort."""
    return f"{{{points}:NUMERICAL_OPT:=NONE}}"


def numerical_opt_analysis(
    value: float,
    points: int = 1,
    decimal_comma: bool = True,
) -> str:
    """NUMERICAL_OPT mit Analysis-Standardtoleranz."""
    return numerical_opt(
        value=value,
        tolerance=ANALYSIS_CALC_TOLERANCE,
        points=points,
        decimals=ANALYSIS_CALC_DECIMALS,
        decimal_comma=decimal_comma,
    )
