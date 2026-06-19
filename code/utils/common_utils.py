"""
common_utils.py
Common utility functions used across the RP-SBe pipeline.
"""

import numpy as np
import cv2
from typing import Tuple, List, Dict


def compute_iou(box1: List[int], box2: List[int]) -> float:
    """
    Compute Intersection over Union (IoU) between two bounding boxes.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


def get_roi_from_frame(frame: np.ndarray, bbox: List[int]) -> np.ndarray:
    """
    Crop ROI from frame using bounding box [x1, y1, x2, y2].
    """
    x1, y1, x2, y2 = map(int, bbox)
    return frame[y1:y2, x1:x2]


def resize_with_aspect_ratio(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio.
    """
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def normalize_risk_score(score: float) -> float:
    """
    Clip and normalize risk score to [0, 1].
    """
    return float(np.clip(score, 0.0, 1.0))


def calculate_relative_drop(original: float, encrypted: float) -> float:
    """
    Calculate relative drop percentage.
    """
    if original == 0:
        return 0.0
    return ((original - encrypted) / original) * 100


def save_image(image: np.ndarray, path: str) -> None:
    """
    Save image to disk.
    """
    cv2.imwrite(path, image)


def load_image(path: str) -> np.ndarray:
    """
    Load image from disk.
    """
    return cv2.imread(path)