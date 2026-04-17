"""
Shared validation utilities used across recognizer modules.
"""

from __future__ import annotations


def validate_svnr(number: str) -> bool:
    """Validate a German Sozialversicherungsnummer (SVNR / Rentenversicherungsnummer).

    Structure (12 characters, no spaces):
        [2-digit area][6-digit DDMMYY][1 uppercase letter][2-digit serial][1 check digit]

    Algorithm
    ---------
    1. Replace the letter at position 9 with its 2-digit alphabet index
       (A=01, B=02, ..., Z=26), yielding a 13-digit sequence.
    2. Apply weights ``[2,1,2,5,7,1,2,1,2,1,2,1]`` to the first 12 digits.
    3. For each product ≥ 10, replace it with its cross-sum (tens + units digit).
    4. Sum all values; the last digit of the sum must equal the 13th digit
       (the original check digit in position 12).
    """
    clean = number.replace(" ", "").replace("-", "").upper()

    if len(clean) != 12:
        return False
    if not (clean[:8].isdigit() and clean[8].isalpha() and clean[9:].isdigit()):
        return False

    letter_pos = ord(clean[8]) - ord("A") + 1          # A=1 … Z=26
    expanded = (
        [int(c) for c in clean[:8]]
        + [letter_pos // 10, letter_pos % 10]
        + [int(c) for c in clean[9:]]                  # serial (2d) + check (1d)
    )                                                   # total 13 ints

    weights = [2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1]
    total = 0
    for d, w in zip(expanded[:12], weights):
        p = d * w
        total += (p // 10 + p % 10) if p >= 10 else p

    return (total % 10) == expanded[12]


def validate_steuer_id(number: str) -> bool:
    """Validate a German steuerliche Identifikationsnummer (individual TIN).

    Structure: 11 digits.
    - Digit 1: 1-9 (never 0).
    - Digits 1-10: no digit may appear more than three times; at most one digit
      appears more than once in positions 1-10.
    - Digit 11: check digit computed via ISO 7064 MOD 11,10.

    Algorithm (ISO 7064 MOD 11,10)
    --------------------------------
    P = 10
    For each digit d in positions 1-10:
        S = (d + P) % 10; if S == 0: S = 10
        P = (S * 2) % 11
    check = 11 - P; if check == 10: check = 0
    """
    clean = number.replace(" ", "").replace("-", "")
    if not clean.isdigit() or len(clean) != 11:
        return False
    if clean[0] == "0":
        return False

    from collections import Counter
    freq = Counter(clean[:10])
    if max(freq.values()) > 3:
        return False
    if sum(1 for v in freq.values() if v > 1) > 1:
        return False

    p = 10
    for d in (int(c) for c in clean[:10]):
        s = (d + p) % 10
        if s == 0:
            s = 10
        p = (s * 2) % 11
    check = 11 - p
    if check == 10:
        check = 0
    return check == int(clean[10])


def validate_ust_idnr(number: str) -> bool:
    """Validate a German USt-IdNr (VAT identification number).

    Format: ``DE`` followed by exactly 9 digits.
    The first digit of the numeric part must be non-zero.
    Full MOD 97-10 (ISO 7064) validation is applied to the 9-digit part.

    Algorithm
    ---------
    P = 10
    For each digit d in positions 1-8 (first 8 of the 9 digits):
        S = (d + P) % 10; if S == 0: S = 10
        P = (S * 2) % 11
    check = 11 - P; if check == 10: check = 0
    check must equal the 9th digit.
    """
    clean = number.replace(" ", "").upper()
    if not clean.startswith("DE") or len(clean) != 11:
        return False
    digits = clean[2:]
    if not digits.isdigit() or digits[0] == "0":
        return False

    p = 10
    for d in (int(c) for c in digits[:8]):
        s = (d + p) % 10
        if s == 0:
            s = 10
        p = (s * 2) % 11
    check = 11 - p
    if check == 10:
        check = 0
    return check == int(digits[8])


def luhn_check(digits: str) -> bool:
    """Return True if *digits* (only digit characters) satisfy the Luhn algorithm.

    Used by custom recognizers that require digit-sequence validation.
    """
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0
