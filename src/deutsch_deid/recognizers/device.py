"""NETWORK recognizers: IP_ADDRESS."""
from deutsch_deid.recognizers.base import PatternRecognizer

from deutsch_deid.config.scoring import SCORE_PROFILES
from deutsch_deid.patterns.german_patterns import IPV4_REGEX, IPV6_REGEX
from deutsch_deid.recognizers._helpers import _p

_IP = SCORE_PROFILES["IP_ADDRESS"]


class DeIpRecognizer(PatternRecognizer):
    PATTERNS = [
        _p("ipv4", IPV4_REGEX, _IP.base),
        _p("ipv6", IPV6_REGEX, _IP.base),
    ]
    CONTEXT = [
        "ip", "ip-adresse", "ip address", "ipv4",
        "ipv6", "netzwerk", "host", "serveradresse",
    ]

    def __init__(self):
        super().__init__(
            supported_entity="IP_ADDRESS",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="de",
        )
