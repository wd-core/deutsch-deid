"""
deutsch_deid

A Python library for detecting and anonymizing PII in German EdTech text and documents.
Powered by a custom NLP engine and spaCy.

Package layout
--------------
deutsch_deid/
  types.py              - core data structures (RecognizerResult, Pattern, ...)
  config/               - entity type list and scoring profiles
  patterns/             - regex patterns and keyword lists
  recognizers/
    base.py             - EntityRecognizer / PatternRecognizer / BaseSpacyRecognizer
    contact.py          - PHONE_NUMBER, EMAIL_ADDRESS, URL
    datetime.py         - DATE, TIME
    device.py           - IP_ADDRESS
    location.py         - ZIPCODE
    spacy_recognizer.py - PERSON, LOCATION (NER)
  analysis/
    analyzer.py         - GuardAnalyzer engine + resolve_entities / run helpers
    context_awareness.py - ContextEnhancer score-boosting rules
    overlap_resolver.py  - resolve_overlaps / merge_entities
  anonymization/
    engine.py           - GuardEngine (anonymize / tag / i_tag modes)
    fake_data.py        - synthetic PII pools
    strategies.py       - OperatorConfig re-export
  processors/
    text_processor.py   - analyze / guard pipelines for plain-text input
    doc_processor.py    - file reading (.pdf/.docx/.txt) + text pipelines
"""

from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from deutsch_deid.config.entities import ALL_DE_ENTITY_TYPES
from deutsch_deid.processors.text_processor import analyze as _analyze, guard as _guard
from deutsch_deid.processors.doc_processor import (
    UnsupportedFormatError,
    analyze as _analyze_doc,
    guard as _guard_doc,
)

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Public namespace objects
# ---------------------------------------------------------------------------

analyze = SimpleNamespace(
    text=_analyze,
    doc=_analyze_doc,
)

guard = SimpleNamespace(
    text=_guard,
    doc=_guard_doc,
)


def custom_pattern(
    name: str,
    regex: str,
    score: float = 0.85,
    context: Optional[List[str]] = None,
    anonymize_list: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a custom pattern definition for use in ``config["custom_patterns"]``.

    Args:
        name           : Entity type label (e.g. ``"STUDENT_ID"``).
        regex          : Python regex string.
        score          : Confidence score (default 0.85).
        context        : Words near the match that boost confidence.
        anonymize_list : Fake replacement values for anonymize mode.

    Returns:
        dict ready for ``config["custom_patterns"]``.

    Example::

        from deutsch_deid import guard, custom_pattern

        pattern = custom_pattern(
            name="STUDENT_ID",
            regex=r"STU-\\d{4}",
            score=0.9,
            context=["schueler", "student"],
            anonymize_list=["STU-0001", "STU-0002"],
        )
        guard.text(text, config={"custom_patterns": [pattern]})
        guard.doc("/path/to/file.pdf", config={"custom_patterns": [pattern]})
    """
    return {
        "name": name,
        "regex": regex,
        "score": score,
        "context": context,
        "anonymize_list": anonymize_list,
    }

__all__ = [
    "analyze",
    "guard",
    "custom_pattern",
    "ALL_DE_ENTITY_TYPES",
    "UnsupportedFormatError",
    "__version__",
]
