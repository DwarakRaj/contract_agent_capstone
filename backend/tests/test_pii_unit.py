import unittest
import pytest
from backend.governance.pii_engine import PIIEngine

class TestPIIEngine(unittest.TestCase):
    @pytest.mark.unit
    def test_email_detection(self):
        text = "My email is test@example.com."
        matches = PIIEngine.detect(text)
        self.assertTrue(any(m[0] == "EMAIL" and m[1] == "test@example.com" for m in matches))
        redacted = PIIEngine.redact(text)
        self.assertEqual(redacted, "My email is [REDACTED_EMAIL].")

    @pytest.mark.unit
    def test_phone_detection(self):
        text = "Call me at (555) 123-4567 or 123.456.7890."
        matches = PIIEngine.detect(text)
        self.assertTrue(any(m[0] == "PHONE" for m in matches))
        redacted = PIIEngine.redact(text)
        self.assertIn("[REDACTED_PHONE]", redacted)

    @pytest.mark.unit
    def test_ssn_detection(self):
        text = "SSN: 123-45-6789"
        matches = PIIEngine.detect(text)
        self.assertTrue(any(m[0] == "SSN" for m in matches))
        redacted = PIIEngine.redact(text)
        self.assertEqual(redacted, "SSN: [REDACTED_SSN]")

    @pytest.mark.unit
    def test_credit_card_detection(self):
        text = "Card: 1234-5678-9012-3456"
        matches = PIIEngine.detect(text)
        self.assertTrue(any(m[0] == "CREDIT_CARD" for m in matches))
        redacted = PIIEngine.redact(text)
        self.assertEqual(redacted, "Card: [REDACTED_CREDIT_CARD]")

    def test_mixed_pii(self):
        text = "User user@site.com with phone 555-555-5555"
        redacted = PIIEngine.redact(text)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)

if __name__ == "__main__":
    unittest.main()
