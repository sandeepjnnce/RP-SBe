"""
run_experiments.py
Main pipeline script for RP-SBe (Risk-Proportional Sign-Bit Encryption).

Features:
- Loads configuration from JSON files
- Clear pipeline flow
- Better logging and structure
- Easy to extend
"""

import argparse
import json
import logging
import os
import cv2
from pathlib import Path

from code.key_management.ahp_risk_scoring import AHPRiskScorer
from code.key_management.ecdh_key_exchange import ECDHKeyExchange
from code.key_management.hkdf_key_derivation import HKDFKeyDerivation
from code.sign_bit_encryption.sign_bit_encryption import RPSignBitEncryption
from code.utils.common_utils import get_roi_from_frame

# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Run RP-SBe Encryption Pipeline")
    parser.add_argument("--input", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, required=True, help="Path to output encrypted video")
    parser.add_argument("--config", type=str, default="config/ahp_config.json",
                        help="Path to AHP configuration file")
    parser.add_argument("--tier", type=str, default="T2", choices=["T1", "T2", "T3", "T4"],
                        help="Default privacy tier")
    return parser.parse_args()


def main():
    args = parse_args()
    logger.info(f"Starting RP-SBe pipeline on: {args.input}")

    # Load configuration
    if os.path.exists(args.config):
        config = load_config(args.config)
        logger.info(f"Loaded AHP config from: {args.config}")
    else:
        logger.warning(f"Config file not found: {args.config}. Using default values.")
        config = {}

    # Initialize components
    risk_scorer = AHPRiskScorer()
    ecdh = ECDHKeyExchange(tier=args.tier)
    hkdf = HKDFKeyDerivation()

    # TODO: Load your YOLOv8-based detector here
    # detector = load_detector(...)

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        logger.error("Cannot open input video.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    frame_id = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Video Info → Resolution: {width}x{height}, FPS: {fps}, Total Frames: {total_frames}")

    with tqdm(total=total_frames, desc="Processing Frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # TODO: Run detection
            # detections = detector.detect(frame)
            detections = []  # Replace with real detections

            for det in detections:
                bbox = det["bbox"]
                class_id = det["class_id"]
                confidence = det["confidence"]
                track_id = det.get("track_id", 0)
                frames_tracked = det.get("frames_tracked", 5)

                # Compute risk score
                risk_score = risk_scorer.compute_risk_score(
                    class_id=class_id,
                    confidence=confidence,
                    bbox=bbox,
                    frame_shape=(height, width),
                    frames_tracked=frames_tracked
                )

                # Generate per-ROI session key
                pub_key = ecdh.generate_key_pair()
                shared_secret = ecdh.compute_shared_secret(pub_key)  # Placeholder
                session_key = hkdf.derive_key_from_ecdh(
                    ecdh_shared_secret=shared_secret,
                    frame_id=frame_id,
                    bytetrack_id=track_id,
                    risk_score=risk_score
                )

                # TODO: Apply sign-bit encryption on ROI
                # roi = get_roi_from_frame(frame, bbox)
                # encrypted_roi = encrypt_sign_bits(roi, session_key, risk_score)

            out.write(frame)
            frame_id += 1
            pbar.update(1)

    cap.release()
    out.release()
    logger.info(f"Encrypted video saved to: {args.output}")
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()