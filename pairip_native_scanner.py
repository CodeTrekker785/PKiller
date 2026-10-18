#!/usr/bin/env python3
"""Read-only scanner for PairIP-related native libraries in APK archives.

This tool reports files only; it never edits, repacks, signs, or patches an APK.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

TARGET = "libpairipcore.so"


def scan_apk(apk_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "apk": str(apk_path),
        "valid_apk_zip": False,
        "matches": [],
        "error": None,
    }
    try:
        with zipfile.ZipFile(apk_path, "r") as archive:
            result["valid_apk_zip"] = True
            for item in archive.infolist():
                if item.is_dir():
                    continue
                name = item.filename
                basename = name.rsplit("/", 1)[-1]
                if basename.lower() == TARGET or "pairip" in basename.lower():
                    parts = name.split("/")
                    abi = parts[1] if len(parts) >= 3 and parts[0] == "lib" else None
                    result["matches"].append({
                        "path": name,
                        "name": basename,
                        "size_bytes": item.file_size,
                        "abi": abi,
                        "exact_target": basename.lower() == TARGET,
                    })
            result["matches"].sort(
                key=lambda match: (not match["exact_target"], match["path"].lower())
            )
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        result["error"] = str(exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find libpairipcore.so and other PairIP-named files in APKs (read-only)."
    )
    parser.add_argument("path", type=Path, help="APK file or directory containing APK files")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    target = args.path.expanduser()
    if target.is_file():
        apk_files = [target] if target.suffix.lower() == ".apk" else []
    elif target.is_dir():
        apk_files = sorted(target.rglob("*.apk"))
        apk_files += sorted(target.rglob("*.APK"))
        apk_files = sorted(set(apk_files))
    else:
        parser.error(f"path does not exist: {target}")

    if not apk_files:
        print("No .apk files found at the supplied path.", file=sys.stderr)
        return 2

    results = [scan_apk(apk) for apk in apk_files]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        total_matches = 0
        for result in results:
            print(f"\nAPK: {result['apk']}")
            if result["error"]:
                print(f"  ERROR: {result['error']}")
                continue
            if not result["valid_apk_zip"]:
                print("  Not a readable APK/ZIP archive.")
                continue
            exact = [m for m in result["matches"] if m["exact_target"]]
            related = [m for m in result["matches"] if not m["exact_target"]]
            print(f"  libpairipcore.so: {'FOUND' if exact else 'not found'}")
            for match in result["matches"]:
                total_matches += 1
                abi = f" | ABI: {match['abi']}" if match["abi"] else ""
                label = "TARGET" if match["exact_target"] else "RELATED"
                print(f"  [{label}] {match['path']} | {match['size_bytes']} bytes{abi}")
            if not result["matches"]:
                print("  No PairIP-named files found.")
        print(f"\nScanned {len(results)} APK(s); reported {total_matches} matching file(s).")
        print("Read-only scan: no APK contents were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
