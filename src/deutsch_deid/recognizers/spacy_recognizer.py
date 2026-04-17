"""
German spaCy-based NER recognizer for PERSON and LOCATION.
"""
import re
from typing import List

from deutsch_deid.recognizers.base import BaseSpacyRecognizer
from deutsch_deid.types import RecognizerResult


class DeNerRecognizer(BaseSpacyRecognizer):
    """
    German NER recognizer using the de_core_news_lg spaCy model.

    Entity label remapping (PER->PERSON, LOC/GPE->LOCATION) is handled
    upstream by GuardAnalyzer before InternalNlpArtifacts are passed here.

    False-positive filter: rejects spans that look like document IDs
    (e.g. AB12345), label abbreviations (e.g. Ausweisnr., Str.),
    digit-only strings, or time strings.
    """

    ENTITIES = ["PERSON", "LOCATION"]

    # Document/reference IDs: 1-3 uppercase letters followed by 5+ digits
    _ID_PATTERN    = re.compile(r'^[A-Z]{1,3}\d{5,}$', re.IGNORECASE)
    # Label abbreviations ending in "nr.", "nrn.", "str.", "pl."
    _LABEL_PATTERN = re.compile(r'(?i)^.*(?:nrn?\.?|str\.?|pl\.?)$')
    _DIGITS_ONLY   = re.compile(r'^\d+$')
    _TIME_PATTERN  = re.compile(r'^\d{1,2}:\d{2}(?::\d{2})?$')
    # URLs (schemed or www.) — spaCy often tags the domain part as LOC
    _URL_PATTERN   = re.compile(r'(?i)(?:https?://|ftp://|www\.)\S+')
    # E-mail addresses
    _EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

    def __init__(self):
        super().__init__(
            supported_entities=self.ENTITIES,
            supported_language="de",
            ner_strength=0.85,
        )

    @classmethod
    def _is_false_positive(cls, span: str) -> bool:
        s = span.strip()
        return bool(
            cls._ID_PATTERN.match(s)
            or cls._LABEL_PATTERN.match(s)
            or cls._DIGITS_ONLY.match(s)
            or cls._TIME_PATTERN.match(s)
            or cls._URL_PATTERN.search(s)
            or cls._EMAIL_PATTERN.search(s)
        )

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts=None,
    ) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        return [
            r for r in results
            if not self._is_false_positive(text[r.start: r.end])
        ]
