"""
sign_bit_encryption.py
Core implementation of Risk-Proportional Sign-Bit Encryption (RP-SBe).
Encrypts only the sign bits of non-zero AC coefficients inside ROI macroblocks.
"""

import numpy as np
from typing import List, Tuple
from .chacha20_ctr import ChaCha20CTR


class RPSignBitEncryption:
    """
    Risk-Proportional Sign-Bit Encryption for H.264/AVC AC coefficients.
    """

    def __init__(self, session_key: bytes, nonce: bytes):
        """
        Initialize with per-ROI session key and nonce.
        """
        self.chacha = ChaCha20CTR(key=session_key, nonce=nonce)

    def select_coefficients_to_encrypt(self,
                                       non_zero_coeffs: List[int],
                                       intensity: float) -> int:
        """
        Determine how many coefficients to encrypt based on risk intensity.
        """
        num_to_encrypt = int(np.floor(intensity * len(non_zero_coeffs)))
        return max(0, min(num_to_encrypt, len(non_zero_coeffs)))

    def encrypt_sign_bits(self,
                          coefficients: np.ndarray,
                          intensity: float) -> Tuple[np.ndarray, int]:
        """
        Encrypt sign bits of the first k non-zero AC coefficients (zigzag order).

        Args:
            coefficients: 1D array of quantized AC coefficients (zigzag order)
            intensity: Encryption intensity I(r_i) in [0, 1]

        Returns:
            Modified coefficients and number of encrypted sign bits
        """
        coeffs = coefficients.copy()
        non_zero_indices = np.where(coeffs != 0)[0]

        if len(non_zero_indices) == 0:
            return coeffs, 0

        k = self.select_coefficients_to_encrypt(non_zero_indices.tolist(), intensity)
        if k == 0:
            return coeffs, 0

        # Extract sign bits of first k non-zero coefficients
        signs = np.sign(coeffs[non_zero_indices[:k]])
        sign_bytes = ((signs + 1) // 2).astype(np.uint8).tobytes()

        # Encrypt sign bits
        encrypted_sign_bytes = self.chacha.encrypt_bytes(sign_bytes)
        encrypted_signs = np.frombuffer(encrypted_sign_bytes, dtype=np.uint8)
        encrypted_signs = (encrypted_signs * 2 - 1).astype(np.int8)

        # Replace original sign bits
        for i in range(k):
            idx = non_zero_indices[i]
            if encrypted_signs[i] != 0:
                coeffs[idx] = np.abs(coeffs[idx]) * encrypted_signs[i]

        return coeffs, k

    def decrypt_sign_bits(self,
                          coefficients: np.ndarray,
                          intensity: float) -> np.ndarray:
        """
        Decrypt sign bits (same operation as encryption for stream cipher).
        """
        return self.encrypt_sign_bits(coefficients, intensity)[0]


# Example usage
if __name__ == "__main__":
    import os

    key = os.urandom(32)
    nonce = os.urandom(12)

    rp_sbe = RPSignBitEncryption(session_key=key, nonce=nonce)

    # Simulated quantized AC coefficients (zigzag order)
    ac_coeffs = np.array([12, -8, 0, 5, -3, 0, 0, 7, -1, 0, 2], dtype=np.int16)

    intensity = 0.75  # Example: 75% encryption intensity
    encrypted_coeffs, num_encrypted = rp_sbe.encrypt_sign_bits(ac_coeffs, intensity)

    print("Original coeffs :", ac_coeffs)
    print("Encrypted coeffs:", encrypted_coeffs)
    print(f"Number of sign bits encrypted: {num_encrypted}")