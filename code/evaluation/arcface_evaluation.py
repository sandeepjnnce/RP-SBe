"""
arcface_evaluation.py
Evaluates privacy protection using ArcFace face recognition model.
Measures accuracy drop between clean and encrypted face crops.
"""

import numpy as np
from typing import List, Tuple
from insightface.app import FaceAnalysis


class ArcFacePrivacyEvaluator:
    """
    Evaluates face verification accuracy degradation caused by RP-SBe.
    """

    def __init__(self, model_name: str = 'buffalo_l', providers: List[str] = None):
        if providers is None:
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']

        self.app = FaceAnalysis(name=model_name, providers=providers)
        self.app.prepare(ctx_id=0)

    def get_embedding(self, image: np.ndarray) -> np.ndarray:
        """
        Extract ArcFace embedding from an image.
        """
        faces = self.app.get(image)
        if len(faces) == 0:
            return None
        return faces[0].embedding

    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        """
        if emb1 is None or emb2 is None:
            return 0.0
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

    def evaluate_privacy_degradation(self,
                                     clean_images: List[np.ndarray],
                                     encrypted_images: List[np.ndarray]) -> dict:
        """
        Evaluate privacy degradation between clean and encrypted face images.
        """
        similarities = []
        for clean, encrypted in zip(clean_images, encrypted_images):
            emb_clean = self.get_embedding(clean)
            emb_enc = self.get_embedding(encrypted)

            sim = self.compute_similarity(emb_clean, emb_enc)
            similarities.append(sim)

        avg_similarity = float(np.mean(similarities)) if similarities else 0.0
        accuracy_drop = (1.0 - avg_similarity) * 100

        return {
            "average_similarity": avg_similarity,
            "accuracy_drop_percent": accuracy_drop,
            "num_samples": len(similarities)
        }


# Example usage
if __name__ == "__main__":
    evaluator = ArcFacePrivacyEvaluator()

    # Dummy example (replace with real face crops)
    clean_faces = [np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)]
    encrypted_faces = [np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)]

    result = evaluator.evaluate_privacy_degradation(clean_faces, encrypted_faces)
    print(result)