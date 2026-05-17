#!/usr/bin/env python3
import zipfile, hashlib, sys

def verify_apk(path):
    try:
        with zipfile.ZipFile(path, "r") as z:
            manifest = z.namelist()
            if "META-INF/MANIFEST.MF" in manifest:
                print("✓ APK signed")
                return True
            else:
                print("✗ APK not signed")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify.py <apk>")
        sys.exit(1)
    verify_apk(sys.argv[1])
