"""
German-specific keywords for PII detection.
"""

# German month names (long + short forms)
DATE_MONTHS_DE = (
    r"januar|jan|februar|feb|maerz|märz|mär|mrz|april|apr|mai|juni|jun"
    r"|juli|jul|august|aug|september|sep|oktober|okt|november|nov|dezember|dez"
)

# English month names (for cross-lingual / ISO-locale datasets)
DATE_MONTHS_EN = (
    r"january|february|march|april|may|june|july"
    r"|august|september|october|november|december"
)
