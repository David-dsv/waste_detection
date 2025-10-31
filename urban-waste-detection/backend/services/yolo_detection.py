"""
YOLOv8 Detection Service for Urban Waste Detection
Utilise YOLOv8 pré-entraîné pour détecter les objets/déchets
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
from PIL import Image

class YOLODetectionService:
    """Service de détection avec YOLO11"""

    # Mapping des classes YOLO11 standard vers catégories de déchets
    # YOLO11 utilise les 80 classes COCO standard
    WASTE_CLASSES = {
        # Objets qui sont des déchets
        39: 'bottle',           # bouteille
        40: 'wine glass',       # verre
        41: 'cup',              # gobelet
        42: 'fork',             # fourchette
        43: 'knife',            # couteau
        44: 'spoon',            # cuillère
        45: 'bowl',             # bol
        46: 'banana',           # banane
        47: 'apple',            # pomme
        48: 'sandwich',         # sandwich
        49: 'orange',           # orange
        50: 'broccoli',         # broccoli
        51: 'carrot',           # carotte
        52: 'hot dog',          # hot dog
        53: 'pizza',            # pizza
        54: 'donut',            # donut
        55: 'cake',             # gâteau
        73: 'book',             # livre (papier)
        76: 'scissors',         # ciseaux
        79: 'toothbrush',       # brosse à dents
    }

    # Mapping des classes vers catégories de déchets
    WASTE_CATEGORIES = {
        'plastic': ['bottle', 'cup'],
        'glass': ['wine glass', 'bottle'],
        'organic': ['banana', 'apple', 'orange', 'broccoli', 'carrot', 'sandwich', 'pizza', 'hot dog', 'donut', 'cake'],
        'metal': ['fork', 'knife', 'spoon', 'scissors'],
        'paper': ['book'],
        'other': ['bowl', 'toothbrush']
    }

    def __init__(self, model_name: str = 'yolo11n.pt'):
        """
        Initialise le service YOLO

        Args:
            model_name: Nom du modèle YOLO11 ('yolo11n.pt', 'yolo11s.pt', etc.)
                       Par défaut: yolo11n.pt (nano - le plus rapide)
        """
        self.model_name = model_name
        self.model = None
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))

        print(f"🤖 Initialisation YOLO11 avec modèle: {model_name}...")

    def load_model(self):
        """Charge le modèle YOLO11 (télécharge automatiquement si nécessaire)"""
        try:
            print(f"📥 Chargement du modèle YOLO11: {self.model_name}...")

            # YOLO télécharge automatiquement le modèle si absent
            self.model = YOLO(self.model_name)

            print(f"✅ Modèle YOLO11 chargé avec succès!")
            print(f"📊 Utilisation de YOLO11 pour la détection de déchets urbains")
            return self.model

        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            raise

    def detect(self, image_path: str) -> List[Dict]:
        """
        Détecte les objets/déchets dans une image

        Args:
            image_path: Chemin vers l'image

        Returns:
            Liste de détections avec format:
            {
                'class': 'bottle',
                'category': 'plastic',
                'confidence': 0.95,
                'bbox': [x1, y1, x2, y2],
                'area': 1234
            }
        """
        if not self.model:
            self.load_model()

        try:
            # Détection avec YOLO
            results = self.model(image_path, conf=self.confidence_threshold)

            detections = []

            for result in results:
                boxes = result.boxes

                for box in boxes:
                    # Extraire les informations
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]

                    # Vérifier si c'est une classe "déchet"
                    if class_id in self.WASTE_CLASSES:
                        class_name = self.WASTE_CLASSES[class_id]
                        category = self._get_category(class_name)

                        # Calculer l'aire
                        area = int((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))

                        detection = {
                            'class': class_name,
                            'category': category,
                            'confidence': round(confidence, 3),
                            'bbox': [int(coord) for coord in bbox],
                            'area': area
                        }

                        detections.append(detection)

            print(f"🔍 YOLO11 détecté: {len(detections)} objets/déchets")
            return detections

        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            return []

    def detect_from_array(self, image_array: np.ndarray) -> List[Dict]:
        """
        Détecte à partir d'un array numpy

        Args:
            image_array: Image en array numpy (RGB)

        Returns:
            Liste de détections
        """
        if not self.model:
            self.load_model()

        try:
            # YOLO accepte directement les arrays numpy
            results = self.model(image_array, conf=self.confidence_threshold)

            detections = []

            for result in results:
                boxes = result.boxes

                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy().tolist()

                    if class_id in self.WASTE_CLASSES:
                        class_name = self.WASTE_CLASSES[class_id]
                        category = self._get_category(class_name)
                        area = int((bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))

                        detection = {
                            'class': class_name,
                            'category': category,
                            'confidence': round(confidence, 3),
                            'bbox': [int(coord) for coord in bbox],
                            'area': area
                        }

                        detections.append(detection)

            return detections

        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            return []

    def detect_video(self, video_path: str, frame_skip: int = 30) -> List[Dict]:
        """
        Détecte dans une vidéo (sample tous les N frames)

        Args:
            video_path: Chemin vers la vidéo
            frame_skip: Analyser 1 frame tous les N frames

        Returns:
            Liste des détections agrégées
        """
        if not self.model:
            self.load_model()

        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            all_detections = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Skip frames pour accélérer
                if frame_count % frame_skip == 0:
                    # Convertir BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    detections = self.detect_from_array(frame_rgb)
                    all_detections.extend(detections)

                frame_count += 1

            cap.release()

            # Agréger les détections
            aggregated = self._aggregate_detections(all_detections)

            print(f"🎥 Vidéo analysée: {frame_count} frames, {len(aggregated)} objets uniques")
            return aggregated

        except Exception as e:
            print(f"❌ Erreur détection vidéo: {e}")
            return []

    def _get_category(self, class_name: str) -> str:
        """Trouve la catégorie d'un déchet"""
        for category, classes in self.WASTE_CATEGORIES.items():
            if class_name in classes:
                return category
        return 'other'

    def _aggregate_detections(self, detections: List[Dict]) -> List[Dict]:
        """Agrège les détections multiples du même objet"""
        if not detections:
            return []

        # Grouper par classe
        grouped = {}
        for det in detections:
            key = f"{det['class']}_{det['category']}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(det)

        # Prendre la meilleure détection de chaque groupe
        aggregated = []
        for key, group in grouped.items():
            # Trier par confiance
            best = max(group, key=lambda x: x['confidence'])

            # Ajouter le nombre d'occurrences
            best['occurrences'] = len(group)
            aggregated.append(best)

        return aggregated

    def annotate_image(self, image_path: str, detections: List[Dict], output_path: str):
        """
        Annote une image avec les détections

        Args:
            image_path: Image source
            detections: Liste des détections
            output_path: Chemin de sortie
        """
        try:
            # Charger l'image
            image = cv2.imread(image_path)

            # Couleurs par catégorie
            colors = {
                'plastic': (0, 0, 255),      # Rouge
                'glass': (0, 255, 255),      # Jaune
                'organic': (0, 255, 0),      # Vert
                'metal': (128, 128, 128),    # Gris
                'paper': (255, 200, 100),    # Bleu clair
                'electronic': (255, 0, 255), # Magenta
                'bulky': (0, 128, 255),      # Orange
                'other': (255, 255, 255)     # Blanc
            }

            # Dessiner les détections
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                category = det['category']
                color = colors.get(category, (255, 255, 255))

                # Rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

                # Label
                label = f"{det['class']} {det['confidence']:.2f}"
                cv2.putText(image, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Sauvegarder
            cv2.imwrite(output_path, image)
            print(f"💾 Image annotée sauvegardée: {output_path}")

        except Exception as e:
            print(f"❌ Erreur annotation: {e}")


# Instance globale
_yolo_service = None

def get_yolo_service(model_name: str = 'yolo11n.pt') -> YOLODetectionService:
    """Retourne l'instance globale du service YOLO11"""
    global _yolo_service
    if _yolo_service is None:
        _yolo_service = YOLODetectionService(model_name=model_name)
        _yolo_service.load_model()
    return _yolo_service
