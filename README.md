# PKiller — PairIP APK Inspector

PKiller provides **read-only inspection** for Android APK files. It can report
whether `libpairipcore.so` or other PairIP-named files are packaged in an APK,
and search every `classes*.dex` DEX string pool for PairIP-related strings.

It does not activate/deactivate a library inside another app, remove licensing
checks, or patch/rebuild/sign APKs. A file or string match does not prove that a
library is loaded or running.

## Termux setup

Install Python and Git:

```sh
pkg update
pkg install -y python git
```

Clone the inspection branch:

```sh
git clone -b feature/pairip-inspection-controls https://github.com/CodeTrekker785/PKiller.git
cd PKiller
```

Allow Termux to access shared storage if you want to scan Downloads:

```sh
termux-setup-storage
```

## Use the scanner directly

Scan one APK:

```sh
python pairip_native_scanner.py ~/storage/downloads/example.apk
```

Scan all APKs in Downloads:

```sh
python pairip_native_scanner.py ~/storage/downloads
```

Output JSON:

```sh
python pairip_native_scanner.py ~/storage/downloads/example.apk --json
```

## Interactive Termux menu

```sh
chmod +x pkiller-menu.sh
./pkiller-menu.sh
```

The menu offers single-APK scanning, Downloads scanning, custom-folder scanning,
and safe-use notes. It is a terminal menu, not a native Android application UI.

## Android app buttons

This repository currently contains the Python scanner and Termux menu, not a
native Android application project. A native UI with buttons can safely provide
**Choose APK**, **Scan**, **Show findings**, and **Rescan**. A switch that
forcibly disables PairIP protection in a third-party APK is not included.

## Limits

The scanner reads archive entries and standard DEX string tables. It cannot
prove runtime behavior, and references may be dynamically assembled or encoded.
