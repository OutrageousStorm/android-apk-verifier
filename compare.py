#!/usr/bin/env python3
"""
compare.py -- Compare two APKs — find differences in size, files, signature
Usage: python3 compare.py old.apk new.apk
"""
import subprocess, zipfile, sys
from pathlib import Path

def get_apk_info(apk_path):
    size = Path(apk_path).stat().st_size
    with zipfile.ZipFile(apk_path, 'r') = zip:
        files = zip.namelist()
        file_sizes = {f: zip.getinfo(f).file_size for f in files}
    return {'size': size, 'files': files, 'file_sizes': file_sizes}

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 compare.py old.apk new.apk")
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]
    old = get_apk_info(old_path)
    new = get_apk_info(new_path)

    print(f"\n📊 APK Comparison")
    print("="*50)
    print(f"Old:  {Path(old_path).name}")
    print(f"New:  {Path(new_path).name}")
    print()

    # Size
    delta = new['size'] - old['size']
    pct = (delta / old['size'] * 100) if old['size'] > 0 else 0
    print(f"Size:  {old['size']/1024:.1f} KB → {new['size']/1024:.1f} KB ({delta/1024:+.1f} KB, {pct:+.1f}%)")

    # Files
    old_files = set(old['files'])
    new_files = set(new['files'])
    added = new_files - old_files
    removed = old_files - new_files
    common = old_files & new_files

    print(f"Files: {len(old_files)} → {len(new_files)} ({len(added):+d} added, {len(removed):+d} removed)")

    if added:
        print(f"\n  Added ({len(added)}):")
        for f in sorted(added)[:10]:
            print(f"    + {f} ({new['file_sizes'].get(f, 0)/1024:.1f} KB)")
        if len(added) > 10: print(f"    ... and {len(added)-10} more")

    if removed:
        print(f"\n  Removed ({len(removed)}):")
        for f in sorted(removed)[:10]:
            print(f"    - {f}")
        if len(removed) > 10: print(f"    ... and {len(removed)-10} more")

    # Biggest changes in common files
    changes = {}
    for f in common:
        old_sz = old['file_sizes'].get(f, 0)
        new_sz = new['file_sizes'].get(f, 0)
        if old_sz != new_sz:
            changes[f] = (new_sz - old_sz, f)

    if changes:
        print(f"\n  Largest changes in existing files:")
        for file, (delta, name) in sorted(changes.items(), key=lambda x: abs(x[1][0]), reverse=True)[:5]:
            print(f"    {name}: {delta/1024:+.1f} KB")

    print()

if __name__ == "__main__":
    main()
