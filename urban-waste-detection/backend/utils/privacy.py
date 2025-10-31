"""
Utilitaires pour protection de la vie privée et éthique.
"""

import cv2
import numpy as np
from typing import List, Tuple


class PrivacyProtection:
    """Outils pour anonymisation et protection des données."""

    def __init__(self):
        # Charger détecteur de visages (Haar Cascade)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def blur_faces(
        self,
        image: np.ndarray,
        blur_strength: int = 51
    ) -> Tuple[np.ndarray, int]:
        """
        Floute automatiquement les visages dans l'image.

        Args:
            image: Image BGR (OpenCV)
            blur_strength: Force du flou (impair)

        Returns:
            (image_anonymized, num_faces_blurred)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Détecter visages
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        image_anonymized = image.copy()

        # Flouter chaque visage
        for (x, y, w, h) in faces:
            # Zone du visage
            face_roi = image_anonymized[y:y+h, x:x+w]

            # Appliquer flou gaussien
            blurred_face = cv2.GaussianBlur(face_roi, (blur_strength, blur_strength), 0)

            # Remplacer dans image
            image_anonymized[y:y+h, x:x+w] = blurred_face

        return image_anonymized, len(faces)

    def remove_metadata(self, image_path: str) -> bool:
        """
        Supprime les métadonnées EXIF d'une image.

        Args:
            image_path: Chemin vers l'image

        Returns:
            Succès
        """
        try:
            from PIL import Image

            # Charger image sans métadonnées
            image = Image.open(image_path)

            # Sauvegarder sans EXIF
            data = list(image.getdata())
            image_no_exif = Image.new(image.mode, image.size)
            image_no_exif.putdata(data)
            image_no_exif.save(image_path)

            return True

        except Exception as e:
            print(f"Erreur suppression métadonnées: {e}")
            return False

    def anonymize_location(
        self,
        latitude: float,
        longitude: float,
        precision: int = 2
    ) -> Tuple[float, float]:
        """
        Réduit la précision GPS pour anonymisation.

        Args:
            latitude: Latitude précise
            longitude: Longitude précise
            precision: Nombre de décimales (2 = ~1km)

        Returns:
            (lat_anonymized, lon_anonymized)
        """
        lat_anonymized = round(latitude, precision)
        lon_anonymized = round(longitude, precision)

        return lat_anonymized, lon_anonymized


class BiasDetection:
    """Détection et mitigation des biais dans les données."""

    @staticmethod
    def analyze_class_distribution(detections: List[dict]) -> dict:
        """
        Analyse la distribution des classes pour détecter biais.

        Args:
            detections: Liste de détections

        Returns:
            Statistiques de distribution
        """
        class_counts = {}

        for det in detections:
            for obj in det.get('objects', []):
                class_name = obj['class_name']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        total = sum(class_counts.values())
        if total == 0:
            return {}

        # Calculer distribution
        distribution = {
            class_name: {
                'count': count,
                'percentage': (count / total) * 100
            }
            for class_name, count in class_counts.items()
        }

        # Détecter classes sous-représentées (<5%)
        underrepresented = [
            name for name, stats in distribution.items()
            if stats['percentage'] < 5
        ]

        return {
            'distribution': distribution,
            'total_classes': len(class_counts),
            'underrepresented_classes': underrepresented,
            'is_balanced': len(underrepresented) == 0
        }

    @staticmethod
    def check_geographical_bias(detections: List[dict]) -> dict:
        """
        Vérifie les biais géographiques.

        Args:
            detections: Détections avec localisation

        Returns:
            Analyse géographique
        """
        regions = {}

        for det in detections:
            if det.get('location'):
                # Arrondir coordonnées pour regrouper par région
                lat = round(det['location']['latitude'], 1)
                lon = round(det['location']['longitude'], 1)
                region_key = f"{lat},{lon}"

                if region_key not in regions:
                    regions[region_key] = 0
                regions[region_key] += 1

        # Analyser concentration
        if not regions:
            return {'balanced': True}

        max_count = max(regions.values())
        min_count = min(regions.values())
        avg_count = sum(regions.values()) / len(regions)

        # Ratio de concentration
        concentration_ratio = max_count / avg_count if avg_count > 0 else 0

        return {
            'num_regions': len(regions),
            'max_detections_per_region': max_count,
            'min_detections_per_region': min_count,
            'avg_detections_per_region': avg_count,
            'concentration_ratio': concentration_ratio,
            'balanced': concentration_ratio < 2.0  # Seuil arbitraire
        }


# Politique de consentement GDPR
GDPR_POLICY = """
POLITIQUE DE CONFIDENTIALITÉ - Urban Waste Detection

1. DONNÉES COLLECTÉES
   - Images de déchets urbains
   - Localisation GPS approximative (précision réduite à ~1km)
   - Métadonnées techniques (date, confiance modèle)

2. ANONYMISATION
   - Floutage automatique des visages
   - Suppression des métadonnées EXIF
   - Réduction précision GPS

3. UTILISATION DES DONNÉES
   - Détection et signalement de déchets
   - Amélioration du modèle IA
   - Statistiques urbaines anonymisées

4. CONSERVATION
   - Images: 30 jours maximum
   - Statistiques agrégées: conservation illimitée
   - Aucune donnée personnelle identifiable

5. DROITS UTILISATEURS (GDPR)
   - Accès aux données
   - Rectification
   - Suppression
   - Opposition au traitement

Contact: privacy@wastedetection.com
"""
