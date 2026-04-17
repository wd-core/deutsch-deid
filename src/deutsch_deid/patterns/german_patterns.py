"""
Regex patterns for German PII detection.
Covers dates, phones, emails, ZIP codes, URLs, IP addresses, times,
the German Sozialversicherungsnummer (SVNR), and tax identification numbers.
"""

from deutsch_deid.patterns.german_keywords import DATE_MONTHS_DE, DATE_MONTHS_EN

# ──────────────────────────── DATES ────────────────────────────
DATE_WITHOUT_WORDS_DE = (
    r"\b(?:\d{4}[/-]\d{1,2}[/-]\d{1,2}"
    r"|\d{4}\.\d{1,2}\.\d{1,2}"
    r"|\d{1,2}[/-]\d{1,2}[/-]\d{4}"
    r"|\d{1,2}\.\d{1,2}\.\d{4}"
    r"|\d{1,2}\.\d{1,2}\.\d{2})\b"
)

DATE_DD_MM_YY = (
    r"\b(0?[1-9]|[12]\d|30|31)[^\w\d\r\n:]"
    r"(0?[1-9]|1[0-2])[^\w\d\r\n:](\d{4}|\d{2})\b"
)

DATE_YY_MM_DD = (
    r"\b(\d{2}|\d{4})[^\w\d\r\n:]"
    r"(0?[1-9]|1[0-2])[^\w\d\r\n:](0?[1-9]|[12]\d|30|31)\b"
)

# "12. Januar 2024" / "3. Maerz" / "15. Juli 1998"
DATE_WITH_WORDS_DE = (
    r"(?i)\b(\d{1,2})\.\s+"
    f"({DATE_MONTHS_DE})"
    r"(?:\s+\d{4})?\b"
)

# Fuzzy: any "DD MonthWord YYYY" combination
DATE_WORDS_FUZZY_DE = (
    r"(?i)\b(\d{1,2})\.?\s+([a-zA-Z]{3,10})\s+(\d{4})\b"
)

# ISO-8601 timestamp: 2024-03-15T13:45:00 (with optional fractional seconds)
DATE_ISO_TIMESTAMP = (
    r"\b\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])"
    r"T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?\b"
)

# English ordinal dates: "July 21st, 1998" / "21st July 1998"
_MONTHS_EN = DATE_MONTHS_EN
_ORDINAL   = r"\d{1,2}(?:st|nd|rd|th)"
DATE_EN_ORDINAL = (
    r"(?i)\b(?:"
    rf"(?:{_MONTHS_EN})\s+{_ORDINAL},?\s*\d{{4}}"
    rf"|{_ORDINAL}\s+(?:{_MONTHS_EN}),?\s*\d{{4}}"
    r")\b"
)

# English month + day + year: "July 4 1776" / "December 25, 2023"
DATE_EN_WORDS = (
    r"(?i)\b(?:"
    rf"(?:{_MONTHS_EN})\s+\d{{1,2}},?\s*\d{{4}}"
    rf"|\d{{1,2}}\s+(?:{_MONTHS_EN}),?\s*\d{{4}}"
    r")\b"
)

# ──────────────────────────── PHONE ────────────────────────────
# German mobile: +49 15x / 16x / 17x  (Telekom, Vodafone, O2, etc.)
PHONE_DE_MOBILE = r"\+49[\s\-]?1[5-7]\d[\s\-]?\d{3,4}[\s\-]?\d{4,5}"

# Structured EU/DE format: +CC [AAA] NNNN NNNN
EU_PHONES = r"(?<!\w)(?:\+|00)\d{1,3}[\s.\-]?(?:\(?\d{2,3}\)?[\s.\-]?)?\d{3,4}[\s.\-]?\d{4}\b"

# Flexible international: +CC followed by 2-5 digit groups
PHONE_INTL = r"\+\d{1,3}(?:[\s.\-]\d{1,6}){2,5}\b"

