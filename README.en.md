# deutsch-deid — German PII Detection & Anonymization

> **Detect, mask, and anonymize Personally Identifiable Information (PII) in German text and documents.**  
> Built for EdTech applications and GDPR / DSGVO compliance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![🇩🇪 Deutsch](https://img.shields.io/badge/Sprache-Deutsch-black?logo=googletranslate)](README.md)

---

## What is deutsch-deid?

**deutsch-deid** is a Python library that detects and anonymizes German PII in both plain text and documents (`.pdf`, `.docx`, `.txt`). It combines:

- **Custom German regex recognizers** — hand-tuned patterns for German identifiers (ZIP codes, phone numbers, SVNR, Steuer-ID, USt-IdNr, …)
- **spaCy German NER** (`de_core_news_lg`) — neural named-entity recognition for persons and locations
- **Algorithmic validation** — ISO 7064 MOD 11,10 for individual Steuer-ID and USt-IdNr; SVN modular check algorithm for SVNR
- **Context-aware scoring** — sentence-bounded keyword windows boost or penalize confidence before anonymization decisions

Use cases: de-identifying student records, anonymizing learning management system data, sanitizing intake and registration forms, GDPR / DSGVO data-minimization pipelines, protecting teacher and pupil personal data.

---

## Key Features

| Feature | Detail |
|---------|--------|
| **11 entity types** | Core PII coverage — persons, locations, dates, times, contact info, network data, and German government IDs |
| **3 guard modes** | `anonymize` (realistic synthetic fakes) · `tag` (`[PERSON]`) · `i_tag` (`[PERSON_1]`) |
| **Document support** | Reads `.pdf` (pypdf), `.docx` (python-docx), and `.txt` natively |
| **PDF normalization** | Automatically repairs pypdf extraction artifacts (double spaces, word-per-line scattering) |
| **Algorithmic validation** | ISO 7064 MOD 11,10 for Steuer-ID & USt-IdNr · SVN modular check for SVNR |
| **Context-aware scoring** | Sentence-bounded keyword windows boost or penalize confidence scores |
| **Vocabulary tiers** | Strong / weak keyword distinction — partial boosts for ambiguous context |
| **Negative context** | Contradicting keywords reduce score before thresholding |
| **Entity filtering** | `keep` allowlist or `ignore` denylist per call |
| **Custom patterns** | Plug in your own regex with optional context words and fake-value pools |
| **GDPR / DSGVO ready** | Designed for German EdTech data pipelines and student-data-protection requirements |

---

## Installation

```bash
pip install deutsch-deid
```

Download the spaCy model (required for `PERSON` and `LOCATION` detection):

```bash
python -m spacy download de_core_news_lg
```

Document support requires optional dependencies:

```bash
pip install pypdf          # PDF support
pip install python-docx    # DOCX support
```

---

## Quick Start

```python
from deutsch_deid import analyze, guard

text = (
    "Schüler: Anna Richter, Klasse 9A. "
    "E-Mail: a.richter@gymnasium-berlin.de. "
    "Telefon: +49 162 55512345. "
    "Sozialversicherungsnummer: 12 150780 J 009."
)

# ── Detect PII ────────────────────────────────────────────────────
findings = analyze.text(text)
for f in findings:
    print(f"[{f['type']}] {text[f['start']:f['end']]} (score: {f['score']})")
# [PERSON]        Anna Richter                      (score: 0.85)
# [EMAIL_ADDRESS] a.richter@gymnasium-berlin.de     (score: 0.95)
# [PHONE_NUMBER]  +49 162 55512345                  (score: 0.70)
# [SVNR]          12 150780 J 009                   (score: 0.90)

# ── Anonymize (default mode) ──────────────────────────────────────
result = guard.text(text)
print(result["guarded_text"])
# "Schüler: Lukas Bauer, Klasse 9A. E-Mail: l.bauer@beispiel.de.
#  Telefon: +49 151 87654321. Sozialversicherungsnummer: 65 230561 M 013."

# ── Tag mode ──────────────────────────────────────────────────────
print(guard.text(text, config={"mode": "tag"})["guarded_text"])
# "Schüler: [PERSON], Klasse 9A. E-Mail: [EMAIL_ADDRESS].
#  Telefon: [PHONE_NUMBER]. Sozialversicherungsnummer: [SVNR]."

# ── Indexed tag mode ──────────────────────────────────────────────
print(guard.text(text, config={"mode": "i_tag"})["guarded_text"])
# "Schüler: [PERSON_1], Klasse 9A. E-Mail: [EMAIL_ADDRESS_1].
#  Telefon: [PHONE_NUMBER_1]. Sozialversicherungsnummer: [SVNR_1]."
```

---

## Document Processing

Process files directly — text extraction and PII analysis in one call:

```python
from deutsch_deid import analyze, guard

# Analyze a file
findings = analyze.doc("student_report.pdf")
findings = analyze.doc("registration_form.docx")
findings = analyze.doc("class_notes.txt")

# Anonymize a file
result = guard.doc("student_report.pdf")
print(result["guarded_text"])   # clean, anonymized text
print(result["findings"])       # list of detected PII spans

# All config options work the same as with .text()
result = guard.doc("registration_form.docx", config={
    "mode": "tag",
    "score_threshold": 0.6,
    "set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]},
})
```

**Supported formats:**

| Format | Reader | Notes |
|--------|--------|-------|
| `.txt` | built-in `open()` | UTF-8 |
| `.pdf` | `pypdf` | All pages concatenated; spacing artifacts auto-normalized |
| `.docx` | `python-docx` | All paragraphs joined |

Any other extension raises `UnsupportedFormatError` before the file-existence check.

---

## Supported Entity Types

| Entity | Description | Recognizer | Validation |
|--------|-------------|------------|------------|
| `PERSON` | Person names | spaCy NER (`de_core_news_lg`) | — |
| `LOCATION` | Cities, addresses, regions | spaCy NER (`de_core_news_lg`) | — |
| `DATE` | Dates in numeric and German month-name formats | Regex | — |
| `TIME` | Times in 12h / 24h / "Uhr" format | Regex | — |
| `PHONE_NUMBER` | German mobile & landline, EU international | Regex | — |
| `EMAIL_ADDRESS` | E-mail addresses | Regex | — |
| `URL` | HTTP/HTTPS/FTP and schemeless `www.*` links | Regex | — |
| `ZIPCODE` | German 5-digit postal codes | Regex | — |
| `IP_ADDRESS` | IPv4 and IPv6 addresses | Regex | — |
| `SVNR` | Sozialversicherungsnummer — 2+6+1+2+1 structure | Regex | SVN modular check |
| `STEUER_ID` | USt-IdNr (`DE`+9d), Steuernummer (slash form), individual TIN (11d) | Regex | ISO 7064 MOD 11,10 |

---

## Guard Modes

| Mode | Behaviour | Output example |
|------|-----------|----------------|
| `anonymize` *(default)* | Replace each entity with a realistic synthetic German value | `Lukas Bauer`, `DE876543219`, `12 150780 J 009` |
| `tag` | Replace with `[ENTITY_TYPE]` | `[PERSON]`, `[SVNR]`, `[STEUER_ID]` |
| `i_tag` | Replace with `[ENTITY_TYPE_N]` — same entity type gets the same index | `[PERSON_1]` … `[PERSON_2]` |

---

## Configuration

All options are passed via a single `config` dict:

```python
# Allowlist — only detect these entity types
config = {"set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]}}

# Denylist — detect everything except these
config = {"set_entities": {"ignore": ["DATE", "TIME"]}}

# Full config example
config = {
    "set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]},

    # Minimum confidence to include a finding
    "score_threshold": 0.5,

    # Guard mode
    "mode": "anonymize",   # "anonymize" | "tag" | "i_tag"

    # Custom patterns (see below)
    "custom_patterns": [...],
}
```

### Custom Patterns

```python
from deutsch_deid import analyze, guard, custom_pattern

student_id = custom_pattern(
    name="STUDENT_ID",
    regex=r"STU-\d{4}",
    score=0.9,
    context=["schüler", "student", "matrikelnummer"],   # nearby words boost score
    anonymize_list=["STU-9999", "STU-8888"],            # fake pool for anonymize mode
)

findings = analyze.text("Schüler STU-1234 hat Zugriff.", config={"custom_patterns": [student_id]})
guarded  = guard.text("Schüler STU-1234 hat Zugriff.",  config={"custom_patterns": [student_id]})
print(guarded["guarded_text"])
# "Schüler STU-9999 hat Zugriff."
```

---

## Scoring & Confidence

Every finding carries a `score` between 0 and 1. Scores are determined by a four-tier system:

| Tier | Condition | Example score |
|------|-----------|---------------|
| `base` | Regex match only, no additional evidence | 0.30 – 0.85 |
| `with_context` | A relevant keyword appears in the same sentence | up to 0.92 |
| `validated` | Algorithmic checksum passes (SVN check / ISO 7064 MOD 11,10) | 0.70 – 0.92 |
| `high_confidence` | Validation *and* context keyword present | 0.90 – 0.92 |

Context scoring is **sentence-aware** — context keywords from other sentences do not influence the score. Negative-context keywords actively reduce confidence.

Use `score_threshold` to filter out low-confidence results before anonymization.

---

## Package Layout

```
deutsch_deid/
├── types.py                  — core data structures (RecognizerResult, Pattern, …)
├── analysis/
│   ├── analyzer.py           — PII analysis engine (GuardAnalyzer)
│   ├── context_awareness.py  — sentence-aware keyword scoring (ContextEnhancer)
│   └── overlap_resolver.py   — span deduplication & merging
├── anonymization/
│   ├── engine.py             — stateless anonymization dispatcher (GuardEngine)
│   └── fake_data.py          — synthetic German PII pools
├── recognizers/
│   ├── base.py               — EntityRecognizer / PatternRecognizer base classes
│   ├── contact.py            — PHONE_NUMBER, EMAIL_ADDRESS, URL
│   ├── datetime.py           — DATE, TIME
│   ├── device.py             — IP_ADDRESS
│   ├── location.py           — ZIPCODE
│   ├── social.py             — SVNR (Sozialversicherungsnummer)
│   ├── tax.py                — STEUER_ID (USt-IdNr, Steuernummer, individual TIN)
│   └── spacy_recognizer.py   — NER recognizer (PERSON, LOCATION)
├── processors/
│   ├── text_processor.py     — analyze / guard pipelines for plain-text input
│   └── doc_processor.py      — file reading (.pdf / .docx / .txt) + normalization
├── config/
│   ├── entities.py           — ALL_DE_ENTITY_TYPES list
│   └── scoring.py            — EntityScoreProfile per entity type
└── patterns/
    ├── german_keywords.py    — German month names and keyword lists
    └── german_patterns.py    — all regex patterns
```

The public interface is exposed through `deutsch_deid/__init__.py`:

```python
from deutsch_deid import analyze, guard, custom_pattern, ALL_DE_ENTITY_TYPES
```

---

## Privacy & Compliance

| Standard | How this library helps |
|----------|----------------------|
| **GDPR / DSGVO** | De-identifies personal data before storage or transfer; supports data-minimization obligations |
| **Student Data Protection** | Provides a technical control layer for pseudonymization of student and pupil data in EdTech pipelines |
| **Human-in-the-loop** | Automated detection is probabilistic — for critical datasets, always include human review of anonymized output |

> This library is a **technical tool**, not a legal guarantee. Your full pipeline architecture, access controls, and data governance policies must meet the applicable regulatory requirements.

---

## Interactive Quickstart

The [examples/quickstart.ipynb](examples/quickstart.ipynb) notebook covers:

- Text and document analysis with all 11 entity types
- SVNR (Sozialversicherungsnummer) detection & validation
- STEUER_ID — all three variants (USt-IdNr, Steuernummer, individual TIN)
- All three guard modes (`anonymize`, `tag`, `i_tag`)
- Custom patterns with anonymization pools
- Entity filtering and score thresholds
- End-to-end German student record example

---

## License

MIT License — see [LICENSE](LICENSE) for details.
