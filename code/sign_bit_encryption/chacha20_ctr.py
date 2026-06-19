"""
chacha20_ctr.py
ChaCha20-CTR implementation for encrypting sign bits of AC coefficients
in the RP-SBe framework.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Optional
import os


class ChaCha20CTR:
    """
    ChaCha20 stream cipher in CTR mode for selective sign-bit encryption.
    """

    def __init__(self, key: Optional[bytes] = None, nonce: Optional[bytes] = None):
        """
        Initialize ChaCha20-CTR.

        Args:
            key: 32-byte key. If None, a random key is generated.
            nonce: 12-byte (96-bit) nonce. If None, a random nonce is generated.
        """
        self.key = key if key else os.urandom(32)
        self.nonce = nonce if nonce else os.urandom(12)
        self._cipher = None

    def _get_cipher(self) -> Cipher:
        """Internal method to create ChaCha20 cipher instance."""
        if self._cipher is None:
            algorithm = algorithms.ChaCha20(self.key, self.nonce)
            self._cipher = Cipher(algorithm, mode=None, backend=default_backend())
        return self._cipher

    def generate_keystream(self, length: int) -> bytes:
        """
        Generate a keystream of the desired length.
        """
        cipher = self._get_cipher()
        encryptor = cipher.encryptor()
        keystream = encryptor.update(b'\x00' * length)
        return keystream

    def encrypt_bytes(self, data: bytes) -> bytes:
        """
        Encrypt data using ChaCha20-CTR (XOR with keystream).
        """
        keystream = self.generate_keystream(len(data))
        return bytes(a ^ b for a, b in zip(data, keystream))

    def decrypt_bytes(self, ciphertext: bytes) -> bytes:
        """
        Decrypt is identical to encrypt in stream ciphers.
        """
        return self.encrypt_bytes(ciphertext)

    def get_key(self) -> bytes:
        return self.key

    def get_nonce(self) -> bytes:
        return self.nonce


# Example usage
if __name__ == "__main__":
    chacha = ChaCha20CTR()

    # Simulate sign bits (as bytes)
    original_signs = b'\x01\x00\x01\x01\x00'   # Example sign bits

    encrypted = chacha.encrypt_bytes(original_signs)
    decrypted = chacha.decrypt_bytes(encrypted)

    print("Original :", original_signs)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)
    print("Match    :", original_signs == decrypted)