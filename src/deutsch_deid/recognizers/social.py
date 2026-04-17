"""SOCIAL group recognizers: SVNR (Sozialversicherungsnummer)."""

from typing import Optional

from deutsch_deid.recognizers.base import PatternRecognizer
from deutsch_deid.config.scoring import SCORE_PROFILES
from deutsch_deid.patterns.german_patterns import SVNR_DE_REGEX
from deutsch_deid.recognizers._helpers import _p
from deutsch_deid.recognizers._utils import validate_svnr

_SV = SCORE_PROFILES["SVNR"]


class DeSvnrRecognizer(PatternRecognizer):
    """
    Detects the German Sozialversicherungsnummer (SVNR).

    Format: 2-digit area code + 6-digit birth date (DDMMYY) +
            1 uppercase letter (surname initial) + 2-digit serial + 1 check digit.

    Example: ``12 150780 J 009``  /  ``12150780J009``

    Detection tiers
    ---------------
    base (0.40)      : regex match only, no surrounding context
    with_context (0.70): context keyword found nearby  (e.g. "versicherungsnummer")
    validated (0.90) : regex match + check-digit passes ``validate_svnr()``
    """

    PATTERNS = [_p("svnr_de", SVNR_DE_REGEX, _SV.base)]
    CONTEXT = [
        "sozialversicherungsnummer", "sozialversicherung", "svnr",
        "rentenversicherungsnummer", "rentenversicherung",
        "versicherungsnummer", "sv-nummer", "sv-nr",
        "versicherungsausweis", "rentenausweis",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="SVNR",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        return validate_svnr(pattern_text)
