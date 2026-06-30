# RP-SBe: Risk-Proportional Sign-Bit Encryption for Privacy Protection in H.264 Surveillance Video

This repository contains the implementation of RP-SBe, a risk-proportional sign-bit encryption framework for privacy-preserving H.264 surveillance video.

## Important Notes

- All videos were encoded using Python (OpenCV) with H.264 codec. We did not use the standalone `x264` command-line tool.
- Encoding configuration is available in `config/encoding_config.json`.
- AHP weights and tier thresholds are available in `config/ahp_config.json`.
- Random seeds used in all experiments are available in `config/random_seeds.json`.

## Repository Structure
RP-SBe/
├── code/
│   ├── key_management/       # AHP, ECDH, HKDF
│   ├── sign_bit_encryption/  # Core RP-SBe encryption
│   ├── evaluation/           # ArcFace, LPR, Re-ID evaluation
│   └── utils/
├── scripts/                  # Experiment and result generation scripts
├── config/                   # Configuration files (AHP, encoding, seeds)
├── results/                  # Generated tables and figures
└── README.md
