"""
Pools of realistic synthetic PII values for anonymization mode.
Each entity type has a list of believable fake replacements.
The FakeDataProvider hands them out consistently: the same original value
always maps to the same fake within a single document.

Sub-pools
---------
LOCATION entities are routed to LOCATION_STREET when the original span
looks like a street name (contains common German street suffixes such as
"straße", "weg", "allee", etc.).

STEUER_ID entities are routed to STEUER_ID_UST (USt-IdNr), STEUER_ID_STN
(Steuernummer with slash/space), or the default STEUER_ID pool (individual
TIN) based on the format of the original matched text.
"""

import re
from itertools import cycle
from typing import Dict, Iterator, List

# ── Sub-pool routing helpers ──────────────────────────────────────────────────

_STREET_RE = re.compile(
    r"(?i)(stra[sß]e|str\.|allee|weg|gasse|platz|ring|damm|ufer|chaussee|boulevard)\b"
)
_UST_ID_RE = re.compile(r"(?i)^DE\s?\d")
_STEUERNUMMER_RE = re.compile(r"^\d{2,3}[\s/]\d")

FAKE_POOLS: Dict[str, List[str]] = {
    "PERSON": [
        "Lukas Bauer", "Anna Schneider", "Maximilian Fischer",
        "Laura Wagner", "Felix Hoffmann", "Sophie Schulz",
        "Jonas Weber", "Lea Richter", "Tobias Koch", "Hannah Klein",
    ],
    # Cities — used when a LOCATION span does not look like a street name
    "LOCATION": [
        "Berlin", "Hamburg", "Muenchen", "Koeln", "Frankfurt am Main",
        "Stuttgart", "Duesseldorf", "Leipzig", "Dortmund", "Bremen",
    ],
    # Streets — used when a LOCATION span looks like a street name
    "LOCATION_STREET": [
        "Hauptstraße", "Gartenweg", "Schulstraße", "Lindenallee",
        "Bahnhofstraße", "Rosenweg", "Kirchstraße", "Waldweg",
        "Friedrichstraße", "Bergstraße",
    ],
    "DATE": [
        "14. Januar 1983", "27. April 1990", "03. September 1975",
        "19. Juni 2001", "08. Dezember 1968", "22. Februar 1995",
        "11. Oktober 1987", "30. Maerz 2003", "05. Juli 1971",
        "16. August 1999",
    ],
    "TIME": [
        "09:15 Uhr", "11:30 Uhr", "13:45 Uhr", "15:00 Uhr", "16:30 Uhr",
        "08:00 Uhr", "10:00 Uhr", "14:15 Uhr", "17:00 Uhr", "18:30 Uhr",
    ],
    "PHONE_NUMBER": [
        "+49 151 87654321", "+49 162 23456789", "+49 30 7654321",
        "+49 89 8765432", "+49 171 34567890", "+49 711 6543210",
        "+49 152 45678901", "+49 40 5432109", "+49 176 56789012",
        "+49 221 4321098",
    ],
    "EMAIL_ADDRESS": [
        "l.bauer@beispiel.de", "a.schneider@unternehmen.de",
        "m.fischer@mail.de", "k.hoffmann@info.de",
        "s.wagner@webmail.de", "f.richter@buero.de",
        "j.weber@post.de", "h.schulz@digital.de",
        "t.koch@postfach.de", "c.klein@netzwerk.de",
    ],
    "ZIPCODE": [
        "10115", "20095", "80331", "50667", "60311",
        "70173", "40213", "04109", "44135", "28195",
    ],
    "IP_ADDRESS": [
        "10.20.30.40", "172.16.0.1", "10.0.0.5",
        "192.0.2.1", "198.51.100.2", "203.0.113.3",
        "2001:0db8:0000:0000:0000:0000:0000:0001",
        "2001:0db8:85a3:0000:0000:8a2e:0370:1111",
        "fe80:0000:0000:0000:0202:b3ff:fe1e:8329",
        "fc00:0000:0000:0001:0000:0000:0000:0001",
    ],
    # Individual TIN (steuerliche Identifikationsnummer, 11-digit) — default
    "STEUER_ID": [
        "12345678903", "87654321095", "23456789013", "34567890125",
        "45678901239", "56789012343", "67890123455", "78901234569",
        "13579246808", "24680135792",
    ],
    # USt-IdNr (DE + 9 digits) — routed when original starts with "DE"
    "STEUER_ID_UST": [
        "DE123456788", "DE876543219", "DE234567894", "DE345678906",
        "DE456789019", "DE567890129", "DE678901231", "DE789012348",
        "DE135792460", "DE246801352",
    ],
    # Steuernummer (slash/space format) — routed when original has slash or digit-space-digit
    "STEUER_ID_STN": [
        "12/345/67890", "81/815/08156", "21/815/08155", "28/321/09876",
        "93/422/41290", "26/123/45678", "55/678/90123", "47/234/56789",
        "38/891/23456", "62/456/78901",
    ],
    "SVNR": [
        "12 150780 J 009", "65 230561 M 013", "45 120893 S 029",
        "32 050472 B 042", "78 010190 K 056", "56 290785 W 039",
        "22 110356 H 067", "89 310882 R 071", "43 180968 F 081",
        "67 250277 N 090",
    ],
    "URL": [
        "https://www.beispiel.de/seite",
        "https://portal.dienst.de/konto",
        "https://www.unternehmen.de/info",
        "https://mein.portal.de/status",
        "https://www.onlineshop.de/bestellung",
        "https://app.plattform.de/profil",
        "https://service.anbieter.de/ticket",
        "https://www.nachrichten.de/artikel",
        "https://kunde.bank.de/uebersicht",
        "https://umgebung.system.de/dashboard",
    ],
}


