"""
Préparation du Dataset TACO pour Fine-tuning RF-DETR
====================================================

Ce script télécharge et prépare le dataset TACO (Trash Annotations in Context)
pour l'entraînement du modèle RF-DETR.

Dataset TACO: http://tacodataset.org/
- 1,500+ images haute résolution
- 60+ catégories de déchets annotées
- Annotations au format COCO

Auteur: Votre Nom
Date: 2025
"""

import os
import json
import shutil
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
from roboflow import Roboflow
import albumentations as A


class TACODatasetPreparator:
    """Préparateur du dataset TACO avec augmentation et conversion."""

    # Classes personnalisées pour déchets urbains
    CUSTOM_CLASSES = {
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

    # Mapping TACO -> Classes personnalisées
    TACO_TO_CUSTOM = {
        "Plastic bottle": 0,
        "Plastic bag & wrapper": 1,
        "Bottle cap": 0,  # Groupé avec plastic_bottle
        "Metal bottle cap": 2,
        "Aluminium foil": 2,
        "Can": 2,
        "Glass bottle": 3,
        "Broken glass": 3,
        "Carton": 4,
        "Paper bag": 4,
        "Paper": 5,
        "Cigarette": 8,
        "Food waste": 7,
        "Styrofoam piece": 1,
        "Plastic film": 1,
        "Cup": 9,
        "Plastic container": 9,
    }

    def __init__(
        self,
        data_dir: str = "./data",
        output_dir: str = "./data/processed",
        train_split: float = 0.8,
        val_split: float = 0.1
    ):
        """
        Args:
            data_dir: Répertoire de téléchargement TACO
            output_dir: Répertoire de sortie préparé
            train_split: Proportion train (0.8 = 80%)
            val_split: Proportion validation (0.1 = 10%)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.train_split = train_split
        self.val_split = val_split

        # Créer les dossiers
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for split in ["train", "val", "test"]:
            (self.output_dir / split / "images").mkdir(parents=True, exist_ok=True)
            (self.output_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    def download_taco(self) -> str:
        """
        Télécharge le dataset TACO depuis GitHub.

        Returns:
            Chemin vers le dossier TACO décompressé
        """
        print("📥 Téléchargement du dataset TACO...")

        taco_url = "https://github.com/pedropro/TACO/archive/refs/heads/master.zip"
        zip_path = self.data_dir / "taco.zip"
        extract_path = self.data_dir / "TACO-master"

        if extract_path.exists():
            print("✅ TACO déjà téléchargé")
            return str(extract_path)

        # Télécharger
        response = requests.get(taco_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(zip_path, 'wb') as f, tqdm(
            desc="Téléchargement",
            total=total_size,
            unit='iB',
            unit_scale=True
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)

        # Décompresser
        print("📦 Extraction...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.data_dir)

        zip_path.unlink()  # Supprimer le zip
        print(f"✅ Dataset TACO extrait dans {extract_path}")

        return str(extract_path)

    def load_coco_annotations(self, annotation_file: str) -> Dict:
        """
        Charge les annotations COCO de TACO.

        Args:
            annotation_file: Chemin vers annotations.json

        Returns:
            Dictionnaire annotations COCO
        """
        print(f"📄 Chargement annotations: {annotation_file}")

        with open(annotation_file, 'r') as f:
            coco_data = json.load(f)

        print(f"  - Images: {len(coco_data['images'])}")
        print(f"  - Annotations: {len(coco_data['annotations'])}")
        print(f"  - Catégories: {len(coco_data['categories'])}")

        return coco_data

    def convert_to_custom_classes(
        self,
        coco_data: Dict
    ) -> Tuple[Dict, Dict[int, int]]:
        """
        Convertit les classes TACO vers nos classes personnalisées.

        Args:
            coco_data: Données COCO originales

        Returns:
            (coco_data_converted, category_mapping)
        """
        print("🔄 Conversion vers classes personnalisées...")

        # Créer mapping id_category -> nom
        cat_id_to_name = {
            cat['id']: cat['name']
            for cat in coco_data['categories']
        }

        # Créer mapping id_category_old -> id_category_new
        category_mapping = {}
        for cat_id, cat_name in cat_id_to_name.items():
            if cat_name in self.TACO_TO_CUSTOM:
                category_mapping[cat_id] = self.TACO_TO_CUSTOM[cat_name]

        # Convertir annotations
        converted_annotations = []
        for ann in coco_data['annotations']:
            if ann['category_id'] in category_mapping:
                ann_copy = ann.copy()
                ann_copy['category_id'] = category_mapping[ann['category_id']]
                converted_annotations.append(ann_copy)

        # Mettre à jour categories
        new_categories = [
            {"id": cat_id, "name": cat_name}
            for cat_id, cat_name in self.CUSTOM_CLASSES.items()
        ]

        coco_converted = coco_data.copy()
        coco_converted['categories'] = new_categories
        coco_converted['annotations'] = converted_annotations

        print(f"  ✅ {len(converted_annotations)} annotations converties")
        print(f"  ✅ {len(new_categories)} classes personnalisées")

        return coco_converted, category_mapping

    def split_dataset(
        self,
        coco_data: Dict
    ) -> Tuple[Dict, Dict, Dict]:
        """
        Divise le dataset en train/val/test.

        Args:
            coco_data: Données COCO complètes

        Returns:
            (coco_train, coco_val, coco_test)
        """
        print(f"✂️ Division dataset: {self.train_split}/{self.val_split}/test...")

        # Grouper annotations par image
        img_to_anns = defaultdict(list)
        for ann in coco_data['annotations']:
            img_to_anns[ann['image_id']].append(ann)

        # Mélanger images
        images = coco_data['images'].copy()
        np.random.seed(42)
        np.random.shuffle(images)

        # Calculer indices split
        n_images = len(images)
        n_train = int(n_images * self.train_split)
        n_val = int(n_images * self.val_split)

        # Diviser
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]

        # Créer datasets COCO par split
        def create_split_coco(split_images):
            split_img_ids = {img['id'] for img in split_images}
            split_anns = [
                ann for ann in coco_data['annotations']
                if ann['image_id'] in split_img_ids
            ]
            return {
                'images': split_images,
                'annotations': split_anns,
                'categories': coco_data['categories']
            }

        coco_train = create_split_coco(train_images)
        coco_val = create_split_coco(val_images)
        coco_test = create_split_coco(test_images)

        print(f"  📊 Train: {len(train_images)} images, {len(coco_train['annotations'])} annotations")
        print(f"  📊 Val: {len(val_images)} images, {len(coco_val['annotations'])} annotations")
        print(f"  📊 Test: {len(test_images)} images, {len(coco_test['annotations'])} annotations")

        return coco_train, coco_val, coco_test

    def get_augmentation_pipeline(self, mode: str = "train") -> A.Compose:
        """
        Pipeline d'augmentation de données.

        Args:
            mode: "train" ou "val"

        Returns:
            Albumentations Compose
        """
        if mode == "train":
            return A.Compose([
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.2),
                A.RandomRotate90(p=0.3),
                A.ShiftScaleRotate(
                    shift_limit=0.1,
                    scale_limit=0.2,
                    rotate_limit=30,
                    p=0.5
                ),
                A.OneOf([
                    A.RandomBrightnessContrast(p=1),
                    A.RandomGamma(p=1),
                    A.HueSaturationValue(p=1),
                ], p=0.5),
                A.OneOf([
                    A.GaussianBlur(p=1),
                    A.MedianBlur(blur_limit=5, p=1),
                    A.MotionBlur(p=1),
                ], p=0.3),
                A.OneOf([
                    A.GaussNoise(p=1),
                    A.ISONoise(p=1),
                ], p=0.2),
                A.RandomShadow(p=0.3),
                A.RandomFog(p=0.1),
            ], bbox_params=A.BboxParams(
                format='coco',
                label_fields=['category_ids'],
                min_visibility=0.3
            ))
        else:
            return A.Compose([
                # Pas d'augmentation pour val/test
            ], bbox_params=A.BboxParams(
                format='coco',
                label_fields=['category_ids']
            ))

    def process_and_save_split(
        self,
        coco_data: Dict,
        split_name: str,
        taco_images_dir: Path,
        apply_augmentation: bool = True
    ):
        """
        Traite et sauvegarde un split (train/val/test).

        Args:
            coco_data: Données COCO du split
            split_name: "train", "val" ou "test"
            taco_images_dir: Chemin vers images TACO
            apply_augmentation: Appliquer augmentation
        """
        print(f"\n🔧 Traitement split '{split_name}'...")

        # Grouper annotations par image
        img_to_anns = defaultdict(list)
        for ann in coco_data['annotations']:
            img_to_anns[ann['image_id']].append(ann)

        # Pipeline augmentation
        transform = self.get_augmentation_pipeline(
            "train" if apply_augmentation and split_name == "train" else "val"
        )

        # Chemins sortie
        output_images_dir = self.output_dir / split_name / "images"
        output_labels_dir = self.output_dir / split_name / "labels"

        processed_count = 0

        for img_info in tqdm(coco_data['images'], desc=f"Processing {split_name}"):
            img_id = img_info['id']
            img_filename = img_info['file_name']
            img_path = taco_images_dir / img_filename

            if not img_path.exists():
                continue

            # Charger image
            image = cv2.imread(str(img_path))
            if image is None:
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w = image.shape[:2]

            # Récupérer annotations
            anns = img_to_anns[img_id]
            if not anns:
                continue

            # Préparer bboxes pour augmentation (format COCO: [x, y, width, height])
            bboxes = []
            category_ids = []

            for ann in anns:
                bbox = ann['bbox']  # [x, y, w, h]
                bboxes.append(bbox)
                category_ids.append(ann['category_id'])

            # Appliquer augmentation
            try:
                transformed = transform(
                    image=image,
                    bboxes=bboxes,
                    category_ids=category_ids
                )

                aug_image = transformed['image']
                aug_bboxes = transformed['bboxes']
                aug_category_ids = transformed['category_ids']

            except Exception as e:
                # En cas d'erreur augmentation, utiliser originaux
                aug_image = image
                aug_bboxes = bboxes
                aug_category_ids = category_ids

            # Sauvegarder image
            output_img_path = output_images_dir / f"{split_name}_{img_id}.jpg"
            aug_image_bgr = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_img_path), aug_image_bgr)

            # Sauvegarder labels (format YOLO: class x_center y_center width height, normalisé)
            output_label_path = output_labels_dir / f"{split_name}_{img_id}.txt"

            with open(output_label_path, 'w') as f:
                for bbox, cat_id in zip(aug_bboxes, aug_category_ids):
                    x, y, box_w, box_h = bbox

                    # Convertir COCO -> YOLO (normalisé)
                    x_center = (x + box_w / 2) / w
                    y_center = (y + box_h / 2) / h
                    norm_w = box_w / w
                    norm_h = box_h / h

                    # Écrire ligne: class x_center y_center width height
                    f.write(f"{cat_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}\n")

            processed_count += 1

        print(f"  ✅ {processed_count} images traitées pour '{split_name}'")

    def create_yaml_config(self):
        """Crée le fichier de configuration YAML pour l'entraînement."""
        yaml_content = f"""# Configuration Dataset Urban Waste Detection
# Format: YOLO / RF-DETR compatible

path: {self.output_dir.absolute()}
train: train/images
val: val/images
test: test/images

# Classes
nc: {len(self.CUSTOM_CLASSES)}
names:
"""
        for cat_id, cat_name in self.CUSTOM_CLASSES.items():
            yaml_content += f"  {cat_id}: {cat_name}\n"

        yaml_path = self.output_dir / "dataset.yaml"
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)

        print(f"\n📝 Configuration sauvegardée: {yaml_path}")

    def generate_statistics(self, coco_train: Dict, coco_val: Dict, coco_test: Dict):
        """Génère des statistiques du dataset."""
        print("\n📊 Statistiques du Dataset:")
        print("=" * 60)

        def count_by_category(coco_data):
            counts = defaultdict(int)
            for ann in coco_data['annotations']:
                counts[ann['category_id']] += 1
            return counts

        train_counts = count_by_category(coco_train)
        val_counts = count_by_category(coco_val)
        test_counts = count_by_category(coco_test)

        print(f"\n{'Classe':<25} {'Train':<10} {'Val':<10} {'Test':<10}")
        print("-" * 60)

        for cat_id, cat_name in self.CUSTOM_CLASSES.items():
            print(f"{cat_name:<25} {train_counts[cat_id]:<10} {val_counts[cat_id]:<10} {test_counts[cat_id]:<10}")

        print("-" * 60)
        print(f"{'TOTAL':<25} {sum(train_counts.values()):<10} {sum(val_counts.values()):<10} {sum(test_counts.values()):<10}")
        print("=" * 60)

    def run(self):
        """Pipeline complet de préparation."""
        print("\n🚀 Démarrage préparation dataset TACO\n")

        # 1. Télécharger TACO
        taco_path = self.download_taco()

        # 2. Charger annotations
        annotation_file = Path(taco_path) / "data" / "annotations.json"
        coco_data = self.load_coco_annotations(annotation_file)

        # 3. Convertir classes
        coco_converted, _ = self.convert_to_custom_classes(coco_data)

        # 4. Diviser dataset
        coco_train, coco_val, coco_test = self.split_dataset(coco_converted)

        # 5. Traiter et sauvegarder chaque split
        taco_images_dir = Path(taco_path) / "data"

        self.process_and_save_split(coco_train, "train", taco_images_dir, apply_augmentation=True)
        self.process_and_save_split(coco_val, "val", taco_images_dir, apply_augmentation=False)
        self.process_and_save_split(coco_test, "test", taco_images_dir, apply_augmentation=False)

        # 6. Créer config YAML
        self.create_yaml_config()

        # 7. Statistiques
        self.generate_statistics(coco_train, coco_val, coco_test)

        print("\n✅ Préparation dataset terminée avec succès!")
        print(f"📁 Dataset prêt dans: {self.output_dir}")


