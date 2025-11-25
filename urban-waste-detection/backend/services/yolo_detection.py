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
    """Service de détection avec YOLO11 fine-tuné sur TACO dataset"""

    # Classes du modèle TACO fine-tuné (6 classes de déchets)
    # Correspond au fichier data.yaml utilisé pour l'entraînement
    TACO_CLASSES = {
        0: 'Cigarette',
        1: 'Glass',
        2: 'Metal',
        3: 'Other',
        4: 'Paper',
        5: 'Plastic'
    }

    # Mapping des classes TACO vers catégories pour les couleurs/stats
    WASTE_CATEGORIES = {
        'plastic': ['Plastic'],
        'glass': ['Glass'],
        'metal': ['Metal'],
        'paper': ['Paper'],
        'organic': ['Cigarette'],  # Cigarettes = déchets organiques/dangereux
        'other': ['Other']
    }

    # Chemin par défaut vers le modèle fine-tuné TACO
    DEFAULT_MODEL_PATH = '/Users/vuong/Desktop/AI_PROJECT/yolo_taco_workspace/runs/detect/yolo11n_taco_20251031_171254/weights/best.pt'

    def __init__(self, model_path: str = None):
        """
        Initialise le service YOLO avec le modèle fine-tuné TACO

        Args:
            model_path: Chemin vers le modèle .pt fine-tuné
                       Par défaut: modèle TACO entraîné sur les 6 classes de déchets
        """
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.model = None
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.15))  # Seuil très bas pour détecter plus

        print(f"🤖 Initialisation YOLO11 TACO avec modèle: {self.model_path}...")

    def load_model(self):
        """Charge le modèle YOLO11 fine-tuné sur TACO"""
        try:
            print(f"📥 Chargement du modèle TACO: {self.model_path}...")

            # Vérifier que le modèle existe
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")

            # Charger le modèle fine-tuné
            self.model = YOLO(self.model_path)

            print(f"✅ Modèle TACO chargé avec succès!")
            print(f"📊 Classes détectables: {list(self.TACO_CLASSES.values())}")
            return self.model

        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            raise

    def detect(self, image_path: str) -> List[Dict]:
        """
        Détecte les déchets dans une image avec le modèle TACO

        Args:
            image_path: Chemin vers l'image

        Returns:
            Liste de détections avec format:
            {
                'class': 'Plastic',
                'category': 'plastic',
                'confidence': 0.95,
                'bbox': [x1, y1, x2, y2],
                'area': 1234
            }
        """
        if not self.model:
            self.load_model()

        try:
            # Détection avec YOLO TACO
            results = self.model(image_path, conf=self.confidence_threshold)

            detections = []

            for result in results:
                boxes = result.boxes

                for box in boxes:
                    # Extraire les informations
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]

                    # Toutes les classes du modèle TACO sont des déchets (0-5)
                    if class_id in self.TACO_CLASSES:
                        class_name = self.TACO_CLASSES[class_id]
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

            print(f"🔍 TACO détecté: {len(detections)} déchets ({[d['class'] for d in detections]})")
            return detections

        except Exception as e:
            print(f"❌ Erreur détection: {e}")
            import traceback
            traceback.print_exc()
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

                    # Toutes les classes TACO sont des déchets
                    if class_id in self.TACO_CLASSES:
                        class_name = self.TACO_CLASSES[class_id]
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

            if image is None:
                print(f"❌ Impossible de charger l'image: {image_path}")
                return

            # Couleurs par catégorie (BGR format pour OpenCV)
            colors = {
                'plastic': (0, 0, 255),      # Rouge vif
                'glass': (0, 255, 255),      # Jaune vif
                'organic': (0, 255, 0),      # Vert vif
                'metal': (192, 192, 192),    # Gris clair
                'paper': (255, 144, 30),     # Bleu-orange
                'electronic': (255, 0, 255), # Magenta
                'bulky': (0, 165, 255),      # Orange
                'other': (255, 255, 0)       # Cyan
            }

            print(f"🎨 Annotation de {len(detections)} détections...")

            # Dessiner les détections
            for i, det in enumerate(detections):
                x1, y1, x2, y2 = det['bbox']
                category = det['category']
                color = colors.get(category, (255, 255, 0))

                # Rectangle avec bordure épaisse
                thickness = 3  # Augmenté de 2 à 3
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

                # Label avec fond
                label = f"{det['class']} {det['confidence']:.2f}"
                font_scale = 0.6  # Augmenté de 0.5 à 0.6
                font_thickness = 2

                # Calculer la taille du texte
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
                )

                # Dessiner un rectangle de fond pour le texte
                cv2.rectangle(
                    image,
                    (x1, y1 - text_height - 10),
                    (x1 + text_width, y1),
                    color,
                    -1  # Remplir
                )

                # Texte en blanc pour contraste
                cv2.putText(
                    image,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),  # Blanc
                    font_thickness
                )

                print(f"  ✓ Détection {i+1}: {label} @ [{x1},{y1},{x2},{y2}]")

            # Sauvegarder
            cv2.imwrite(output_path, image)
            print(f"💾 Image annotée sauvegardée: {output_path}")
            print(f"📊 Total: {len(detections)} bounding boxes dessinées")

        except Exception as e:
            print(f"❌ Erreur annotation: {e}")
            import traceback
            traceback.print_exc()


# Instance globale
_yolo_service = None

def get_yolo_service(model_path: str = None) -> YOLODetectionService:
    """Retourne l'instance globale du service YOLO TACO"""
    global _yolo_service
    if _yolo_service is None:
        _yolo_service = YOLODetectionService(model_path=model_path)
        _yolo_service.load_model()
    return _yolo_service
