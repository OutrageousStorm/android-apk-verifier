#!/usr/bin/env python3
"""
sign.py -- Sign an APK with a keystore (debug or release)
Usage: python3 sign.py --apk target.apk --ks keystore.jks --ks-pass password
       python3 sign.py --apk target.apk --debug  # uses ~/.android/debug.keystore
"""
import subprocess, argparse, sys, os
from pathlib import Path

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr

def main():
    parser = argparse.ArgumentParser(description="Sign Android APKs")
    parser.add_argument("--apk", required=True, help="APK file to sign")
    parser.add_argument("--ks", help="Keystore file")
    parser.add_argument("--ks-pass", help="Keystore password")
    parser.add_argument("--key-pass", help="Key password (default: same as ks-pass)")
    parser.add_argument("--debug", action="store_true", help="Use debug keystore (~/.android/debug.keystore)")
    parser.add_argument("--align", action="store_true", default=True, help="Zipalign APK (default: yes)")
    parser.add_argument("--output", help="Output APK path")
    args = parser.parse_args()

    apk = Path(args.apk)
    if not apk.exists():
        print(f"APK not found: {apk}"); sys.exit(1)

    if args.debug:
        ks = Path.home() / ".android" / "debug.keystore"
        ks_pass = "android"
        key_pass = "android"
        alias = "androiddebugkey"
        print(f"Using debug keystore: {ks}")
    else:
        ks = Path(args.ks or "keystore.jks")
        ks_pass = args.ks_pass or input("Keystore password: ")
        key_pass = args.key_pass or ks_pass
        if not ks.exists():
            print(f"Keystore not found: {ks}"); sys.exit(1)
        alias = "releasekey"

    output = Path(args.output or f"{apk.stem}_signed.apk")
    aligned = Path(f"{apk.stem}_aligned.apk") if args.align else apk

    print(f"\n📦 APK Signer")
    print("="*50)
    print(f"Input:    {apk.name}")
    print(f"Keystore: {ks.name} ({alias})")
    print(f"Output:   {output.name}\n")

    # Zipalign
    if args.align:
        print("Zipaligning...")
        ok, out = run(f"zipalign -f 4 {apk} {aligned}")
        if not ok:
            print(f"Zipalign failed:\n{out}"); sys.exit(1)
        print("  ✓ Zipaligned")

    # Sign with apksigner if available, else jarsigner
    if os.system("which apksigner > /dev/null 2>&1") == 0:
        print("Signing with apksigner...")
        ok, out = run(
            f'apksigner sign --ks "{ks}" --ks-pass pass:{ks_pass} '
            f'--key-pass pass:{key_pass} --out "{output}" "{aligned}"'
        )
        if not ok:
            print(f"Signing failed:\n{out}"); sys.exit(1)
    else:
        print("Signing with jarsigner...")
        ok, out = run(
            f'jarsigner -keystore "{ks}" -storepass {ks_pass} '
            f'-keypass {key_pass} -signedjar "{output}" "{aligned}" {alias}'
        )
        if not ok:
            print(f"Signing failed:\n{out}"); sys.exit(1)

    print("  ✓ Signed")

    # Verify
    print("Verifying...")
    ok, out = run(f"jarsigner -verify -verbose {output}")
    if ok and "jar verified" in out.lower():
        print("  ✓ Signature valid")
    else:
        print(f"  ⚠️  Verification output:\n{out[:300]}")

    print(f"\n✅ Done → {output}")
    print(f"   Install: adb install {output}")

if __name__ == "__main__":
    main()
