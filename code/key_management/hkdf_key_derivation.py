"""
hkdf_key_derivation.py
HKDF-based session key derivation for RP-SBe per-ROI encryption.
This module works together with ECDH key exchange.
"""

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import Optional
import os


class HKDFKeyDerivation:
    """
    Derives cryptographically strong session keys using HKDF-SHA256.
    Used after ECDH shared secret computation.
    """

    def __init__(self, key_length: int = 32):
        self.key_length = key_length

    def derive_key(self,
                   ikm: bytes,
                   salt: Optional[bytes] = None,
                   info: Optional[bytes] = None) -> bytes:
        """
        Derive a session key from Input Keying Material (IKM).

        Args:
            ikm: Input Keying Material (usually ECDH shared secret)
            salt: Optional salt (recommended: frame_id + ByteTrack_ID)
            info: Optional context info (recommended: risk score or tier)

        Returns:
            Derived session key (32 bytes by default)
        """
        if salt is None:
            salt = os.urandom(16)

        if info is None:
            info = b"RP-SBe-Session-Key"

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(ikm)

    def derive_key_from_ecdh(self,
                             ecdh_shared_secret: bytes,
                             frame_id: int,
                             bytetrack_id: int,
                             risk_score: float) -> bytes:
        """
        Convenience method to derive key directly from ECDH output + metadata.
        Matches the construction used in the RP-SBe paper.
        """
        # Salt = frame_id (32-bit) || ByteTrack_ID (32-bit)
        salt = frame_id.to_bytes(4, 'big') + bytetrack_id.to_bytes(4, 'big')

        # Info = risk score (as bytes)
        info = str(round(risk_score, 4)).encode('utf-8')

        return self.derive_key(ecdh_shared_secret, salt=salt, info=info)


# Example usage
if __name__ == "__main__":
    hkdf = HKDFKeyDerivation()

    # Simulate ECDH shared secret
    shared_secret = os.urandom(32)

    session_key = hkdf.derive_key_from_ecdh(
        ecdh_shared_secret=shared_secret,
        frame_id=12345,
        bytetrack_id=7,
        risk_score=0.87
    )

    print("Derived Session Key (hex):", session_key.hex())
    print("Key Length:", len(session_key), "bytes")