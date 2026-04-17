# deutsch-deid — Erkennung & Anonymisierung von personenbezogenen Daten auf Deutsch

> **Erkennung, Maskierung und Anonymisierung personenbezogener Daten (PII) in deutschen Texten und Dokumenten.**  
> Entwickelt für EdTech-Anwendungen und DSGVO-Compliance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-green.svg)](LICENSE)
[![🇬🇧 English](https://img.shields.io/badge/Language-English-black?logo=googletranslate)](README.en.md)

---

## Was ist deutsch-deid?

**deutsch-deid** ist eine Python-Bibliothek zur Erkennung und Anonymisierung personenbezogener Daten in deutschen Texten und Dokumenten (`.pdf`, `.docx`, `.txt`). Sie kombiniert:

- **Angepasste deutsche Regex-Erkenner** — handoptimierte Muster für deutsche Identifikatoren (PLZ, Telefonnummern, SVNR, Steuer-ID, USt-IdNr, …)
- **spaCy German NER** (`de_core_news_lg`) — neuronale Eigennamenerkennung für Personen und Orte
- **Algorithmische Validierung** — ISO 7064 MOD 11,10 für individuelle Steuer-ID und USt-IdNr; SVN-Modular-Check für die SVNR
- **Kontextbewusstes Scoring** — satzgebundene Schlüsselwortfenster erhöhen oder verringern die Konfidenz vor der Anonymisierung

Anwendungsfälle: Anonymisierung von Schülerakten, Anonymisierung von Lernmanagementsystem-Daten, Bereinigung von Anmeldungsformularen, DSGVO-Datensparsamkeits-Pipelines, Schutz personenbezogener Daten von Lehrern und Schülern.

---

## Hauptfunktionen

| Funktion | Details |
|---------|--------|
| **11 Entitätstypen** | Kern-PII-Abdeckung — Personen, Orte, Datum, Uhrzeit, Kontaktdaten, Netzwerkdaten und deutsche Ausweisdokumente |
| **3 Schutzmodi** | `anonymize` (realistische synthetische Ersatzwerte) · `tag` (`[PERSON]`) · `i_tag` (`[PERSON_1]`) |
| **Dokumentenunterstützung** | Liest `.pdf` (pypdf), `.docx` (python-docx) und `.txt` nativ |
| **PDF-Normalisierung** | Repariert automatisch pypdf-Extraktionsartefakte (doppelte Leerzeichen, Wort-pro-Zeile-Streuung) |
| **Algorithmische Validierung** | ISO 7064 MOD 11,10 für Steuer-ID & USt-IdNr · SVN-Modular-Check für SVNR |
| **Kontextbewusstes Scoring** | Satzgebundene Schlüsselwortfenster erhöhen oder verringern Konfidenzwerte |
| **Vokabularebenen** | Unterscheidung zwischen starken und schwachen Schlüsselwörtern — teilweise Verstärkung bei mehrdeutigem Kontext |
| **Negativer Kontext** | Widersprechende Schlüsselwörter reduzieren den Score vor der Schwellwertfilterung |
| **Entitätsfilterung** | `keep`-Allowlist oder `ignore`-Denylist pro Aufruf |
| **Eigene Muster** | Eigene Regex-Muster mit optionalen Kontextwörtern und Fake-Wert-Pools einbinden |
| **DSGVO-bereit** | Für deutsche EdTech-Datenpipelines und Schülerdatenschutz-Anforderungen ausgelegt |

---

## Installation

```bash
pip install deutsch-deid
```

Laden Sie das spaCy-Modell herunter (erforderlich für die Erkennung von `PERSON` und `LOCATION`):

```bash
python -m spacy download de_core_news_lg
```

Für die Dokumentenverarbeitung werden optionale Abhängigkeiten benötigt:

```bash
pip install pypdf          # PDF-Unterstützung
pip install python-docx    # DOCX-Unterstützung
```

---

## Schnellstart

```python
from deutsch_deid import analyze, guard

text = (
    "Schüler: Anna Richter, Klasse 9A. "
    "E-Mail: a.richter@gymnasium-berlin.de. "
    "Telefon: +49 162 55512345. "
    "Sozialversicherungsnummer: 12 150780 J 009."
)

# ── PII erkennen ──────────────────────────────────────────────────
findings = analyze.text(text)
for f in findings:
    print(f"[{f['type']}] {text[f['start']:f['end']]} (Score: {f['score']})")
# [PERSON]        Anna Richter                      (Score: 0.85)
# [EMAIL_ADDRESS] a.richter@gymnasium-berlin.de     (Score: 0.95)
# [PHONE_NUMBER]  +49 162 55512345                  (Score: 0.75)
# [SVNR]          12 150780 J 009                   (Score: 0.90)

# ── Anonymisieren (Standardmodus) ─────────────────────────────────
result = guard.text(text)
print(result["guarded_text"])
# "Schüler: Lukas Bauer, Klasse 9A. E-Mail: l.bauer@beispiel.de.
#  Telefon: +49 151 87654321. Sozialversicherungsnummer: 65 230561 M 013."

# ── Tag-Modus ─────────────────────────────────────────────────────
print(guard.text(text, config={"mode": "tag"})["guarded_text"])
# "Schüler: [PERSON], Klasse 9A. E-Mail: [EMAIL_ADDRESS].
#  Telefon: [PHONE_NUMBER]. Sozialversicherungsnummer: [SVNR]."

# ── Indizierter Tag-Modus ─────────────────────────────────────────
print(guard.text(text, config={"mode": "i_tag"})["guarded_text"])
# "Schüler: [PERSON_1], Klasse 9A. E-Mail: [EMAIL_ADDRESS_1].
#  Telefon: [PHONE_NUMBER_1]. Sozialversicherungsnummer: [SVNR_1]."
```

---

## Dokumentenverarbeitung

Dateien direkt verarbeiten — Textextraktion und PII-Analyse in einem Aufruf:

```python
from deutsch_deid import analyze, guard

# Datei analysieren
findings = analyze.doc("schuelerakte.pdf")
findings = analyze.doc("anmeldeformular.docx")
findings = analyze.doc("klassennotizbuch.txt")

# Datei anonymisieren
result = guard.doc("schuelerakte.pdf")
print(result["guarded_text"])   # bereinigter, anonymisierter Text
print(result["findings"])       # Liste der erkannten PII-Spans

# Alle Konfigurationsoptionen funktionieren genauso wie bei .text()
result = guard.doc("anmeldeformular.docx", config={
    "mode": "tag",
    "score_threshold": 0.6,
    "set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]},
})
```

**Unterstützte Formate:**

| Format | Leser | Hinweise |
|--------|--------|-------|
| `.txt` | eingebautes `open()` | UTF-8 |
| `.pdf` | `pypdf` | Alle Seiten zusammengeführt; Abstandsartefakte werden automatisch normalisiert |
| `.docx` | `python-docx` | Alle Absätze zusammengeführt |

Jede andere Erweiterung löst einen `UnsupportedFormatError` aus, bevor die Dateiexistenz geprüft wird.

---

## Unterstützte Entitätstypen

| Entität | Beschreibung | Erkenner | Validierung |
|--------|-------------|------------|------------|
| `PERSON` | Personennamen | spaCy NER (`de_core_news_lg`) | — |
| `LOCATION` | Städte, Adressen, Regionen | spaCy NER (`de_core_news_lg`) | — |
| `DATE` | Datumsangaben (numerisch und mit deutschen Monatsnamen) | Regex | — |
| `TIME` | Uhrzeiten (12h / 24h / „Uhr"-Format) | Regex | — |
| `PHONE_NUMBER` | Deutsche Mobil- und Festnetznummern, EU-International | Regex | — |
| `EMAIL_ADDRESS` | E-Mail-Adressen | Regex | — |
| `URL` | HTTP/HTTPS/FTP und schemalose `www.*`-Links | Regex | — |
| `ZIPCODE` | Deutsche 5-stellige Postleitzahlen | Regex | — |
| `IP_ADDRESS` | IPv4- und IPv6-Adressen | Regex | — |
| `SVNR` | Sozialversicherungsnummer — Struktur 2+6+1+2+1 | Regex | SVN-Modular-Check |
| `STEUER_ID` | USt-IdNr (`DE`+9d), Steuernummer (Schrägstrichformat), individuelle TIN (11d) | Regex | ISO 7064 MOD 11,10 |

---

## Schutzmodi

| Modus | Verhalten | Ausgabebeispiel |
|------|-----------|----------------|
| `anonymize` *(Standard)* | Ersetzt jede Entität durch einen realistischen synthetischen deutschen Wert | `Lukas Bauer`, `DE876543219`, `12 150780 J 009` |
| `tag` | Ersetzt durch `[ENTITÄTSTYP]` | `[PERSON]`, `[SVNR]`, `[STEUER_ID]` |
| `i_tag` | Ersetzt durch `[ENTITÄTSTYP_N]` — gleicher Entitätstyp erhält gleichen Index | `[PERSON_1]` … `[PERSON_2]` |

---

## Konfiguration

Alle Optionen werden über ein einzelnes `config`-Dictionary übergeben:

```python
# Allowlist — nur diese Entitätstypen erkennen
config = {"set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]}}

# Denylist — alles außer diesen erkennen
config = {"set_entities": {"ignore": ["DATE", "TIME"]}}

# Vollständiges Konfigurationsbeispiel
config = {
    "set_entities": {"keep": ["PERSON", "SVNR", "STEUER_ID"]},

    # Minimale Konfidenz für einen Fund
    "score_threshold": 0.5,

    # Schutzmodus
    "mode": "anonymize",   # "anonymize" | "tag" | "i_tag"

    # Eigene Muster (siehe unten)
    "custom_patterns": [...],
}
```

### Eigene Muster

```python
from deutsch_deid import analyze, guard, custom_pattern

schueler_id = custom_pattern(
    name="SCHUELER_ID",
    regex=r"STU-\d{4}",
    score=0.9,
    context=["schüler", "student", "matrikelnummer"],   # Nahe Wörter erhöhen den Score
    anonymize_list=["STU-9999", "STU-8888"],            # Fake-Pool für den Anonymisierungsmodus
)

findings = analyze.text("Schüler STU-1234 hat Zugriff.", config={"custom_patterns": [schueler_id]})
guarded  = guard.text("Schüler STU-1234 hat Zugriff.",  config={"custom_patterns": [schueler_id]})
print(guarded["guarded_text"])
# "Schüler STU-9999 hat Zugriff."
```

---

## Scoring & Konfidenz

Jeder Fund trägt einen `score` zwischen 0 und 1. Die Scores werden durch ein Vier-Stufen-System bestimmt:

| Stufe | Bedingung | Beispiel-Score |
|------|-----------|---------------|
| `base` | Nur Regex-Treffer, keine weiteren Hinweise | 0,30 – 0,85 |
| `with_context` | Ein relevantes Schlüsselwort erscheint im selben Satz | bis zu 0,92 |
| `validated` | Algorithmische Prüfsumme bestanden (SVN-Check / ISO 7064 MOD 11,10) | 0,70 – 0,92 |
| `high_confidence` | Validierung *und* Kontextschlüsselwort vorhanden | 0,90 – 0,92 |

Das Context-Scoring ist **satzbewusst** — Kontextschlüsselwörter aus anderen Sätzen beeinflussen den Score nicht. Negative Kontextschlüsselwörter reduzieren die Konfidenz aktiv.

Mit `score_threshold` können Ergebnisse mit niedriger Konfidenz vor der Anonymisierung gefiltert werden.

---

## Paketstruktur

```
deutsch_deid/
├── types.py                  — Kerndatenstrukturen (RecognizerResult, Pattern, …)
├── analysis/
│   ├── analyzer.py           — PII-Analyse-Engine (GuardAnalyzer)
│   ├── context_awareness.py  — satzbewusstes Keyword-Scoring (ContextEnhancer)
│   └── overlap_resolver.py   — Span-Deduplizierung & Zusammenführung
├── anonymization/
│   ├── engine.py             — zustandsloser Anonymisierungs-Dispatcher (GuardEngine)
│   └── fake_data.py          — synthetische deutsche PII-Pools
├── recognizers/
│   ├── base.py               — EntityRecognizer / PatternRecognizer Basisklassen
│   ├── contact.py            — PHONE_NUMBER, EMAIL_ADDRESS, URL
│   ├── datetime.py           — DATE, TIME
│   ├── device.py             — IP_ADDRESS
│   ├── location.py           — ZIPCODE
│   ├── social.py             — SVNR (Sozialversicherungsnummer)
│   ├── tax.py                — STEUER_ID (USt-IdNr, Steuernummer, individuelle TIN)
│   └── spacy_recognizer.py   — NER-Erkenner (PERSON, LOCATION)
├── processors/
│   ├── text_processor.py     — Analyse-/Schutz-Pipelines für Klartext
│   └── doc_processor.py      — Dateilesen (.pdf / .docx / .txt) + Normalisierung
├── config/
│   ├── entities.py           — ALL_DE_ENTITY_TYPES-Liste
│   └── scoring.py            — EntityScoreProfile pro Entitätstyp
└── patterns/
    ├── german_keywords.py    — Deutsche Monatsnamen und Schlüsselwortlisten
    └── german_patterns.py    — Alle Regex-Muster
```

Die öffentliche Schnittstelle wird über `deutsch_deid/__init__.py` bereitgestellt:

```python
from deutsch_deid import analyze, guard, custom_pattern, ALL_DE_ENTITY_TYPES
```

---

## Datenschutz & Compliance

| Standard | Unterstützung durch diese Bibliothek |
|----------|----------------------|
| **DSGVO / GDPR** | De-identifiziert personenbezogene Daten vor Speicherung oder Übertragung; unterstützt Datensparsamkeitspflichten |
| **Schülerdatenschutz** | Bietet eine technische Kontrollschicht für die Pseudonymisierung von Schüler- und Lernenddaten in EdTech-Pipelines |
| **Mensch im Loop** | Automatische Erkennung ist probabilistisch — bei kritischen Datensätzen immer eine manuelle Überprüfung des anonymisierten Outputs einplanen |

> Diese Bibliothek ist ein **technisches Werkzeug**, keine rechtliche Garantie. Die gesamte Pipeline-Architektur, Zugriffskontrollen und Data-Governance-Richtlinien müssen die geltenden regulatorischen Anforderungen erfüllen.

---

## Interaktiver Schnellstart

Das Notebook [examples/quickstart.ipynb](examples/quickstart.ipynb) behandelt:

- Text- und Dokumentenanalyse mit allen 11 Entitätstypen
- SVNR-Erkennung (Sozialversicherungsnummer) & Validierung
- STEUER_ID — alle drei Varianten (USt-IdNr, Steuernummer, individuelle TIN)
- Alle drei Schutzmodi (`anonymize`, `tag`, `i_tag`)
- Eigene Muster mit Anonymisierungs-Pools
- Entitätsfilterung und Score-Schwellenwerte
- Vollständiges Beispiel mit deutschem Schülerausweis

---

## Lizenz

MIT-Lizenz — siehe [LICENSE](LICENSE) für Details.
