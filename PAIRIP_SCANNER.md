# PairIP Native Library and DEX String Scanner

Use `pairip_native_scanner.py` to inspect APK archives for `libpairipcore.so`,
other PairIP-named files, and PairIP-related strings in every `classes*.dex`
entry found in the APK. The scanner is read-only: it does not modify, rebuild,
sign, or patch APKs.

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

The scanner searches every matching DEX entry, including `classes.dex`,
`classes2.dex`, `classes3.dex`, and numbered entries such as `classes60.dex`.
It reads each DEX string table and reports matching string-pool index, string
data offset, and value. It also reports native library ZIP paths, byte sizes,
and ABI folders when available.

A string match proves only that the text is present in the DEX string pool; it
does not prove the app loads that library or explain how the text is used. Some
references may be assembled dynamically or stored in encoded form and therefore
not appear as a plain string.

## Android / Termux

```sh
pkg install python
termux-setup-storage
python pairip_native_scanner.py ~/storage/downloads
```

This tool is for read-only inspection and does not bypass or disable app licensing,
integrity, or security checks.
