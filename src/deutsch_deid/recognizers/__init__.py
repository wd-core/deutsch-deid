"""
Recognizer registry for deutsch_deid.

Imports every domain recognizer and exports:
  - ALL_REGEX_RECOGNIZERS  – ordered list of recognizer *classes* (not instances)
    passed to GuardAnalyzer at engine initialisation.
  - Individual classes re-exported for direct import convenience.
"""

from deutsch_deid.recognizers.datetime import DeDateRecognizer, DeTimeRecognizer
from deutsch_deid.recognizers.contact import (
    DePhoneRecognizer,
    DeEmailRecognizer,
    DeUrlRecognizer,
)
from deutsch_deid.recognizers.location import DeZipcodeRecognizer
from deutsch_deid.recognizers.device import DeIpRecognizer
from deutsch_deid.recognizers.social import DeSvnrRecognizer
from deutsch_deid.recognizers.tax import DeSteuerIdRecognizer
from deutsch_deid.recognizers.spacy_recognizer import DeNerRecognizer

ALL_REGEX_RECOGNIZERS = [
    # ── DATETIME ─────────────────────────────────────────────────
    DeDateRecognizer,
    DeTimeRecognizer,
    # ── CONTACT ──────────────────────────────────────────────────
    DePhoneRecognizer,
    DeEmailRecognizer,
    DeUrlRecognizer,
    # ── LOCATION ─────────────────────────────────────────────────
    DeZipcodeRecognizer,
    # ── NETWORK ──────────────────────────────────────────────────
    DeIpRecognizer,
    # ── SOCIAL ───────────────────────────────────────────────────
    DeSvnrRecognizer,
    # ── TAX ──────────────────────────────────────────────────────
    DeSteuerIdRecognizer,
]

__all__ = [
    "ALL_REGEX_RECOGNIZERS",
    "DeNerRecognizer",
    "DeDateRecognizer",
    "DeTimeRecognizer",
    "DePhoneRecognizer",
    "DeEmailRecognizer",
    "DeUrlRecognizer",
    "DeZipcodeRecognizer",
    "DeIpRecognizer",
    "DeSvnrRecognizer",
    "DeSteuerIdRecognizer",
]
