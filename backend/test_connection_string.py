"""Test script to verify DATABASE_URL connection string format"""
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

# Load environment variables
load_dotenv()
load_dotenv('.env.local', override=True)

url = os.getenv('DATABASE_URL', '')

print("=" * 60)
print("CONNECTION STRING VERIFICATION")
print("=" * 60)
print(f"\nRaw URL from .env:")
print(f"  {url[:80]}..." if len(url) > 80 else f"  {url}")
print(f"\nLength: {len(url)} characters")

if not url:
    print("\n[ERROR] DATABASE_URL is empty!")
    exit(1)

# Parse the URL
try:
    parsed = urlparse(url)
    print(f"\nParsed Components:")
    print(f"  Scheme: {parsed.scheme}")
    print(f"  Username: {parsed.username}")
    print(f"  Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
    print(f"  Hostname: {parsed.hostname}")
    print(f"  Port: {parsed.port}")
    print(f"  Database: {parsed.path.lstrip('/')}")
    print(f"  Query: {parsed.query}")
    
    # Check password encoding
    if parsed.password:
        decoded_password = unquote(parsed.password)
        print(f"\nPassword Analysis:")
        print(f"  Encoded password contains %40: {'%40' in parsed.password}")
        print(f"  Decoded password contains @: {'@' in decoded_password}")
        print(f"  Password length: {len(parsed.password)} (encoded), {len(decoded_password)} (decoded)")
    
    # Validation checks
    print(f"\nValidation:")
    checks = []
    
    # Check 1: Scheme
    if parsed.scheme == 'postgresql':
        checks.append(("[OK] Scheme is postgresql", True))
    else:
        checks.append((f"[ERROR] Scheme is {parsed.scheme} (should be postgresql)", False))
    
    # Check 2: Hostname
    if parsed.hostname and parsed.hostname.startswith('aws-'):
        checks.append(("[OK] Hostname starts with aws-", True))
    elif parsed.hostname:
        checks.append((f"[WARN] Hostname is {parsed.hostname}", True))
    else:
        checks.append(("[ERROR] Hostname is missing", False))
    
    # Check 3: Port
    if parsed.port == 5432:
        checks.append(("[OK] Port is 5432 (Session pooler)", True))
    elif parsed.port == 6543:
        checks.append(("[OK] Port is 6543 (Transaction pooler)", True))
    elif parsed.port:
        checks.append((f"[WARN] Port is {parsed.port} (unusual)", True))
    else:
        checks.append(("[ERROR] Port is missing", False))
    
    # Check 4: SSL mode
    if 'sslmode=require' in parsed.query:
        checks.append(("[OK] SSL mode is require", True))
    else:
        checks.append(("[WARN] SSL mode not found in query string", True))
    
    # Check 5: Password encoding
    if parsed.password:
        if '@' in parsed.password and '%40' not in parsed.password:
            checks.append(("[ERROR] Password contains unencoded @ symbol", False))
        elif '%40' in parsed.password:
            checks.append(("[OK] Password @ is URL-encoded as %40", True))
        else:
            checks.append(("[OK] Password appears to be properly encoded", True))
    
    # Check 6: No brackets in password
    if parsed.password:
        if parsed.password.startswith('[') or parsed.password.endswith(']'):
            checks.append(("[ERROR] Password contains brackets (should be removed)", False))
        else:
            checks.append(("[OK] Password has no brackets", True))
    
    for check, passed in checks:
        print(f"  {check}")
    
    # Overall status
    all_passed = all(passed for _, passed in checks)
    print(f"\n{'=' * 60}")
    if all_passed:
        print("[OK] CONNECTION STRING FORMAT IS CORRECT")
        print("\nIf connection still fails, it's likely:")
        print("  1. Circuit breaker is open (wait 10-15 minutes)")
        print("  2. Password is incorrect (verify in Supabase Dashboard)")
        print("  3. Network/firewall issue")
    else:
        print("[ERROR] CONNECTION STRING HAS ISSUES")
        print("\nFix the issues above before testing connection.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Error parsing connection string: {e}")
    print(f"\nThis means the connection string format is invalid.")
    exit(1)
