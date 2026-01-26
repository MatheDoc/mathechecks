def latex_term(coef, variable, power=1):
    """
    Baut einen LaTeX-Term aus einer Zahl, einer Variable und optional einem Exponenten.
    """
    if coef == 0:
        return ""  # Term entfällt
    sign = "-" if coef < 0 else ""
    abs_coef = abs(coef)

    # Koeffizient nur anzeigen, wenn sie != 1 oder Exponent 0
    if abs_coef == 1 and power != 0:
        coef_str = ""
    else:
        coef_str = str(abs_coef)

    # Exponent
    if power == 0:
        var_str = ""
    elif power == 1:
        var_str = variable
    else:
        var_str = f"{variable}^{power}"

    return f"{sign}{coef_str}{var_str}"

def latex_polynomial(coeffs, name="f", variable="x"):
    """
    Baut einen LaTeX-String aus einer Liste von Koeffizienten.
    coeffs[0] = höchste Potenz
    """
    degree = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = degree - i
        term = latex_term(c, variable, power)
        if term:
            # Vorzeichen berücksichtigen
            if terms:
                if term.startswith("-"):
                    terms.append(term)
                else:
                    terms.append(f"+{term}")
            else:
                terms.append(term)
    polynomial = "".join(terms)
    return f"\\({name}(x) = {polynomial}\\)"