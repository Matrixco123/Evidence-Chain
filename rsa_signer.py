"""
rsa_signer.py — RSA-2048 digital signature module.

Provides keypair generation, hash signing, and signature verification
for integration with a FastAPI-based digital evidence verification system.

Dependencies: pycryptodome  (pip install pycryptodome)
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# ── Configuration ────────────────────────────────────────────────────
_BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = _BASE_DIR / "private.pem"
PUBLIC_KEY_PATH = _BASE_DIR / "public.pem"
_KEY_SIZE_BITS = 2048


# ── Core API ─────────────────────────────────────────────────────────

def generate_keypair(
    *,
    force: bool = False,
    private_path: Path = PRIVATE_KEY_PATH,
    public_path: Path = PUBLIC_KEY_PATH,
) -> None:
    """Generate an RSA-2048 keypair and write PEM files to disk.

    If both key files already exist the call is a no-op unless *force* is True.

    Args:
        force:        Overwrite existing key files.
        private_path: Destination for the private key PEM.
        public_path:  Destination for the public key PEM.
    """
    if not force and private_path.exists() and public_path.exists():
        return

    key = RSA.generate(_KEY_SIZE_BITS)
    private_path.write_bytes(key.export_key())
    public_path.write_bytes(key.publickey().export_key())


def sign_hash(hash_string: str) -> str:
    """Sign a SHA-256 hash string using the RSA private key.

    Automatically generates a keypair on first use if keys are absent.

    Args:
        hash_string: The SHA-256 hex digest to sign (e.g. from hashlib).

    Returns:
        Base64-encoded PKCS#1 v1.5 signature.

    Raises:
        FileNotFoundError: If the private key file cannot be found.
        ValueError:        If the hash string is empty.
    """
    generate_keypair()  # no-op if keys already exist

    private_key = RSA.import_key(PRIVATE_KEY_PATH.read_bytes())
    digest = SHA256.new(hash_string.encode("utf-8"))
    signature = pkcs1_15.new(private_key).sign(digest)
    return base64.b64encode(signature).decode("ascii")


def verify_signature(hash_string: str, signature_b64: str) -> bool:
    """Verify an RSA signature against a SHA-256 hash string.

    Args:
        hash_string:   The original SHA-256 hex digest that was signed.
        signature_b64: Base64-encoded PKCS#1 v1.5 signature to verify.

    Returns:
        True if the signature is valid, False otherwise.
    """
    try:
        public_key = RSA.import_key(PUBLIC_KEY_PATH.read_bytes())
        digest = SHA256.new(hash_string.encode("utf-8"))
        raw_sig = base64.b64decode(signature_b64, validate=True)
        pkcs1_15.new(public_key).verify(digest, raw_sig)
        return True
    except (ValueError, TypeError):
        return False


# ── Quick self-test ──────────────────────────────────────────────────
if __name__ == "__main__":
    import hashlib

    # Force fresh keys for the test run
    generate_keypair(force=True)
    print("[+] Keypair generated")

    sample_hash = hashlib.sha256(b"evidence_file_bytes").hexdigest()
    print(f"[+] Sample hash : {sample_hash}")

    sig = sign_hash(sample_hash)
    print(f"[+] Signature   : {sig[:48]}...")

    assert verify_signature(sample_hash, sig), "Valid signature rejected!"
    print("[+] Verification: AUTHENTIC")

    tampered = hashlib.sha256(b"tampered_bytes").hexdigest()
    assert not verify_signature(tampered, sig), "Tampered hash accepted!"
    print("[+] Tampered    : REJECTED")

    print("\n[OK] All checks passed.")
