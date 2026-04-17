"""
Centralised score profiles for every supported PII entity type.

Each EntityScoreProfile encodes three canonical confidence tiers:

  base           – regex match alone, no surrounding context, no algorithmic
                   validation.  Used as the Pattern score inside PatternRecognizer
                   subclasses and as the starting score for custom EntityRecognizers.

  with_context   – score expected after PatternRecognizer's context-window boost
                   or after ContextEnhancer applies a ContextBoostRule.
                   For PatternRecognizer subclasses this is informational; for
                   EntityRecognizer subclasses that inspect context manually it
                   is used directly.

  validated      – score assigned when an algorithmic check passes.
                   Always ≥ with_context.

  high_confidence – optional fourth tier for entities where both context AND
                    validation are satisfied simultaneously.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


RECOGNIZER_WINDOW_CHARS: int = 120


@dataclass(frozen=True)
class EntityScoreProfile:
    base: float
    with_context: float
    validated: float
    high_confidence: Optional[float] = None


# ---------------------------------------------------------------------------
# Profiles — one entry per entity in ALL_DE_ENTITY_TYPES (see config/entities.py)
# ---------------------------------------------------------------------------

SCORE_PROFILES: dict[str, EntityScoreProfile] = {
    # ── spaCy NER ────────────────────────────────────────────────────────────
    "PERSON":           EntityScoreProfile(base=0.85, with_context=0.90, validated=0.90),
    "LOCATION":         EntityScoreProfile(base=0.85, with_context=0.90, validated=0.90),

    # ── Temporal ─────────────────────────────────────────────────────────────
    "DATE":             EntityScoreProfile(base=0.30, with_context=0.65, validated=0.85),
    "TIME":             EntityScoreProfile(base=0.45, with_context=0.70, validated=0.70),

    # ── Contact ──────────────────────────────────────────────────────────────
    "PHONE_NUMBER":     EntityScoreProfile(base=0.30, with_context=0.75, validated=0.75),
    "EMAIL_ADDRESS":    EntityScoreProfile(base=0.90, with_context=0.95, validated=0.95),
    "ZIPCODE":          EntityScoreProfile(base=0.55, with_context=0.75, validated=0.75),
    "URL":              EntityScoreProfile(base=0.70, with_context=0.85, validated=0.85),

    # ── Network ──────────────────────────────────────────────────────────────
    "IP_ADDRESS":       EntityScoreProfile(base=0.60, with_context=0.80, validated=0.80),

    # ── Social / Government ID ────────────────────────────────────────────────
    "SVNR":             EntityScoreProfile(base=0.40, with_context=0.70, validated=0.90),

    # ── Tax ID ────────────────────────────────────────────────────────────────
    # Three sub-formats share one profile; pattern-level base scores differ
    # (0.75 / 0.45 / 0.30) — these are set directly in DeSteuerIdRecognizer.PATTERNS.
    "STEUER_ID":        EntityScoreProfile(base=0.30, with_context=0.85, validated=0.92),
}
