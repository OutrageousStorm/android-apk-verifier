#!/usr/bin/env python3
"""
extract_certs.py -- Extract certificates from an APK and display their details.
Usage: python3 extract_certs.py target.apk
Shows: issuer, subject, validity dates, public key algorithm, signature algorithm.
"""
import zipfile, sys, subprocess, re
from pathlib import Path
from datetime import datetime

def extract_and_inspect(apk_path):
    with zipfile.ZipFile(apk_path, 'r') as z:
        # Find the signer cert (usually in META-INF/)
        meta = [f for f in z.namelist() if f.startswith('META-INF/') and f.endswith('.RSA')]
        if not meta:
            print(f"❌ No RSA certificate found in {apk_path}")
            sys.exit(1)
        
        cert_path = meta[0]
        cert_data = z.read(cert_path)
        
        # Write to temp file and parse with openssl
        tmp = '/tmp/cert.der'
        with open(tmp, 'wb') as f:
            f.write(cert_data)
        
        # Extract cert details
        out = subprocess.run(
            ['openssl', 'pkcs7', '-inform', 'DER', '-print_certs', '-text', '-in', tmp],
            capture_output=True, text=True
        ).stdout
        
        print(f"\n🔐 APK Certificate Details: {Path(apk_path).name}\n")
        print("=" * 60)
        
        # Parse key fields
        issuer = re.search(r'Issuer: (.+)', out)
        subject = re.search(r'Subject: (.+)', out)
        not_before = re.search(r'Not Before: (.+)', out)
        not_after = re.search(r'Not After : (.+)', out)
        pubkey = re.search(r'Public-Key: \((\d+) bit', out)
        sig_algo = re.search(r'Signature Algorithm: (.+?)(?:\n|$)', out)
        
        if issuer: print(f"Issuer:     {issuer.group(1)}")
        if subject: print(f"Subject:    {subject.group(1)}")
        if not_before: print(f"Valid from: {not_before.group(1)}")
        if not_after: print(f"Valid until: {not_after.group(1)}")
        if pubkey: print(f"Public key: {pubkey.group(1)}-bit")
        if sig_algo: print(f"Signature:  {sig_algo.group(1)}")
        
        # Check expiry
        if not_after:
            try:
                exp = datetime.strptime(not_after.group(1), '%b %d %H:%M:%S %Y %Z')
                if exp < datetime.now():
                    print(f"\n⚠️  CERTIFICATE EXPIRED!")
            except: pass
        
        print("=" * 60 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 extract_certs.py <apk_file>")
        sys.exit(1)
    extract_and_inspect(sys.argv[1])
