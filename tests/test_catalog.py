"""CatalogTests — test_tyrion_tools.py dan ajratilgan (asbob/mavzu bo'yicha)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import catalog  # noqa: E402



def _ns():
    import argparse
    return argparse.Namespace()


class CatalogTests(unittest.TestCase):
    """Katalog — tizimning yagona reestri."""

    def test_scan_returns_expected_shape(self) -> None:
        data = catalog.scan()
        self.assertEqual(data["schema"], catalog.SCHEMA)
        for key in ("counts", "items", "mirrors", "warnings"):
            self.assertIn(key, data)

    def test_counts_match_item_lists(self) -> None:
        data = catalog.scan()
        for layer in catalog.LAYERS:
            self.assertEqual(
                data["counts"][layer], len(data["items"][layer]),
                f"{layer}: sanoq ro'yxatga mos emas",
            )

    def test_knowledge_layer_is_populated(self) -> None:
        """Bilim va agent qatlami bo'sh bo'lsa — tizim sindirilgan."""
        counts = catalog.scan()["counts"]
        self.assertGreater(counts["wiki"], 0, "wiki/ bo'sh")
        self.assertGreater(counts["agents"], 0, "agents/ bo'sh")
        self.assertGreater(counts["skills"], 0, "skills/ bo'sh")

    def test_frontmatter_parsing(self) -> None:
        data = catalog.scan()
        notes = data["items"]["wiki"]
        self.assertTrue(notes, "wiki qayd yo'q")
        parsed = [n for n in notes if n.get("title")]
        self.assertGreater(len(parsed), 0, "hech bir qaydda name o'qilmadi")

    def test_frontmatter_catches_backslash_escape(self) -> None:
        """Qo'shtirnoq ichidagi backslash YAML'ni buzadi — katalog buni tutishi kerak."""
        backslash = chr(92)
        content = f'---\nname: x\nsource: "D:{backslash}tyrion{backslash}a.md"\n---\n\n# x\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            path.write_text(content, encoding="utf-8")
            fm = catalog.read_frontmatter(path)
            self.assertIn("_error", fm, "buzilgan YAML aniqlanmadi")

    def test_valid_frontmatter_has_no_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "note.md"
            path.write_text('---\nname: x\nsource: "vault/a.md"\n---\n\n# x\n', encoding="utf-8")
            fm = catalog.read_frontmatter(path)
            self.assertNotIn("_error", fm)

    def test_build_and_check_roundtrip(self) -> None:
        """build → check mos kelishi kerak (katalog haqiqatni aks ettiradi)."""
        before = catalog.MANIFEST.read_bytes() if catalog.MANIFEST.is_file() else None
        try:
            self.assertEqual(catalog.cmd_build(_ns()), 0)
            self.assertEqual(catalog.cmd_check(_ns()), 0)
        finally:
            if before is None and catalog.MANIFEST.is_file():
                catalog.MANIFEST.unlink()
            elif before is not None:
                catalog.MANIFEST.write_bytes(before)

    def test_check_detects_stale_manifest(self) -> None:
        """Katalog eskirsa `check` xato qaytarishi kerak (jim qolmasligi)."""
        original_bytes = catalog.MANIFEST.read_bytes()
        try:
            data = json.loads(original_bytes.decode("utf-8"))
            data["counts"]["wiki"] = -1
            catalog.MANIFEST.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertNotEqual(catalog.cmd_check(_ns()), 0, "eskirgan katalog sezilmadi")
        finally:
            catalog.MANIFEST.write_bytes(original_bytes)

    def test_mirror_status_classifies_pairs(self) -> None:
        items = {
            "commands": [{"name": "a", "path": "x", "sha256": "1"}, {"name": "b", "path": "y", "sha256": "2"}],
            "commands.mirror": [{"name": "a", "path": "x2", "sha256": "1"}, {"name": "b", "path": "y2", "sha256": "9"}],
        }
        statuses = {m["name"]: m["status"] for m in catalog.mirror_status(items)}
        self.assertEqual(statuses["a"], "identical")
        self.assertEqual(statuses["b"], "drifted")

    def test_human_claims_detects_mismatch(self) -> None:
        """Noto'g'ri sanoq berilsa, oddiy matndagi raqamlar mos emas deb topilsin."""
        claims = catalog.human_claims({"wiki": 999999})
        self.assertTrue(claims, "nazorat qilinadigan raqam yo'q")
        self.assertTrue(all(not c["ok"] for c in claims), claims)

    def test_human_claims_all_match_catalog(self) -> None:
        """INDEX.md/README.md/rules dagi raqamlar katalogdagi haqiqatga mos bo'lsin.

        Regressiya: bu sonlar bir vaqtda 41 bo'lib qolgan, wiki esa 42 edi —
        miya o'zi haqida yolg'on gapirardi.
        """
        claims = catalog.human_claims(catalog.scan()["counts"])
        self.assertTrue(claims, "claims registry bo'sh")
        for claim in claims:
            self.assertTrue(claim["ok"], f"{claim['file']}: {claim}")


if __name__ == "__main__":
    unittest.main()