# German local numbers: 0XXX / 030 / 089 / 0800 etc.
LOCAL_PHONES = (
    r"\b(?:0\d{1,4}|00\d{1,3}|\+\d{1,3})"
    r"[\s.\-]?\d{1,4}(?:[\s.\-]?\d{2,4}){1,3}\b"
)

# ──────────────────────────── EMAIL ────────────────────────────
EMAIL_REGEX = (
    r"[a-zA-Z0-9._%+-]+@"
    r"(?:\[(?:\d{1,3}\.){3}\d{1,3}\]"
    r"|(?:[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})*|[a-zA-Z0-9-]+))"
)

# ──────────────────────────── ZIP CODE ─────────────────────────
# German postal codes: exactly 5 digits (e.g. 10115, 80331, 20095)
ZIP_REGEX_DE = r"\b\d{5}\b"

# ──────────────────────────── IP ADDRESS ───────────────────────
IPV4_REGEX = r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b"

# Full (8-group) and compressed (::) IPv6 forms
IPV6_REGEX = (
    r"\b(?:"
    r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}"
    r"|(?:[0-9a-fA-F]{1,4}:)*::(?::[0-9a-fA-F]{1,4})*"
    r"|::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}"
    r"|::)"
    r"\b"
)

# ──────────────────────────── WEBSITE / URL ────────────────────
# Schemed URLs: http(s):// or ftp://
WEBSITE_REGEX = (
    r"(?:https?|ftp)://(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}"
    r"(?::\d+)?(?:/[\w~;/\\?%&=#-]*)?"
)

# Schemeless www.* URLs
WEBSITE_REGEX_WWW = (
    r"\bwww\.(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}"
    r"(?::\d+)?(?:/[\w~;/\\?%&=#-]*)?"
)

# ──────────────────── STEUER-IDENTIFIKATION ────────────────────
# 1) USt-IdNr / VAT ID (intra-community): DE + 9 digits
#    e.g. "DE123456789"  /  "DE 123 456 789"
UST_ID_REGEX = r"\bDE[\s]?\d{3}[\s]?\d{3}[\s]?\d{3}\b"

# 2) Steuernummer — domestic business tax number (slash-delimited)
#    e.g. "12/345/67890"  /  "123/456/78901"  /  "21 5 109 31717"
STEUERNUMMER_REGEX = (
    r"\b\d{2,3}[\s/]\d{3,5}[\s/]\d{4,5}\b"
)

# 3) Steuerliche Identifikationsnummer — individual 11-digit TIN
#    First digit 1-9, total 11 digits, check digit via ISO 7064 MOD 11,10
#    e.g. "12345678903"
STEUER_INDIVIDUAL_REGEX = r"\b[1-9]\d{10}\b"

# ──────────────────── SOZIALVERSICHERUNGSNUMMER ────────────────
# Structure: [Bereich 2d][DDMMYY 6d][Buchstabe A-Z][Serien 2d][Prüfziffer 1d]
# E.g.: "12 150780 J 001"  /  "12150780J001"
SVNR_DE_REGEX = r"\b\d{2}[\s-]?\d{6}[\s-]?[A-Z][\s-]?\d{3}\b"

# ──────────────────────────── TIME ─────────────────────────────
# Matches: "14:30", "09:15 Uhr", "9 Uhr", "9.30 Uhr", "2:30 PM"
# The dot-separated branch uses (?!\.\d) to avoid swallowing the
# first two components of a date like "10.06.2026" as a time.
TIME_REGEX = (
    r"(?i)\b(?:"
    r"(?:1[0-2]|0?[1-9])[:\.][0-5]\d\s*(?:AM|PM|a\.m\.|p\.m\.)"
    r"|(?:[01]?\d|2[0-3])\s*(?:Uhr|uhr|h)\s*(?:[0-5]\d)?"
    r"|(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?(?:\s*(?:Uhr|uhr))?"
    r"|(?:[01]?\d|2[0-3])\.[0-5]\d(?!\.\d)(?:\s*(?:Uhr|uhr))?"
    r")\b"
)
