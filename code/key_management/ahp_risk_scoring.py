"""
ahp_risk_scoring.py
Implements Analytic Hierarchy Process (AHP) based privacy risk scoring
for RP-SBe framework.
"""

import numpy as np
from typing import Dict, List, Tuple


class AHPRiskScorer:
    """
    Computes continuous privacy risk score using AHP.
    """

    def __init__(self):
        # Criteria weights derived from AHP (updated values)
        self.weights = np.array([0.49, 0.25, 0.09, 0.17])  # [C, S, U, T]

        # Class weights
        self.class_weights = {0: 1.0, 1: 0.6}  # 0=face, 1=license_plate

        self.T_MAX = 30  # Maximum tracking duration (in frames)

    def compute_risk_score(self,
                           class_id: int,
                           confidence: float,
                           bbox: List[int],
                           frame_shape: Tuple[int, int],
                           frames_tracked: int) -> float:
        """
        Compute privacy risk score for a detected ROI.

        Args:
            class_id: 0 for face, 1 for license plate
            confidence: Detection confidence from YOLO
            bbox: [x1, y1, x2, y2]
            frame_shape: (height, width)
            frames_tracked: Number of frames this object has been tracked

        Returns:
            Risk score in range [0, 1]
        """
        h, w = frame_shape
        x1, y1, x2, y2 = bbox

        # 1. Class weight
        C = self.class_weights.get(class_id, 0.6)

        # 2. Spatial salience (normalized ROI area)
        roi_area = (x2 - x1) * (y2 - y1)
        frame_area = h * w
        S = min(roi_area / frame_area, 1.0)

        # 3. Detection uncertainty
        U = 1.0 - confidence

        # 4. Temporal persistence
        T = min(frames_tracked / self.T_MAX, 1.0)

        # Weighted sum
        risk_score = (self.weights[0] * C +
                      self.weights[1] * S +
                      self.weights[2] * U +
                      self.weights[3] * T)

        return float(np.clip(risk_score, 0.0, 1.0))

    def assign_risk_tier(self, risk_score: float) -> str:
        """
        Map risk score to privacy tier.
        """
        if risk_score >= 0.80:
            return "T4 Critical"
        elif risk_score >= 0.60:
            return "T3 High"
        elif risk_score >= 0.35:
            return "T2 Medium"
        else:
            return "T1 Low"

    def get_encryption_intensity(self, risk_score: float, alpha: float = 1.0) -> float:
        """
        Compute encryption intensity I(r_i) = alpha * R(r_i)
        """
        return float(np.clip(alpha * risk_score, 0.0, 1.0))


# Example usage
if __name__ == "__main__":
    scorer = AHPRiskScorer()

    # Example detection
    risk = scorer.compute_risk_score(
        class_id=0,                    # face
        confidence=0.92,
        bbox=[100, 150, 220, 290],
        frame_shape=(720, 1280),
        frames_tracked=12
    )

    tier = scorer.assign_risk_tier(risk)
    intensity = scorer.get_encryption_intensity(risk)

    print(f"Risk Score: {risk:.4f}")
    print(f"Risk Tier : {tier}")
    print(f"Encryption Intensity: {intensity:.4f}")