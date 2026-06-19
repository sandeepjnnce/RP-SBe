"""
run_experiments.py
Main script to run the full RP-SBe pipeline on a video or image sequence.
"""

import argparse
import os
import cv2
import numpy as np
from tqdm import tqdm

from code.key_management.ahp_risk_scoring import AHPRiskScorer
from code.key_management.ecdh_key_exchange import ECDHKeyExchange
from code.key_management.hkdf_key_derivation import HKDFKeyDerivation
from code.sign_bit_encryption.sign_bit_encryption import RPSignBitEncryption
from code.utils.common_utils import get_roi_from_frame


def parse_args():
    parser = argparse.ArgumentParser(description="Run RP-SBe Encryption Pipeline")
    parser.add_argument("--input", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, required=True, help="Path to output encrypted video")
    parser.add_argument("--detector", type=str, default="yolov8", help="Object detector to use")
    parser.add_argument("--tier", type=str, default="T2", choices=["T1", "T2", "T3", "T4"])
    return parser.parse_args()


def main():
    args = parse_args()

    # Initialize components
    risk_scorer = AHPRiskScorer()
    ecdh = ECDHKeyExchange(tier=args.tier)
    hkdf = HKDFKeyDerivation()

    # TODO: Load YOLOv8-SAN-DTSH detector here
    # detector = YOLOv8SANDTSH(...)

    cap = cv2.VideoCapture(args.input)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    frame_id = 0
    print(f"Processing video: {args.input}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # TODO: Run detection
        # detections = detector.detect(frame)

        # Placeholder: Assume we have detections
        detections = []  # Replace with real detections

        for det in detections:
            bbox = det["bbox"]
            class_id = det["class_id"]
            confidence = det["confidence"]
            track_id = det.get("track_id", 0)

            # Compute risk score
            risk_score = risk_scorer.compute_risk_score(
                class_id=class_id,
                confidence=confidence,
                bbox=bbox,
                frame_shape=(height, width),
                frames_tracked=det.get("frames_tracked", 5)
            )

            # Generate per-ROI session key
            pub_key = ecdh.generate_key_pair()
            # In real scenario, exchange with decoder side
            shared_secret = ecdh.compute_shared_secret(pub_key)  # Placeholder
            session_key = hkdf.derive_key_from_ecdh(
                ecdh_shared_secret=shared_secret,
                frame_id=frame_id,
                bytetrack_id=track_id,
                risk_score=risk_score
            )

            # TODO: Apply sign-bit encryption on ROI macroblocks
            # roi = get_roi_from_frame(frame, bbox)
            # encrypted_roi = encrypt_roi(roi, session_key)

        out.write(frame)
        frame_id += 1

    cap.release()
    out.release()
    print(f"Encrypted video saved to: {args.output}")


if __name__ == "__main__":
    main()