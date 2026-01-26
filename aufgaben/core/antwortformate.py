class Antwortformat:
    @staticmethod
    def numerical(value,points=1, tolerance=0.01, decimals=2):
        value_str = f"{value:.{decimals}f}"
        return f"{{{{{points}:NUMERICAL:={value_str}:{tolerance}}}}}"
    @staticmethod
    def integer(points, value):
        return f"{{{{{points}:NUMERICAL:={int(value)}:0}}}}"
    @staticmethod
    def multiple_choice(points, correct_index):
        return f"{{{{{points}:MULTICHOICE:={correct_index}}}}}"