class FakeDataProvider:
    """
    Hands out fake values for each entity type.
    Within one document, the same original text always gets the same fake
    (consistent substitution). Cycles through the pool if there are more
    unique values than pool entries.

    Sub-pool routing
    ----------------
    LOCATION spans that look like street names (contain common German street
    suffixes) are served from the LOCATION_STREET pool instead of LOCATION.

    STEUER_ID spans are routed to STEUER_ID_UST (USt-IdNr format) when the
    original starts with "DE", to STEUER_ID_STN (slash/space Steuernummer)
    when the original contains a slash or digit-space-digit pattern, and to
    the default STEUER_ID pool (individual 11-digit TIN) otherwise.
    """

    def __init__(self):
        self._cycles: Dict[str, Iterator[str]] = {
            entity: cycle(pool) for entity, pool in FAKE_POOLS.items()
        }
        self._seen: Dict[str, Dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Sub-pool routing
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_pool_key(entity_type: str, original: str) -> str:
        """Return the FAKE_POOLS key to use for this (entity, original) pair."""
        if entity_type == "LOCATION":
            if _STREET_RE.search(original):
                return "LOCATION_STREET"
        if entity_type == "STEUER_ID":
            if _UST_ID_RE.match(original.strip()):
                return "STEUER_ID_UST"
            if _STEUERNUMMER_RE.match(original.strip()):
                return "STEUER_ID_STN"
        return entity_type

    # ------------------------------------------------------------------

    def get(self, entity_type: str, original: str) -> str:
        entity_map = self._seen.setdefault(entity_type, {})
        if original not in entity_map:
            pool_key = self._resolve_pool_key(entity_type, original)
            pool = self._cycles.get(pool_key)
            if pool:
                candidate = original
                for _ in range(len(FAKE_POOLS.get(pool_key, ["_"]))):
                    candidate = next(pool)
                    if candidate != original:
                        break
                if candidate == original:
                    candidate = f"[{entity_type}]"
                entity_map[original] = candidate
            else:
                entity_map[original] = f"[{entity_type}]"
        return entity_map[original]