def integrate_with_roboflow(
    api_key: str,
    workspace: str,
    project_name: str = "urban-waste-detection"
):
    """
    Optionnel: Upload du dataset vers Roboflow pour annotation supplémentaire.

    Args:
        api_key: Clé API Roboflow
        workspace: Nom du workspace Roboflow
        project_name: Nom du projet
    """
    print("\n☁️ Intégration avec Roboflow...")

    rf = Roboflow(api_key=api_key)
    workspace = rf.workspace(workspace)

    # Créer ou récupérer projet
    try:
        project = workspace.project(project_name)
        print(f"  ✅ Projet existant: {project_name}")
    except:
        print(f"  🆕 Création nouveau projet: {project_name}")
        # Code pour créer projet (nécessite API Roboflow)

    print("  💡 Utilisez Roboflow pour:")
    print("     - Annotations supplémentaires")
    print("     - Augmentation avancée")
    print("     - Versioning dataset")
    print("     - Export multi-formats (YOLO, COCO, TFRecord)")


if __name__ == "__main__":
    # Configuration
    preparator = TACODatasetPreparator(
        data_dir="./data/taco_raw",
        output_dir="./data/taco_processed",
        train_split=0.8,
        val_split=0.1
    )

    # Exécuter pipeline
    preparator.run()

    # Optionnel: Roboflow integration
    # ROBOFLOW_API_KEY = "votre_api_key"
    # integrate_with_roboflow(ROBOFLOW_API_KEY, "votre_workspace")
