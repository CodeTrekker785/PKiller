#!/usr/bin/env python3
"""Read-only scanner for PairIP-related native libraries and DEX strings.

The scanner reports archive paths and matching DEX string-pool entries only.
It never edits, repacks, signs, or patches an APK.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

TARGET = "libpairipcore.so"


def _read_uleb128(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data) and shift <= 35:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise ValueError("invalid or truncated ULEB128")


def scan_dex_strings(data: bytes, dex_path: str) -> dict[str, Any]:
    """Search every string_id in a standard little-endian DEX string pool."""
    result: dict[str, Any] = {
        "dex_path": dex_path,
        "valid_dex": False,
        "string_count": 0,
        "matches": [],
        "error": None,
    }
    try:
        if len(data) < 112 or not data.startswith(b"dex\n") or data[7:8] != b"\0":
            raise ValueError("not a standard DEX file or header is truncated")
        string_count = int.from_bytes(data[56:60], "little")
        string_ids_off = int.from_bytes(data[60:64], "little")
        if string_count > 10_000_000 or string_ids_off > len(data):
            raise ValueError("invalid DEX string table bounds")
        table_end = string_ids_off + string_count * 4
        if table_end > len(data):
            raise ValueError("DEX string_ids table extends beyond file")
        result["valid_dex"] = True
        result["string_count"] = string_count

        for index in range(string_count):
            id_offset = string_ids_off + index * 4
            string_offset = int.from_bytes(data[id_offset:id_offset + 4], "little")
            if string_offset >= len(data):
                continue
            try:
                _utf16_size, cursor = _read_uleb128(data, string_offset)
            except ValueError:
                continue
            end = data.find(b"\0", cursor)
            if end < 0:
                continue
            # The target library name is ASCII. Replacement decoding also makes
            # unusual modified-UTF-8 entries safe to display without aborting.
            value = data[cursor:end].decode("utf-8", errors="replace")
            if "pairip" in value.lower():
                result["matches"].append({
                    "string_index": index,
                    "string_data_offset": string_offset,
                    "value": value,
                    "exact_target": value.lower() == TARGET,
                })
        result["matches"].sort(
            key=lambda match: (not match["exact_target"], match["string_index"])
        )
    except (ValueError, IndexError) as exc:
        result["error"] = str(exc)
    return result


def scan_apk(apk_path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "apk": str(apk_path),
        "valid_apk_zip": False,
        "matches": [],
        "dex_files_scanned": 0,
        "dex_results": [],
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
                if basename.lower() == "classes.dex" or (
                    basename.lower().startswith("classes")
                    and basename.lower().endswith(".dex")
                    and basename[7:-4].isdigit()
                ):
                    result["dex_files_scanned"] += 1
                    try:
                        dex_data = archive.read(item)
                        dex_result = scan_dex_strings(dex_data, name)
                    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                        dex_result = {
                            "dex_path": name, "valid_dex": False,
                            "string_count": 0, "matches": [], "error": str(exc),
                        }
                    result["dex_results"].append(dex_result)
            result["matches"].sort(
                key=lambda match: (not match["exact_target"], match["path"].lower())
            )
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        result["error"] = str(exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find PairIP-named files and strings in every classes*.dex entry (read-only)."
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
        total_file_matches = 0
        total_dex_matches = 0
        for result in results:
            print(f"\nAPK: {result['apk']}")
            if result["error"]:
                print(f"  ERROR: {result['error']}")
                continue
            if not result["valid_apk_zip"]:
                print("  Not a readable APK/ZIP archive.")
                continue
            exact = [m for m in result["matches"] if m["exact_target"]]
            print(f"  Native libpairipcore.so: {'FOUND' if exact else 'not found'}")
            for match in result["matches"]:
                total_file_matches += 1
                abi = f" | ABI: {match['abi']}" if match["abi"] else ""
                label = "TARGET" if match["exact_target"] else "RELATED"
                print(f"  [{label}] {match['path']} | {match['size_bytes']} bytes{abi}")
            print(f"  DEX files scanned: {result['dex_files_scanned']}")
            for dex in result["dex_results"]:
                if not dex["valid_dex"]:
                    detail = f" ({dex['error']})" if dex["error"] else ""
                    print(f"    {dex['dex_path']}: not a valid readable DEX{detail}")
                    continue
                print(f"    {dex['dex_path']}: searched {dex['string_count']} string-pool entries")
                for match in dex["matches"]:
                    total_dex_matches += 1
                    label = "EXACT STRING" if match["exact_target"] else "RELATED STRING"
                    print(
                        f"      [{label}] string #{match['string_index']} "
                        f"at offset {match['string_data_offset']}: {match['value']}"
                    )
            if not result["matches"] and not any(d["matches"] for d in result["dex_results"]):
                print("  No PairIP-named files or PairIP strings found.")
        print(
            f"\nScanned {len(results)} APK(s); reported {total_file_matches} "
            f"file match(es) and {total_dex_matches} DEX string match(es)."
        )
        print("Read-only scan: no APK contents were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
