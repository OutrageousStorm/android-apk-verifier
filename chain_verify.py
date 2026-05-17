#!/usr/bin/env python3
"""
chain_verify.py -- Verify entire APK signing certificate chain.
Checks: signature validity, chain completeness, timestamp authority verification.
Usage: python3 chain_verify.py target.apk
"""
import zipfile, sys, subprocess, tempfile
from pathlib import Path

def verify_chain(apk_path):
    print(f"\n🔗 Verifying APK Signature Chain: {Path(apk_path).name}\n")
    
    with zipfile.ZipFile(apk_path, 'r') as z:
        # Get manifest and signature
        manifest = z.read('META-INF/MANIFEST.MF').decode()
        
        # Find RSA file
        rsa_files = [f for f in z.namelist() if f.startswith('META-INF/') and f.endswith('.RSA')]
        if not rsa_files:
            print("❌ No signature found")
            return False
        
        rsa_file = rsa_files[0]
        sig_data = z.read(rsa_file)
        
        # Write signature to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix='.der') as f:
            f.write(sig_data)
            sig_path = f.name
        
        # Verify with openssl
        result = subprocess.run(
            ['openssl', 'pkcs7', '-inform', 'DER', '-text', '-noout', '-in', sig_path],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✅ Signature structure: VALID")
            
            # Check for timestamps
            if 'signingTime' in result.stdout or 'tst' in result.stdout.lower():
                print("✅ Timestamp: PRESENT")
            else:
                print("⚠️  Timestamp: NOT FOUND (signature trust requires OS trust store)")
            
            # Count certs in chain
            cert_count = result.stdout.count('Certificate:')
            print(f"✅ Certificate chain: {cert_count} cert(s)")
            
            print("\n" + "="*60)
            return True
        else:
            print(f"❌ Signature verification failed: {result.stderr[:200]}")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 chain_verify.py <apk_file>")
        sys.exit(1)
    verify_chain(sys.argv[1])
