"""TAX group recognizers: STEUER_ID (German tax identification numbers).

Three sub-formats are detected under a single entity label:

  USt-IdNr  — intra-community VAT ID: ``DE`` + 9 digits
              e.g. "DE123456788"
              High base score (0.75); validated via ISO 7064 MOD 11,10.

  Steuernummer — domestic business tax number (slash/space delimited)
              e.g. "12/345/67890", "123 456 78901"
              Medium base score (0.45); no algorithmic validation possible
              (format varies per Bundesland).

  Steuer-ID — individual 11-digit TIN (steuerliche Identifikationsnummer)
              e.g. "12345678903"
              Low base score (0.30) due to ambiguity; validated via
              ISO 7064 MOD 11,10.
"""

import re
from copy import copy as _copy
from typing import List, Optional

from deutsch_deid.recognizers.base import PatternRecognizer
from deutsch_deid.config.scoring import SCORE_PROFILES
from deutsch_deid.patterns.german_patterns import (
    UST_ID_REGEX,
    STEUERNUMMER_REGEX,
    STEUER_INDIVIDUAL_REGEX,
)
from deutsch_deid.recognizers._helpers import _p
from deutsch_deid.recognizers._utils import validate_steuer_id, validate_ust_idnr

_ST = SCORE_PROFILES["STEUER_ID"]

# Regex to decide which sub-format matched
_UST_ID_RE = re.compile(r"^DE[\s]?\d{3}[\s]?\d{3}[\s]?\d{3}$", re.IGNORECASE)
_STEUERNUMMER_RE = re.compile(r"^\d{2,3}[\s/]\d{3,5}[\s/]\d{4,5}$")

# Context window used when capping individual-TIN scores
_CTX_WINDOW = 120
# Score for a validated individual TIN with NO context keyword nearby
_INDIV_VALIDATED_NO_CTX: float = 0.55


class DeSteuerIdRecognizer(PatternRecognizer):
    """
    Detects all three variants of German tax identification numbers
    under the unified label ``STEUER_ID``.

    Detection tiers
    ---------------
    base:         0.75 (USt-IdNr), 0.45 (Steuernummer), 0.30 (Steuer-ID individual)
    with_context: 0.85 — context keyword (e.g. "steuernummer") found nearby
    validated:    0.92 — regex match + algorithmic check passes
    """

    PATTERNS = [
        _p("ust_id",          UST_ID_REGEX,           0.75),
        _p("steuernummer",    STEUERNUMMER_REGEX,      0.45),
        _p("steuer_id_indiv", STEUER_INDIVIDUAL_REGEX, 0.30),
    ]
    CONTEXT = [
        "steuernummer", "steueridentifikationsnummer", "steuer-id",
        "steuerid", "steuerliche identifikationsnummer",
        "umsatzsteuer-identifikationsnummer", "ust-idnr", "ust-id",
        "umsatzsteuer-id", "umsatzsteuernummer", "umsatzsteuer",
        "finanzamt", "steuerpflichtig", "steuer-nr", "st.-nr",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="STEUER_ID",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        text = pattern_text.strip()
        # USt-IdNr: DE + 9 digits — validate; high base score (0.75) makes
        # context less critical, so we apply full validated tier directly.
        if _UST_ID_RE.match(text):
            return validate_ust_idnr(text)
        # Steuernummer (slash/space format) — no universal checksum algorithm
        if _STEUERNUMMER_RE.match(text):
            return None
        # Individual 11-digit Steuer-ID — return None here; the actual checksum
        # is applied in analyze() after context presence is checked, to avoid
        # giving 0.92 to bare 11-digit numbers with no surrounding context.
        return None

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts=None,
    ) -> List["RecognizerResult"]:  # type: ignore[name-defined]
        results = super().analyze(text, entities, nlp_artifacts)

        text_lower = text.lower()
        adjusted = []
        for r in results:
            pname = (
                r.analysis_explanation.pattern_name
                if r.analysis_explanation
                else None
            )
            if pname == "steuer_id_indiv":
                clean = text[r.start: r.end].replace(" ", "")
                if clean.isdigit() and len(clean) == 11:
                    checksum_ok = validate_steuer_id(clean)
                    if not checksum_ok:
                        # Fail checksum → drop the result entirely
                        continue
                    # Checksum passes — check if a context keyword is nearby
                    lo = max(0, r.start - _CTX_WINDOW)
                    hi = min(len(text), r.end + _CTX_WINDOW)
                    window = text_lower[lo:hi]
                    has_context = any(kw in window for kw in self.context)
                    r = _copy(r)
                    r.score = _ST.validated if has_context else _INDIV_VALIDATED_NO_CTX
            adjusted.append(r)

        return adjusted
