"""market_locale.py: bozor aniqlash ustuvorligi, valyuta formatlash, til normallashtirish, API versiya (to'g'ridan-to'g'ri testlar)."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from tests._helpers import VAULT  # noqa: F401  (tools/ ni sys.path ga qo'shadi)

import market_locale as ml  # noqa: E402


def _clean_env():
    return mock.patch.dict(os.environ, {k: v for k, v in os.environ.items() if k not in ("TYRION_MARKET", "META_GRAPH_API_VERSION")}, clear=True)


class DetectMarketTests(unittest.TestCase):
    def test_explicit_market_wins_over_text(self) -> None:
        with _clean_env():
            res = ml.detect_market(text="Toshkentda reklama", explicit_market="us")
        self.assertEqual((res["market_id"], res["detection_source"]), ("us", "explicit"))

    def test_env_override_used_when_no_explicit(self) -> None:
        with mock.patch.dict(os.environ, {"TYRION_MARKET": "eu"}):
            self.assertEqual(ml.detect_market(text="hello")["market_id"], "eu")

    def test_unknown_explicit_market_falls_through(self) -> None:
        with _clean_env():
            res = ml.detect_market(text="ads in Dubai", explicit_market="atlantis")
        self.assertEqual(res["market_id"], "mena")

    def test_geo_lookup_beats_text_keywords(self) -> None:
        with _clean_env():
            geo_key = next(iter(ml.GEO_TO_MARKET))
            res = ml.detect_market(text="Toshkent", geo=geo_key)
        self.assertEqual(res["market_id"], ml.GEO_TO_MARKET[geo_key])
        self.assertTrue(res["detection_source"].startswith("geo:"))

    def test_text_keywords_cover_scripts_and_regions(self) -> None:
        cases = {"Reklama Toshkentda": "uz", "реклама в Ташкенте": "uz", "campaigns in Berlin GDPR": "eu", "London brand": "uk",
                 "Texas CCPA": "us", "Riyadh Tabby": "mena", "Mumbai UPI": "in", "Singapore GrabPay": "sea", "Brazil PIX": "latam"}
        with _clean_env():
            for text, want in cases.items():
                self.assertEqual(ml.detect_market(text=text)["market_id"], want, text)

    def test_currency_and_language_fallbacks(self) -> None:
        with _clean_env():
            self.assertEqual(ml.detect_market(currency="uzs")["market_id"], "uz")
            self.assertEqual(ml.detect_market(detected_lang="uz_latin")["market_id"], "uz")
            res = ml.detect_market(text="plain english request")
        self.assertEqual((res["market_id"], res["detection_source"]), ("global", "default_global"))

    def test_rtl_language_flag(self) -> None:
        with _clean_env():
            res = ml.detect_market(text="Dubai ads", detected_lang="ar")
        self.assertTrue(res["is_rtl"])
        self.assertIsNotNone(res["rtl_formatting_note"])


class FormattingTests(unittest.TestCase):
    def test_format_and_round_currency(self) -> None:
        self.assertEqual(ml.format_currency(1500000, "UZS"), "1,500,000 UZS")
        self.assertEqual(ml.format_currency(99.5, "EUR"), "€99.50")
        self.assertEqual(ml.format_currency(1234.567, "XYZ"), "XYZ 1,234.57")
        self.assertEqual(ml.round_currency(12500.7, "JPY"), 12501)
        self.assertEqual(ml.round_currency(1.005 + 1, "USD"), 2.0)

    def test_language_normalisation(self) -> None:
        self.assertEqual(ml.normalize_bcp47_language("uz_latin")["bcp47"], "uz-Latn")
        self.assertEqual(ml.normalize_bcp47_language("uz_cyrillic")["bcp47"], "uz-Cyrl")
        self.assertEqual(ml.normalize_bcp47_language("pt")["bcp47"], "pt-BR")
        self.assertTrue(ml.is_rtl_language("ar-SA"))
        self.assertFalse(ml.is_rtl_language("en"))
        self.assertEqual(ml.normalize_bcp47_language("")["bcp47"], "en")


class PacksAndLocalesTests(unittest.TestCase):
    def test_every_supported_market_has_a_loadable_pack(self) -> None:
        for m in ml.SUPPORTED_MARKETS:
            pack = ml.load_market_pack(m)
            self.assertEqual(pack["market_id"], m)
            self.assertTrue(pack["default_currency"])

    def test_unknown_market_falls_back_to_global(self) -> None:
        with _clean_env():
            self.assertEqual(ml.load_market_pack("narnia")["market_id"], "global")

    def test_locale_messages_fallback(self) -> None:
        self.assertTrue(ml.load_locale_messages("uz-Latn"))
        self.assertTrue(ml.load_locale_messages("ru-RU"))
        self.assertEqual(ml.load_locale_messages("xx"), ml.load_locale_messages("en"))


class ApiVersionTests(unittest.TestCase):
    def test_default_current_and_deprecated(self) -> None:
        with _clean_env(), mock.patch.object(ml, "VAULT", VAULT / "nonexistent-dir"):
            info = ml.get_configured_api_version()
            self.assertEqual((info["version"], info["is_deprecated"]), ("v26.0", False))
            with mock.patch.dict(os.environ, {"META_GRAPH_API_VERSION": "v23.0"}):
                info = ml.get_configured_api_version()
            self.assertTrue(info["is_deprecated"])
            self.assertIn("v26.0", info["warning"])
            with mock.patch.dict(os.environ, {"META_GRAPH_API_VERSION": "27"}):
                self.assertEqual(ml.get_configured_api_version()["version"], "v27")


if __name__ == "__main__":
    unittest.main()
