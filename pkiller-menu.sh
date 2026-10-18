#!/data/data/com.termux/files/usr/bin/bash
# PKiller read-only PairIP inspection menu for Termux.
# This menu scans APK archives; it never modifies APKs or controls their runtime.

set -u
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCANNER="$SCRIPT_DIR/pairip_native_scanner.py"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is required. Install it with: pkg install python"
  exit 1
fi
if [ ! -f "$SCANNER" ]; then
  echo "Scanner not found: $SCANNER"
  echo "Keep pkiller-menu.sh beside pairip_native_scanner.py."
  exit 1
fi

while true; do
  printf '\n=== PKiller: PairIP Inspection ===\n'
  printf '1) Scan one APK\n'
  printf '2) Scan Android Downloads folder\n'
  printf '3) Scan a folder path\n'
  printf '4) Show safe-use notes\n'
  printf '0) Exit\n'
  printf 'Choose: '
  IFS= read -r choice || exit 0

  case "$choice" in
    1)
      printf 'APK path: '
      IFS= read -r apk || continue
      apk="${apk#\"}"; apk="${apk%\"}"
      if [ -f "$apk" ]; then
        python "$SCANNER" "$apk"
      else
        echo "File not found: $apk"
      fi
      ;;
    2)
      DOWNLOADS="$HOME/storage/downloads"
      if [ ! -d "$DOWNLOADS" ]; then
        echo "Downloads folder is not available."
        echo "Run termux-setup-storage and allow storage access, then try again."
      else
        python "$SCANNER" "$DOWNLOADS"
      fi
      ;;
    3)
      printf 'Folder path: '
      IFS= read -r folder || continue
      folder="${folder#\"}"; folder="${folder%\"}"
      if [ -d "$folder" ]; then
        python "$SCANNER" "$folder"
      else
        echo "Folder not found: $folder"
      fi
      ;;
    4)
      cat <<'NOTES'
- This tool reports files and PairIP-related DEX strings in APK archives.
- FOUND means the file/string is packaged in the APK; it does not prove it is loaded.
- The menu does not activate/deactivate native libraries in another app.
- It does not patch, rebuild, sign, or bypass app security checks.
NOTES
      ;;
    0) exit 0 ;;
    *) echo "Invalid choice." ;;
  esac
done
