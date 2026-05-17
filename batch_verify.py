#!/usr/bin/env python3
"""
batch_verify.py -- Verify signatures on all APKs in a directory
Generates a CSV report with signature validity, certificate chain, issuer info
Usage: python3 batch_verify.py /path/to/apks [--report results.csv]
"""
import sys, os, csv, subprocess
from pathlib import Path
from datetime import datetime

def verify_apk(apk_path):
    """Verify APK signature and return details"""
    try:
        result = subprocess.run(
            ['jarsigner', '-verify', '-verbose', str(apk_path)],
            capture_output=True, text=True, timeout=10
        )
        valid = result.returncode == 0
        
        # Extract cert info
        cert_info = {'valid': valid, 'signer': '', 'subject': '', 'issuer': '', 'expires': ''}
        
        for line in result.stderr.split('\n'):
            if 'CN=' in line:
                cert_info['subject'] = line.strip()
            if 'issuer' in line.lower():
                cert_info['issuer'] = line.strip()
        
        return cert_info
    except Exception as e:
        return {'valid': False, 'error': str(e), 'signer': '', 'subject': '', 'issuer': '', 'expires': ''}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_verify.py <apk_directory> [--report out.csv]")
        sys.exit(1)
    
    apk_dir = Path(sys.argv[1])
    if not apk_dir.exists():
        print(f"Directory not found: {apk_dir}")
        sys.exit(1)
    
    report_file = None
    if '--report' in sys.argv:
        idx = sys.argv.index('--report')
        report_file = sys.argv[idx + 1]
    
    apks = list(apk_dir.glob('*.apk'))
    print(f"\n🔍 Verifying {len(apks)} APKs...\n")
    
    results = []
    for i, apk in enumerate(apks, 1):
        print(f"  [{i}/{len(apks)}] {apk.name}...", end='', flush=True)
        info = verify_apk(apk)
        status = '✓' if info['valid'] else '✗'
        print(f" {status}")
        
        results.append({
            'filename': apk.name,
            'path': str(apk),
            'valid': 'YES' if info['valid'] else 'NO',
            'subject': info.get('subject', ''),
            'issuer': info.get('issuer', ''),
            'error': info.get('error', ''),
        })
    
    # Summary
    valid_count = sum(1 for r in results if r['valid'] == 'YES')
    print(f"\n✅ Valid: {valid_count}/{len(apks)}")
    
    # CSV report
    if report_file:
        with open(report_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'valid', 'subject', 'issuer', 'error'])
            writer.writeheader()
            writer.writerows(results)
        print(f"📊 Report: {report_file}")

if __name__ == "__main__":
    main()
