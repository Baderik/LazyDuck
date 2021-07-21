from re import sub


def find_snils(text: str) -> str:
    digits = sub("\D", "", text)
    if len(digits) == 9 or len(digits) == 11:
        return digits
    return ""
