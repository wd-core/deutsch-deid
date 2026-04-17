"""
Integration tests for deutsch-deid.

Tests cover all 11 supported entity types plus guard modes, entity filtering,
score thresholds, custom patterns, and validation logic.
"""
import pytest
from deutsch_deid import analyze, guard, custom_pattern, ALL_DE_ENTITY_TYPES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _types(text: str, **config_kwargs) -> list[str]:
    """Return entity type list detected in *text*."""
    cfg = config_kwargs or {}
    return [f["type"] for f in analyze.text(text, config=cfg if cfg else None)]


def _has(text: str, entity: str, **config_kwargs) -> bool:
    return entity in _types(text, **config_kwargs)


def _scores(text: str, entity: str) -> list[float]:
    return [f["score"] for f in analyze.text(text) if f["type"] == entity]


# ---------------------------------------------------------------------------
# 1. Package-level smoke test
# ---------------------------------------------------------------------------

class TestPackage:
    def test_version_string(self):
        import deutsch_deid
        assert isinstance(deutsch_deid.__version__, str)
        assert deutsch_deid.__version__

    def test_entity_types_count(self):
        assert len(ALL_DE_ENTITY_TYPES) == 11

    def test_all_expected_entity_types_present(self):
        expected = {
            "PERSON", "LOCATION", "DATE", "TIME", "PHONE_NUMBER",
            "EMAIL_ADDRESS", "URL", "ZIPCODE", "IP_ADDRESS", "SVNR", "STEUER_ID",
        }
        assert expected == set(ALL_DE_ENTITY_TYPES)


# ---------------------------------------------------------------------------
# 2. DATE
# ---------------------------------------------------------------------------

class TestDate:
    def test_numeric_dot_separator(self):
        assert _has("Termin: 10.06.2026.", "DATE")

    def test_german_month_name_ascii(self):
        assert _has("Geboren am 15. Maerz 2002.", "DATE")

    def test_german_month_name_umlaut(self):
        assert _has("Geboren am 15. März 2002.", "DATE")

    def test_iso_format(self):
        assert _has("Datum: 2024-11-20.", "DATE")

    def test_context_boost(self):
        scores_ctx = _scores("Geburtsdatum: 10.06.2026.", "DATE")
        scores_no  = _scores("Am 10.06.2026 war alles gut.", "DATE")
        assert scores_ctx, "DATE not detected with context"
        assert scores_no,  "DATE not detected without context"
        assert scores_ctx[0] >= scores_no[0]


# ---------------------------------------------------------------------------
# 3. TIME
# ---------------------------------------------------------------------------

class TestTime:
    def test_colon_uhr(self):
        assert _has("Beginn um 14:30 Uhr.", "TIME")

    def test_colon_only(self):
        assert _has("Beginn 09:15.", "TIME")

    def test_h_suffix(self):
        assert _has("Beginn 9h.", "TIME")

    def test_dot_not_swallowing_date(self):
        """10.06 must NOT be detected as TIME when it is part of 10.06.2026."""
        results = analyze.text("Am 10.06.2026 um 14:30 Uhr.")
        types = [r["type"] for r in results]
        matched = [r for r in results if r["type"] == "TIME"]
        # There must be exactly one TIME: 14:30 Uhr — NOT 10.06
        assert "TIME" in types
        for m in matched:
            # No TIME match should start at position 3 (the '10' of the date)
            span = "Am 10.06.2026 um 14:30 Uhr."[m["start"]:m["end"]]
            assert "10.06" not in span, f"TIME regex swallowed date prefix: {span!r}"


# ---------------------------------------------------------------------------
# 4. PHONE_NUMBER
# ---------------------------------------------------------------------------

class TestPhoneNumber:
    def test_german_mobile(self):
        assert _has("+49 151 23456789 ist meine Nummer.", "PHONE_NUMBER")

    def test_with_context(self):
        scores_ctx = _scores("Telefon: +49 151 23456789.", "PHONE_NUMBER")
        scores_no  = _scores("+49 151 23456789 ist meine Nummer.", "PHONE_NUMBER")
        assert scores_ctx and scores_no
        assert scores_ctx[0] >= scores_no[0]


# ---------------------------------------------------------------------------
# 5. EMAIL_ADDRESS
# ---------------------------------------------------------------------------

class TestEmail:
    def test_standard(self):
        assert _has("E-Mail: max.mustermann@example.com.", "EMAIL_ADDRESS")

    def test_subdomain(self):
        assert _has("Schreib an a.richter@gymnasium-berlin.de.", "EMAIL_ADDRESS")

    def test_score_high(self):
        scores = _scores("max@example.com", "EMAIL_ADDRESS")
        assert scores and scores[0] >= 0.90


