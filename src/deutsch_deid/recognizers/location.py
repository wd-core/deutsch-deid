"""LOCATION group recognizers: ZIPCODE."""
from deutsch_deid.recognizers.base import PatternRecognizer

from deutsch_deid.config.scoring import SCORE_PROFILES
from deutsch_deid.patterns.german_patterns import ZIP_REGEX_DE
from deutsch_deid.recognizers._helpers import _p

_ZI = SCORE_PROFILES["ZIPCODE"]


class DeZipcodeRecognizer(PatternRecognizer):
    PATTERNS = [_p("de_zip", ZIP_REGEX_DE, _ZI.base)]
    CONTEXT = [
        "postleitzahl", "plz", "zip", "postanschrift",
        "hausnummer", "wohnort", "ort", "stadt",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="ZIPCODE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )
