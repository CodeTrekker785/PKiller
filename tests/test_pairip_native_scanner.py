import tempfile
import unittest
import zipfile
from pathlib import Path

from pairip_native_scanner import scan_apk


class ScannerTests(unittest.TestCase):
    def test_detects_target_and_abi(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "sample.apk"
            with zipfile.ZipFile(apk, "w") as archive:
                archive.writestr("lib/arm64-v8a/libpairipcore.so", b"native")
                archive.writestr("lib/armeabi-v7a/libpairipcore.so", b"native32")
                archive.writestr("assets/pairip_config.dat", b"config")
                archive.writestr("classes.dex", b"dex")
            result = scan_apk(apk)
            self.assertTrue(result["valid_apk_zip"])
            matches = result["matches"]
            self.assertEqual(3, len(matches))
            target = next(m for m in matches if m["path"].startswith("lib/arm64"))
            self.assertEqual("arm64-v8a", target["abi"])
            self.assertTrue(target["exact_target"])

    def test_invalid_archive_reports_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "broken.apk"
            apk.write_text("not a zip", encoding="utf-8")
            result = scan_apk(apk)
            self.assertFalse(result["valid_apk_zip"])
            self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
