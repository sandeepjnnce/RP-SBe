"""
lpr_evaluation.py
Evaluates License Plate Recognition (LPR) degradation caused by RP-SBe.
Uses EasyOCR to measure Character Recognition Rate (CRR).
"""

import numpy as np
import easyocr
from typing import List, Dict


class LPRPrivacyEvaluator:
    """
    Evaluates privacy protection on license plates using Character Recognition Rate (CRR).
    """

    def __init__(self, languages: List[str] = None):
        if languages is None:
            languages = ['en']
        self.reader = easyocr.Reader(languages, gpu=True)

    def recognize_plate(self, image: np.ndarray) -> str:
        """
        Recognize text from a license plate image using EasyOCR.
        """
        results = self.reader.readtext(image, detail=0)
        if results:
            return results[0].upper().replace(" ", "")
        return ""

    def compute_crr(self, original_text: str, recognized_text: str) -> float:
        """
        Compute Character Recognition Rate (CRR).
        """
        if not original_text:
            return 0.0

        min_len = min(len(original_text), len(recognized_text))
        if min_len == 0:
            return 0.0

        matches = sum(1 for i in range(min_len) if original_text[i] == recognized_text[i])
        return (matches / len(original_text)) * 100

    def evaluate_privacy_degradation(self,
                                     clean_images: List[np.ndarray],
                                     encrypted_images: List[np.ndarray],
                                     ground_truth_texts: List[str]) -> Dict:
        """
        Evaluate LPR degradation between clean and encrypted license plate images.
        """
        results = []

        for clean, encrypted, gt in zip(clean_images, encrypted_images, ground_truth_texts):
            clean_recog = self.recognize_plate(clean)
            enc_recog = self.recognize_plate(encrypted)

            clean_crr = self.compute_crr(gt, clean_recog)
            enc_crr = self.compute_crr(gt, enc_recog)
            relative_drop = ((clean_crr - enc_crr) / clean_crr * 100) if clean_crr > 0 else 0.0

            results.append({
                "ground_truth": gt,
                "clean_recognized": clean_recog,
                "encrypted_recognized": enc_recog,
                "clean_crr": clean_crr,
                "encrypted_crr": enc_crr,
                "relative_drop": relative_drop
            })

        avg_clean_crr = float(np.mean([r["clean_crr"] for r in results]))
        avg_enc_crr = float(np.mean([r["encrypted_crr"] for r in results]))
        avg_drop = float(np.mean([r["relative_drop"] for r in results]))

        return {
            "average_clean_crr": avg_clean_crr,
            "average_encrypted_crr": avg_enc_crr,
            "average_relative_drop": avg_drop,
            "num_plates": len(results),
            "detailed_results": results
        }


# Example usage
if __name__ == "__main__":
    evaluator = LPRPrivacyEvaluator()

    # Dummy example
    clean_plates = [np.random.randint(0, 255, (80, 200, 3), dtype=np.uint8)]
    enc_plates = [np.random.randint(0, 255, (80, 200, 3), dtype=np.uint8)]
    gt_texts = ["KA19AB1234"]

    result = evaluator.evaluate_privacy_degradation(clean_plates, enc_plates, gt_texts)
    print(result)