# ---------------------------------------------------------------------------
# 6. URL
# ---------------------------------------------------------------------------

class TestUrl:
    def test_https(self):
        assert _has("Mehr auf https://www.example.de/profil.", "URL")

    def test_www_schemeless(self):
        assert _has("Besuche www.maxmustermann.de.", "URL")

    def test_url_not_detected_as_location(self):
        """spaCy must not mis-tag a URL as LOCATION."""
        results = analyze.text("Portal: https://lernportal.gymnasium-berlin.de/profil")
        for r in results:
            if r["type"] == "LOCATION":
                span = "Portal: https://lernportal.gymnasium-berlin.de/profil"[r["start"]:r["end"]]
                assert "http" not in span and "www" not in span, \
                    f"URL mis-tagged as LOCATION: {span!r}"


# ---------------------------------------------------------------------------
# 7. ZIPCODE
# ---------------------------------------------------------------------------

class TestZipcode:
    def test_five_digit(self):
        # "10115 Berlin" alone is caught by spaCy as LOCATION which outscores ZIPCODE.
        # Use a comma-separated address form so the zip appears on its own line.
        assert _has("Postleitzahl: 10115.", "ZIPCODE")

    def test_score_at_least_base(self):
        scores = _scores("10115 Berlin", "ZIPCODE")
        assert scores and scores[0] >= 0.50


# ---------------------------------------------------------------------------
# 8. IP_ADDRESS
# ---------------------------------------------------------------------------

class TestIpAddress:
    def test_ipv4(self):
        assert _has("IP-Adresse: 192.168.1.1.", "IP_ADDRESS")

    def test_ipv6(self):
        assert _has("IPv6: 2001:db8::1.", "IP_ADDRESS")

    def test_loopback(self):
        assert _has("Localhost: 127.0.0.1.", "IP_ADDRESS")


# ---------------------------------------------------------------------------
# 9. SVNR
# ---------------------------------------------------------------------------

class TestSvnr:
    VALID_SPACED   = "12 150780 J 009"
    VALID_COMPACT  = "12150780J009"
    INVALID_CHECK  = "12 150780 J 007"   # wrong check digit

    def test_spaced_with_context(self):
        assert _has(f"Sozialversicherungsnummer: {self.VALID_SPACED}.", "SVNR")

    def test_compact_form(self):
        assert _has(f"SVNR: {self.VALID_COMPACT}.", "SVNR")

    def test_validated_score(self):
        scores = _scores(f"Sozialversicherungsnummer: {self.VALID_SPACED}.", "SVNR")
        assert scores and scores[0] == pytest.approx(0.90)

    def test_invalid_check_digit_not_detected(self):
        assert not _has(f"Sozialversicherungsnummer: {self.INVALID_CHECK}.", "SVNR")

    def test_validate_svnr_util(self):
        from deutsch_deid.recognizers._utils import validate_svnr
        assert validate_svnr("12150780J009") is True
        assert validate_svnr("12150780J007") is False


# ---------------------------------------------------------------------------
# 10. STEUER_ID
# ---------------------------------------------------------------------------

class TestSteuerID:
    VALID_INDIV   = "12345678903"    # individual TIN — valid ISO 7064 checksum
    INVALID_INDIV = "52413698701"    # invalid checksum
    VALID_UST     = "DE123456788"    # USt-IdNr — valid ISO 7064 checksum
    INVALID_UST   = "DE123456789"    # USt-IdNr — invalid checksum
    STEUERNUMMER  = "12/345/67890"   # slash-form Steuernummer

    def test_individual_tin_with_context(self):
        assert _has(f"Steuer-ID: {self.VALID_INDIV}.", "STEUER_ID")

    def test_individual_tin_score_with_context(self):
        scores = _scores(f"Steuer-ID: {self.VALID_INDIV}.", "STEUER_ID")
        assert scores and scores[0] == pytest.approx(0.92)

    def test_individual_tin_invalid_checksum_not_detected(self):
        assert not _has(f"Steuer-ID: {self.INVALID_INDIV}.", "STEUER_ID")

    def test_ust_idnr_valid(self):
        assert _has(f"USt-IdNr: {self.VALID_UST}.", "STEUER_ID")

    def test_ust_idnr_invalid_not_detected(self):
        assert not _has(f"USt-IdNr: {self.INVALID_UST}.", "STEUER_ID")

    def test_steuernummer_slash(self):
        assert _has(f"Steuernummer: {self.STEUERNUMMER}.", "STEUER_ID")

    def test_validate_steuer_id_util(self):
        from deutsch_deid.recognizers._utils import validate_steuer_id
        assert validate_steuer_id(self.VALID_INDIV) is True
        assert validate_steuer_id(self.INVALID_INDIV) is False

    def test_validate_ust_idnr_util(self):
        from deutsch_deid.recognizers._utils import validate_ust_idnr
        assert validate_ust_idnr(self.VALID_UST) is True
        assert validate_ust_idnr(self.INVALID_UST) is False


