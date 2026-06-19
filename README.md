\# RP-SBe: Risk-Proportional Sign-Bit Encryption for Privacy-Preserving H.264 Surveillance Video



This repository contains the implementation and experimental code for the paper:



\*\*RP-SBe: A Risk-Proportional Sign-Bit Encryption Scheme for Privacy Protection in H.264/AVC Surveillance Video Streams\*\*



\## Abstract

RP-SBe is a selective encryption framework that applies encryption intensity proportionally to the privacy risk of each detected region (faces and license plates) using AHP-based risk scoring. It achieves strong privacy protection with minimal bitrate overhead while maintaining full H.264/AVC format compliance.



\## Key Features

\- Risk-proportional encryption using AHP-derived privacy scores

\- Format-compliant sign-bit encryption using ChaCha20-CTR

\- Real-time performance (81.3 FPS core pipeline)

\- New Risk-Weighted Visual Distortion (RWVD) metric

\- Comprehensive evaluation against ArcFace, Re-ID, and LPR



\## Directory Structure

\- `code/`: Core implementation (key management, encryption, evaluation)

\- `scripts/`: Scripts to run experiments and generate results

\- `paper/`: Preprint of the paper

\- `results/`: Tables and figures

\- `data/`: Instructions to obtain datasets



\## Installation

```bash

git clone https://github.com/sandeepjnnce/RP-SBe.git

cd RP-SBe

pip install -r requirements.txt

