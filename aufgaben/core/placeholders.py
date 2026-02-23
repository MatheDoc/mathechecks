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


def mc(options: list[str], correct_index: int, points: int = 1) -> str:
    entries: list[str] = []
    for index, option in enumerate(options):
        prefix = "=" if index == correct_index else "~"
        entries.append(f"{prefix}{option}")
    return f"{{{points}:MC:{''.join(entries)}}}"
