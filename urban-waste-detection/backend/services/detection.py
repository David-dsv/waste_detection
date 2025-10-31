"""
Service de détection de déchets avec RF-DETR.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Tuple

import torch
import cv2
import numpy as np
from PIL import Image
import onnxruntime as ort


class DetectionService:
    """Service pour inférence du modèle RF-DETR."""

    # Classes de déchets
    CLASS_NAMES = {
        0: "plastic_bottle",
        1: "plastic_bag",
        2: "metal_can",
        3: "glass_bottle",
        4: "cardboard",
        5: "paper_waste",
        6: "overflowing_bin",
        7: "organic_waste",
        8: "cigarette_butt",
        9: "food_container",
        10: "electronic_waste",
        11: "textile_waste"
    }

    # Couleurs pour visualisation (BGR)
    COLORS = {
        0: (255, 0, 0),      # Bleu
        1: (0, 255, 0),      # Vert
        2: (0, 0, 255),      # Rouge
        3: (255, 255, 0),    # Cyan
        4: (255, 0, 255),    # Magenta
        5: (0, 255, 255),    # Jaune
        6: (128, 0, 128),    # Violet
        7: (0, 128, 128),    # Teal
        8: (128, 128, 0),    # Olive
        9: (192, 192, 192),  # Gris
        10: (255, 165, 0),   # Orange
        11: (75, 0, 130),    # Indigo
    }

    def __init__(
        self,
        model_path: str = None,
        model_type: str = 'onnx',
        device: str = None,
        conf_threshold: float = 0.5,
        nms_threshold: float = 0.4
    ):
        """
        Args:
            model_path: Chemin vers modèle (.pth ou .onnx)
            model_type: 'pytorch' ou 'onnx'
            device: 'cuda' ou 'cpu'
            conf_threshold: Seuil de confiance minimum
            nms_threshold: Seuil NMS (Non-Maximum Suppression)
        """
        self.model_path = model_path or os.getenv('MODEL_PATH')
        self.model_type = model_type or os.getenv('MODEL_TYPE', 'onnx')
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.conf_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', conf_threshold))
        self.nms_threshold = float(os.getenv('NMS_THRESHOLD', nms_threshold))

        self.model = None
        self.img_size = 640

    def load_model(self):
        """Charge le modèle RF-DETR."""
        print(f"\n🔧 Chargement modèle {self.model_type}...")

        if self.model_type == 'onnx':
            # Chargement ONNX Runtime
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.device == 'cuda' else ['CPUExecutionProvider']
            self.model = ort.InferenceSession(self.model_path, providers=providers)
            print(f"  ✅ Modèle ONNX chargé: {self.model_path}")

        elif self.model_type == 'pytorch':
            # Chargement PyTorch
            checkpoint = torch.load(self.model_path, map_location=self.device)

            # Créer modèle (adapter selon votre architecture)
            # self.model = create_rtdetr_model(num_classes=len(self.CLASS_NAMES))
            # self.model.load_state_dict(checkpoint['model_state_dict'])
            # self.model.to(self.device)
            # self.model.eval()

            print(f"  ✅ Modèle PyTorch chargé: {self.model_path}")
        else:
            raise ValueError(f"Type de modèle non supporté: {self.model_type}")

        return self.model

    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Prétraite l'image pour inférence.

        Args:
            image: Image BGR (OpenCV)

        Returns:
            (image_tensor, original_shape)
        """
        # Sauvegarder dimensions originales
        orig_h, orig_w = image.shape[:2]

        # Convertir BGR -> RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Redimensionner
        image_resized = cv2.resize(image_rgb, (self.img_size, self.img_size))

        # Normaliser [0, 255] -> [0, 1]
        image_normalized = image_resized.astype(np.float32) / 255.0

        # Transposer (H, W, C) -> (C, H, W)
        image_transposed = np.transpose(image_normalized, (2, 0, 1))

        # Ajouter dimension batch (1, C, H, W)
        image_batch = np.expand_dims(image_transposed, axis=0)

        return image_batch, (orig_h, orig_w)

    def postprocess_detections(
        self,
        outputs: Dict,
        orig_shape: Tuple[int, int]
    ) -> List[Dict]:
        """
        Post-traite les sorties du modèle.

        Args:
            outputs: Sorties du modèle
            orig_shape: Forme originale de l'image (h, w)

        Returns:
            Liste de détections filtrées
        """
        orig_h, orig_w = orig_shape

        # Extraire logits et boxes (adapter selon votre modèle)
        if self.model_type == 'onnx':
            # Format ONNX (adapter selon votre export)
            logits = outputs[0][0]  # (num_queries, num_classes)
            boxes = outputs[1][0]   # (num_queries, 4)
        else:
            # Format PyTorch
            logits = outputs['pred_logits'][0].cpu().numpy()
            boxes = outputs['pred_boxes'][0].cpu().numpy()

        # Calculer scores (softmax ou sigmoid)
        scores = self._sigmoid(logits)

        # Extraire détections au-dessus du seuil
        detections = []

        for i in range(len(scores)):
            # Classe avec score max
            class_id = np.argmax(scores[i])
            confidence = scores[i][class_id]

            if confidence < self.conf_threshold:
                continue

            # Extraire bbox (format: cx, cy, w, h normalisé)
            cx, cy, w, h = boxes[i]

            # Convertir en pixels originaux
            x1 = int((cx - w / 2) * orig_w)
            y1 = int((cy - h / 2) * orig_h)
            x2 = int((cx + w / 2) * orig_w)
            y2 = int((cy + h / 2) * orig_h)

            # Clipper aux dimensions image
            x1 = max(0, min(x1, orig_w))
            y1 = max(0, min(y1, orig_h))
            x2 = max(0, min(x2, orig_w))
            y2 = max(0, min(y2, orig_h))

            detections.append({
                'class_id': int(class_id),
                'class_name': self.CLASS_NAMES.get(int(class_id), 'unknown'),
                'confidence': float(confidence),
                'bbox': [x1, y1, x2, y2]
            })

        # Appliquer NMS
        detections = self._apply_nms(detections)

        return detections

    def _sigmoid(self, x):
        """Fonction sigmoid."""
        return 1 / (1 + np.exp(-x))

    def _apply_nms(self, detections: List[Dict]) -> List[Dict]:
        """
        Applique Non-Maximum Suppression.

        Args:
            detections: Liste de détections

        Returns:
            Détections filtrées
        """
        if not detections:
            return []

        # Convertir en format numpy
        boxes = np.array([d['bbox'] for d in detections])
        scores = np.array([d['confidence'] for d in detections])

        # NMS OpenCV
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            self.conf_threshold,
            self.nms_threshold
        )

        if len(indices) == 0:
            return []

        # Filtrer détections
        indices = indices.flatten()
        filtered_detections = [detections[i] for i in indices]

        return filtered_detections

    def detect(self, image: np.ndarray) -> Tuple[List[Dict], float]:
        """
        Détecte les déchets dans une image.

        Args:
            image: Image BGR (OpenCV)

        Returns:
            (detections, processing_time)
        """
        start_time = time.time()

        # Prétraitement
        image_tensor, orig_shape = self.preprocess_image(image)

        # Inférence
        if self.model_type == 'onnx':
            input_name = self.model.get_inputs()[0].name
            outputs = self.model.run(None, {input_name: image_tensor})
        else:
            with torch.no_grad():
                image_torch = torch.from_numpy(image_tensor).to(self.device)
                outputs = self.model(image_torch)

        # Post-traitement
        detections = self.postprocess_detections(outputs, orig_shape)

        processing_time = time.time() - start_time

        return detections, processing_time

    def visualize_detections(
        self,
        image: np.ndarray,
        detections: List[Dict],
        save_path: str = None
    ) -> np.ndarray:
        """
        Visualise les détections sur l'image.

        Args:
            image: Image BGR
            detections: Liste de détections
            save_path: Chemin sauvegarde (optionnel)

        Returns:
            Image annotée
        """
        image_vis = image.copy()

        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_id = det['class_id']
            class_name = det['class_name']
            confidence = det['confidence']

            # Couleur
            color = self.COLORS.get(class_id, (255, 255, 255))

            # Dessiner rectangle
            cv2.rectangle(image_vis, (x1, y1), (x2, y2), color, 2)

            # Label
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_w, label_h = label_size

            # Fond label
            cv2.rectangle(
                image_vis,
                (x1, y1 - label_h - 5),
                (x1 + label_w, y1),
                color,
                -1
            )

            # Texte
            cv2.putText(
                image_vis,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        # Sauvegarder si demandé
        if save_path:
            cv2.imwrite(save_path, image_vis)

        return image_vis

    def detect_video(self, video_path: str, output_path: str = None) -> Dict:
        """
        Détecte les déchets dans une vidéo.

        Args:
            video_path: Chemin vers vidéo
            output_path: Chemin vidéo annotée (optionnel)

        Returns:
            Statistiques détections
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Impossible d'ouvrir la vidéo: {video_path}")

        # Infos vidéo
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Writer pour vidéo annotée
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Statistiques
        all_detections = []
        frame_count = 0

        print(f"🎥 Traitement vidéo ({total_frames} frames à {fps} FPS)...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Détection (tous les N frames pour perf)
            if frame_count % 5 == 0:  # Tous les 5 frames
                detections, _ = self.detect(frame)
                all_detections.extend(detections)

                # Visualiser
                if writer:
                    frame_annotated = self.visualize_detections(frame, detections)
                    writer.write(frame_annotated)

            frame_count += 1

        # Libérer ressources
        cap.release()
        if writer:
            writer.release()

        # Statistiques
        stats = self._compute_video_stats(all_detections)
        stats['total_frames'] = total_frames
        stats['fps'] = fps

        print(f"  ✅ Vidéo traitée: {frame_count} frames")

        return stats

    def _compute_video_stats(self, detections: List[Dict]) -> Dict:
        """Calcule statistiques vidéo."""
        if not detections:
            return {'total_detections': 0}

        class_counts = {}
        for det in detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        avg_confidence = np.mean([d['confidence'] for d in detections])

        return {
            'total_detections': len(detections),
            'class_distribution': class_counts,
            'average_confidence': float(avg_confidence)
        }
