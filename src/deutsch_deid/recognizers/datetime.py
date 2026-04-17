"""DATETIME group recognizers: DATE, TIME."""
from deutsch_deid.recognizers.base import PatternRecognizer

from deutsch_deid.config.scoring import SCORE_PROFILES
from deutsch_deid.patterns.german_patterns import (
    DATE_WITHOUT_WORDS_DE, DATE_DD_MM_YY, DATE_YY_MM_DD,
    DATE_WITH_WORDS_DE, DATE_WORDS_FUZZY_DE,
    DATE_ISO_TIMESTAMP, DATE_EN_ORDINAL, DATE_EN_WORDS,
    TIME_REGEX,
)
from deutsch_deid.recognizers._helpers import _p

_D = SCORE_PROFILES["DATE"]
_T = SCORE_PROFILES["TIME"]


class DeDateRecognizer(PatternRecognizer):
    PATTERNS = [
        _p("date_iso_ts",      DATE_ISO_TIMESTAMP,    0.90),
        _p("date_en_ordinal",  DATE_EN_ORDINAL,       0.80),
        _p("date_en_words",    DATE_EN_WORDS,         0.75),
        _p("date_words_de",    DATE_WITH_WORDS_DE,    _D.validated),
        _p("date_numeric",     DATE_WITHOUT_WORDS_DE, 0.60),
        _p("date_dd_mm_yy",    DATE_DD_MM_YY,         0.50),
        _p("date_yy_mm_dd",    DATE_YY_MM_DD,         0.50),
        _p("date_words_fuzzy", DATE_WORDS_FUZZY_DE,   _D.base),
    ]
    CONTEXT = [
        "datum", "geburtsdatum", "date", "geboren", "sterbedatum",
        "tag", "monat", "jahr", "ablaufdatum", "startdatum", "enddatum",
        "ausstellungsdatum", "abgelaufen", "exp", "expiry", "gueltig",
        "birthday", "birth", "born", "geburtstag",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="DATE",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )


class DeTimeRecognizer(PatternRecognizer):
    PATTERNS = [_p("time_de", TIME_REGEX, _T.base)]
    CONTEXT = [
        "uhr", "time", "um", "gegen", "zeitpunkt",
        "minute", "sekunde", "beginn", "endzeit",
        "aktualisiert", "eingeloggt", "glocke",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="TIME",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )
