import tempfile
import unittest
import zipfile
from pathlib import Path

from pairip_native_scanner import scan_apk, scan_dex_strings


def make_test_dex(strings):
    """Build a tiny valid-header DEX fixture with a string_ids table."""
    data = bytearray(112)
    data[:8] = b"dex\n035\0"
    string_ids_off = len(data)
    data.extend(b"\0" * (4 * len(strings)))
    data[56:60] = len(strings).to_bytes(4, "little")
    data[60:64] = string_ids_off.to_bytes(4, "little")
    for index, value in enumerate(strings):
        encoded = value.encode("utf-8")
        string_offset = len(data)
        data[string_ids_off + index * 4:string_ids_off + index * 4 + 4] = string_offset.to_bytes(4, "little")
        # All fixture strings are ASCII, so byte length equals UTF-16 length.
        data.append(len(value))
        data.extend(encoded)
        data.append(0)
    return bytes(data)


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
            self.assertEqual(3, len(result["matches"]))
            target = next(m for m in result["matches"] if m["path"].startswith("lib/arm64"))
            self.assertEqual("arm64-v8a", target["abi"])
            self.assertTrue(target["exact_target"])

    def test_searches_dex_string_pool(self):
        dex = make_test_dex(["hello", "libpairipcore.so", "Lcom/example/PairIP;"])
        result = scan_dex_strings(dex, "classes.dex")
        self.assertTrue(result["valid_dex"])
        self.assertEqual(3, result["string_count"])
        self.assertEqual(2, len(result["matches"]))
        self.assertTrue(result["matches"][0]["exact_target"])
        self.assertEqual("libpairipcore.so", result["matches"][0]["value"])

    def test_scans_high_numbered_dex_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "multidex.apk"
            with zipfile.ZipFile(apk, "w") as archive:
                archive.writestr("classes.dex", make_test_dex(["ordinary"]))
                archive.writestr("classes5.dex", make_test_dex(["nothing"]))
                archive.writestr("classes60.dex", make_test_dex(["libpairipcore.so"]))
            result = scan_apk(apk)
            self.assertEqual(3, result["dex_files_scanned"])
            dex60 = next(d for d in result["dex_results"] if d["dex_path"] == "classes60.dex")
            self.assertEqual("libpairipcore.so", dex60["matches"][0]["value"])

    def test_invalid_archive_reports_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "broken.apk"
            apk.write_text("not a zip", encoding="utf-8")
            result = scan_apk(apk)
            self.assertFalse(result["valid_apk_zip"])
            self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