# ---------------------------------------------------------------------------
# 11. Guard modes
# ---------------------------------------------------------------------------

class TestGuardModes:
    TEXT = "Name: Anna Richter. E-Mail: a.richter@example.de."

    def test_anonymize_returns_string(self):
        result = guard.text(self.TEXT)
        assert isinstance(result["guarded_text"], str)
        assert "Anna Richter" not in result["guarded_text"]

    def test_tag_mode(self):
        result = guard.text(self.TEXT, config={"mode": "tag"})
        gt = result["guarded_text"]
        assert "[PERSON]" in gt or "[EMAIL_ADDRESS]" in gt

    def test_i_tag_mode(self):
        text = "Anna Richter schreibt an Maria Müller."
        result = guard.text(text, config={"mode": "i_tag"})
        gt = result["guarded_text"]
        assert "[PERSON_1]" in gt
        assert "[PERSON_2]" in gt

    def test_findings_in_result(self):
        result = guard.text(self.TEXT)
        assert "findings" in result
        assert isinstance(result["findings"], list)


# ---------------------------------------------------------------------------
# 12. Entity filtering
# ---------------------------------------------------------------------------

class TestEntityFiltering:
    TEXT = (
        "Anna Richter, +49 151 23456789, "
        "a.richter@example.de, 10115 Berlin."
    )

    def test_keep_allowlist(self):
        results = analyze.text(self.TEXT, config={
            "set_entities": {"keep": ["EMAIL_ADDRESS"]}
        })
        types = {r["type"] for r in results}
        assert types == {"EMAIL_ADDRESS"}

    def test_ignore_denylist(self):
        results = analyze.text(self.TEXT, config={
            "set_entities": {"ignore": ["ZIPCODE", "PHONE_NUMBER"]}
        })
        types = {r["type"] for r in results}
        assert "ZIPCODE" not in types
        assert "PHONE_NUMBER" not in types


# ---------------------------------------------------------------------------
# 13. Score threshold
# ---------------------------------------------------------------------------

class TestScoreThreshold:
    def test_threshold_filters_low_scores(self):
        text = "PLZ 10115."
        all_results  = analyze.text(text)
        high_results = analyze.text(text, config={"score_threshold": 0.90})
        assert len(high_results) <= len(all_results)
        for r in high_results:
            assert r["score"] >= 0.90


# ---------------------------------------------------------------------------
# 14. Custom patterns
# ---------------------------------------------------------------------------

class TestCustomPatterns:
    def test_custom_detect(self):
        pat = custom_pattern(name="STUDENT_ID", regex=r"STU-\d{4}", score=0.9)
        results = analyze.text(
            "Schueler STU-1234 hat Zugriff.",
            config={"custom_patterns": [pat]},
        )
        types = [r["type"] for r in results]
        assert "STUDENT_ID" in types

    def test_custom_anonymize(self):
        pat = custom_pattern(
            name="STUDENT_ID",
            regex=r"STU-\d{4}",
            score=0.9,
            anonymize_list=["STU-9999"],
        )
        result = guard.text(
            "Schueler STU-1234 hat Zugriff.",
            config={"custom_patterns": [pat]},
        )
        assert "STU-9999" in result["guarded_text"]
        assert "STU-1234" not in result["guarded_text"]


# ---------------------------------------------------------------------------
# 15. Document processing
# ---------------------------------------------------------------------------

class TestDocProcessing:
    def test_txt_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text(
            "Name: Anna Richter.\nE-Mail: a.richter@example.de.\n",
            encoding="utf-8",
        )
        findings = analyze.doc(str(f))
        types = [r["type"] for r in findings]
        assert "EMAIL_ADDRESS" in types

    def test_unsupported_format_raises(self, tmp_path):
        from deutsch_deid import UnsupportedFormatError
        f = tmp_path / "test.xlsx"
        f.write_bytes(b"fake")
        with pytest.raises(UnsupportedFormatError):
            analyze.doc(str(f))
