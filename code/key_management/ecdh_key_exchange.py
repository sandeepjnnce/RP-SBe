"""
ecdh_key_exchange.py
Elliptic Curve Diffie-Hellman (ECDH) key exchange for per-ROI session key generation
in the RP-SBe framework.
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import os
from typing import Tuple, Optional


class ECDHKeyExchange:
    """
    Performs ephemeral ECDH key exchange and derives session keys using HKDF.
    Supports multiple curves based on privacy tier.
    """

    CURVE_MAP = {
        "T1": ec.SECP256R1(),      # Curve25519 equivalent strength
        "T2": ec.SECP256R1(),
        "T3": ec.SECP384R1(),
        "T4": ec.SECP521R1()
    }

    def __init__(self, tier: str = "T2"):
        self.tier = tier
        self.curve = self.CURVE_MAP.get(tier, ec.SECP256R1())
        self.private_key = None
        self.public_key = None
        self.shared_secret = None

    def generate_key_pair(self) -> bytes:
        """
        Generate ephemeral ECDH key pair.
        Returns the serialized public key.
        """
        self.private_key = ec.generate_private_key(self.curve, default_backend())
        self.public_key = self.private_key.public_key()

        # Serialize public key for transmission
        public_bytes = self.public_key.public_bytes(
            encoding=ec.Encoding.X962,
            format=ec.PublicFormat.UncompressedPoint
        )
        return public_bytes

    def compute_shared_secret(self, peer_public_bytes: bytes) -> bytes:
        """
        Compute shared secret using peer's public key.
        """
        if self.private_key is None:
            raise ValueError("Private key not generated. Call generate_key_pair() first.")

        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            self.curve, peer_public_bytes
        )

        self.shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)
        return self.shared_secret

    def derive_session_key(self,
                           salt: bytes,
                           info: bytes,
                           key_length: int = 32) -> bytes:
        """
        Derive final session key using HKDF-SHA256.
        """
        if self.shared_secret is None:
            raise ValueError("Shared secret not computed yet.")

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(self.shared_secret)


# Example usage
if __name__ == "__main__":
    # Simulate two parties (e.g., encoder and decoder side)
    party_a = ECDHKeyExchange(tier="T3")
    party_b = ECDHKeyExchange(tier="T3")

    pub_a = party_a.generate_key_pair()
    pub_b = party_b.generate_key_pair()

    secret_a = party_a.compute_shared_secret(pub_b)
    secret_b = party_b.compute_shared_secret(pub_a)

    print("Shared secrets match:", secret_a == secret_b)

    # Derive session key
    salt = os.urandom(8)
    info = b"RP-SBe-T3"
    session_key = party_a.derive_session_key(salt, info)
    print("Session Key (hex):", session_key.hex())