# PairIP Native Library Scanner

Use `pairip_native_scanner.py` to inspect APK archives for `libpairipcore.so`
and other files whose names contain `pairip`. The scanner is read-only: it does
not modify, rebuild, sign, or patch APKs.

## Requirements

- Python 3.9 or newer
- No third-party Python packages

## Usage

Scan one APK:

```sh
python pairip_native_scanner.py /path/to/app.apk
```

Scan a directory recursively:

```sh
python pairip_native_scanner.py ~/storage/downloads
```

Output JSON for scripts or automation:

```sh
python pairip_native_scanner.py app.apk --json
```

For native libraries stored under a standard APK path such as
`lib/arm64-v8a/libpairipcore.so`, the report includes the ZIP path, byte size,
and ABI folder. Other PairIP-named files are listed as related matches.

## Android / Termux

```sh
pkg install python
termux-setup-storage
python pairip_native_scanner.py ~/storage/downloads
```

This scanner identifies files for inspection only. A match does not, by itself,
prove how a library is used or whether it performs a particular check.
