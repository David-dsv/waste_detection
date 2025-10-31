"""
Fine-tuning RF-DETR pour Détection de Déchets Urbains
======================================================

Script d'entraînement du modèle RT-DETR (Real-Time Detection Transformer)
sur le dataset TACO préparé.

RF-DETR combine:
- Architecture Transformer efficace
- Détection temps réel (30+ FPS)
- Haute précision (mAP >0.8)

Auteur: Votre Nom
Date: 2025
"""

import os
import argparse
import yaml
from pathlib import Path
from datetime import datetime
import json

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

import numpy as np
from PIL import Image
import cv2
from tqdm import tqdm

# Métriques
from torchmetrics.detection.mean_ap import MeanAveragePrecision

# Logging
from torch.utils.tensorboard import SummaryWriter
import wandb

# Note: RT-DETR peut nécessiter installation depuis GitHub
# pip install git+https://github.com/lyuwenyu/RT-DETR.git
try:
    from rtdetr_pytorch import RTDETR
    from rtdetr_pytorch.tools import train, val
except ImportError:
    print("⚠️ RT-DETR non installé. Installation...")
    print("pip install git+https://github.com/lyuwenyu/RT-DETR.git")


class WasteDetectionDataset(Dataset):
    """Dataset custom pour déchets urbains (format YOLO)."""

    def __init__(
        self,
        images_dir: str,
        labels_dir: str,
        img_size: int = 640,
        augment: bool = False
    ):
        """
        Args:
            images_dir: Dossier des images
            labels_dir: Dossier des labels (format YOLO)
            img_size: Taille image redimensionnée
            augment: Appliquer augmentation
        """
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)
        self.img_size = img_size
        self.augment = augment

        # Lister images
        self.image_files = sorted(list(self.images_dir.glob("*.jpg")))
        print(f"  📸 {len(self.image_files)} images chargées")

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        """Retourne (image, targets) au format COCO."""
        img_path = self.image_files[idx]
        label_path = self.labels_dir / f"{img_path.stem}.txt"

        # Charger image
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]

        # Redimensionner
        image_resized = cv2.resize(image, (self.img_size, self.img_size))
        image_tensor = torch.from_numpy(image_resized).permute(2, 0, 1).float() / 255.0

        # Charger labels
        boxes = []
        labels = []

        if label_path.exists():
            with open(label_path, 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        x_center, y_center, box_w, box_h = map(float, parts[1:])

                        # Convertir YOLO normalisé -> pixels redimensionnés
                        x_center *= self.img_size
                        y_center *= self.img_size
                        box_w *= self.img_size
                        box_h *= self.img_size

                        # Convertir center -> xyxy
                        x1 = x_center - box_w / 2
                        y1 = y_center - box_h / 2
                        x2 = x_center + box_w / 2
                        y2 = y_center + box_h / 2

                        boxes.append([x1, y1, x2, y2])
                        labels.append(class_id)

        # Créer target dict (format COCO)
        target = {
            'boxes': torch.as_tensor(boxes, dtype=torch.float32) if boxes else torch.zeros((0, 4)),
            'labels': torch.as_tensor(labels, dtype=torch.int64) if labels else torch.zeros((0,), dtype=torch.int64),
            'image_id': torch.tensor([idx]),
            'orig_size': torch.as_tensor([h, w]),
        }

        return image_tensor, target


class RTDETRTrainer:
    """Entraîneur pour RT-DETR."""

    def __init__(
        self,
        config_path: str,
        device: str = None,
        use_wandb: bool = False
    ):
        """
        Args:
            config_path: Chemin vers dataset.yaml
            device: 'cuda' ou 'cpu'
            use_wandb: Utiliser Weights & Biases
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_wandb = use_wandb

        # Charger config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.num_classes = self.config['nc']
        self.class_names = self.config['names']
        self.data_path = Path(self.config['path'])

        print(f"\n🎯 Configuration chargée:")
        print(f"  - Classes: {self.num_classes}")
        print(f"  - Device: {self.device}")
        print(f"  - Data path: {self.data_path}")

        # Créer dossier outputs
        self.output_dir = Path("./outputs") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # TensorBoard
        self.writer = SummaryWriter(log_dir=str(self.output_dir / "logs"))

        # Weights & Biases
        if self.use_wandb:
            wandb.init(
                project="urban-waste-detection",
                config={
                    "num_classes": self.num_classes,
                    "device": self.device,
                }
            )

    def create_model(self, pretrained: bool = True) -> nn.Module:
        """
        Crée le modèle RT-DETR.

        Args:
            pretrained: Utiliser poids pré-entraînés COCO

        Returns:
            Modèle RT-DETR
        """
        print("\n🏗️ Création du modèle RT-DETR...")

        # Charger RT-DETR pré-entraîné
        # Note: Adapter selon l'API réelle de RT-DETR
        model_config = {
            'num_classes': self.num_classes,
            'backbone': 'resnet50',  # ou 'resnet101'
            'num_queries': 300,
            'num_decoder_layers': 6,
        }

        # Simuler chargement modèle (adapter avec vraie API RT-DETR)
        print("  ⚠️ Exemple simplifié - Adapter avec RT-DETR officiel")
        print("  💡 Voir: https://github.com/lyuwenyu/RT-DETR")

        # Placeholder - remplacer par:
        # model = RTDETR(num_classes=self.num_classes, pretrained=pretrained)

        class PlaceholderRTDETR(nn.Module):
            """Placeholder - remplacer par vrai RT-DETR."""
            def __init__(self, num_classes):
                super().__init__()
                self.num_classes = num_classes
                # Architecture simplifiée pour démo
                self.backbone = nn.Sequential(
                    nn.Conv2d(3, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                )
                self.head = nn.Linear(64, num_classes * 4)  # bbox predictions

            def forward(self, images, targets=None):
                # Simuler forward pass
                batch_size = images.shape[0]
                features = self.backbone(images)
                # Retourner format attendu
                return {
                    'pred_logits': torch.randn(batch_size, 300, self.num_classes),
                    'pred_boxes': torch.randn(batch_size, 300, 4),
                }

        model = PlaceholderRTDETR(num_classes=self.num_classes)

        model = model.to(self.device)

        print(f"  ✅ Modèle créé avec {sum(p.numel() for p in model.parameters())/1e6:.2f}M paramètres")

        return model

    def create_dataloaders(
        self,
        batch_size: int = 16,
        num_workers: int = 4
    ):
        """
        Crée les dataloaders train/val/test.

        Args:
            batch_size: Taille du batch
            num_workers: Workers pour chargement parallèle

        Returns:
            (train_loader, val_loader, test_loader)
        """
        print(f"\n📦 Création dataloaders (batch_size={batch_size})...")

        # Datasets
        train_dataset = WasteDetectionDataset(
            images_dir=self.data_path / "train" / "images",
            labels_dir=self.data_path / "train" / "labels",
            augment=True
        )

        val_dataset = WasteDetectionDataset(
            images_dir=self.data_path / "val" / "images",
            labels_dir=self.data_path / "val" / "labels",
            augment=False
        )

        test_dataset = WasteDetectionDataset(
            images_dir=self.data_path / "test" / "images",
            labels_dir=self.data_path / "test" / "labels",
            augment=False
        )

        # Dataloaders
        def collate_fn(batch):
            images, targets = zip(*batch)
            images = torch.stack(images)
            return images, targets

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=True if self.device == 'cuda' else False
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            collate_fn=collate_fn,
            pin_memory=True if self.device == 'cuda' else False
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            collate_fn=collate_fn
        )

        print(f"  ✅ Train: {len(train_dataset)} images")
        print(f"  ✅ Val: {len(val_dataset)} images")
        print(f"  ✅ Test: {len(test_dataset)} images")

        return train_loader, val_loader, test_loader

    def train_epoch(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        epoch: int
    ) -> float:
        """
        Entraîne une époque.

        Args:
            model: Modèle RT-DETR
            dataloader: Dataloader train
            optimizer: Optimiseur
            epoch: Numéro époque

        Returns:
            Loss moyenne
        """
        model.train()
        total_loss = 0.0

        pbar = tqdm(dataloader, desc=f"Epoch {epoch}")

        for batch_idx, (images, targets) in enumerate(pbar):
            images = images.to(self.device)

            # Forward
            outputs = model(images, targets)

            # Calculer loss (adapter selon RT-DETR)
            # RT-DETR utilise généralement une combinaison de:
            # - Classification loss
            # - Bbox regression loss (L1 + GIoU)
            # - Matcher loss (Hungarian matching)

            # Placeholder - remplacer par vraie loss RT-DETR
            loss = outputs['pred_logits'].mean() + outputs['pred_boxes'].mean()

            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            # Update progress bar
            pbar.set_postfix({'loss': loss.item()})

            # Log TensorBoard
            global_step = epoch * len(dataloader) + batch_idx
            self.writer.add_scalar('train/loss', loss.item(), global_step)

        avg_loss = total_loss / len(dataloader)
        return avg_loss

    @torch.no_grad()
    def validate(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        epoch: int
    ) -> dict:
        """
        Validation du modèle.

        Args:
            model: Modèle RT-DETR
            dataloader: Dataloader val
            epoch: Numéro époque

        Returns:
            Métriques (mAP, etc.)
        """
        model.eval()

        # Métriques
        metric = MeanAveragePrecision(
            box_format='xyxy',
            iou_type='bbox'
        )

        all_predictions = []
        all_targets = []

        for images, targets in tqdm(dataloader, desc="Validation"):
            images = images.to(self.device)

            # Inférence
            outputs = model(images)

            # Post-processing (NMS, etc.)
            # Adapter selon RT-DETR
            # predictions = post_process(outputs, confidence_threshold=0.5)

            # Placeholder
            predictions = [
                {
                    'boxes': outputs['pred_boxes'][i][:10],  # Top 10
                    'scores': torch.sigmoid(outputs['pred_logits'][i][:10, 0]),
                    'labels': torch.argmax(outputs['pred_logits'][i][:10], dim=-1)
                }
                for i in range(len(images))
            ]

            all_predictions.extend(predictions)
            all_targets.extend(targets)

        # Calculer mAP
        metric.update(all_predictions, all_targets)
        metrics = metric.compute()

        # Log métriques
        print(f"\n📊 Validation Epoch {epoch}:")
        print(f"  - mAP@0.5: {metrics['map_50']:.4f}")
        print(f"  - mAP@0.5:0.95: {metrics['map']:.4f}")

        self.writer.add_scalar('val/mAP_50', metrics['map_50'], epoch)
        self.writer.add_scalar('val/mAP', metrics['map'], epoch)

        if self.use_wandb:
            wandb.log({
                'val/mAP_50': metrics['map_50'],
                'val/mAP': metrics['map'],
                'epoch': epoch
            })

        return metrics

    def train(
        self,
        epochs: int = 50,
        batch_size: int = 16,
        lr: float = 1e-4,
        save_every: int = 5
    ):
        """
        Pipeline d'entraînement complet.

        Args:
            epochs: Nombre d'époques
            batch_size: Taille batch
            lr: Learning rate
            save_every: Sauvegarder tous les N epochs
        """
        print("\n🚀 Démarrage entraînement RT-DETR")
        print("=" * 60)

        # Créer modèle
        model = self.create_model(pretrained=True)

        # Créer dataloaders
        train_loader, val_loader, test_loader = self.create_dataloaders(
            batch_size=batch_size
        )

        # Optimiseur
        optimizer = AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

        # Scheduler
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

        # Training loop
        best_map = 0.0

        for epoch in range(1, epochs + 1):
            print(f"\n{'='*60}")
            print(f"Epoch {epoch}/{epochs}")
            print('='*60)

            # Train
            train_loss = self.train_epoch(model, train_loader, optimizer, epoch)
            print(f"Train Loss: {train_loss:.4f}")

            # Validate
            if epoch % 5 == 0:  # Valider tous les 5 epochs
                metrics = self.validate(model, val_loader, epoch)

                # Sauvegarder meilleur modèle
                if metrics['map_50'] > best_map:
                    best_map = metrics['map_50']
                    save_path = self.output_dir / "best_model.pth"
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': model.state_dict(),
                        'optimizer_state_dict': optimizer.state_dict(),
                        'mAP_50': best_map,
                    }, save_path)
                    print(f"  💾 Meilleur modèle sauvegardé (mAP@0.5={best_map:.4f})")

            # Sauvegarder checkpoint
            if epoch % save_every == 0:
                checkpoint_path = self.output_dir / f"checkpoint_epoch_{epoch}.pth"
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                }, checkpoint_path)

            # Update scheduler
            scheduler.step()

        print("\n✅ Entraînement terminé!")
        print(f"📁 Modèles sauvegardés dans: {self.output_dir}")

        # Test final
        print("\n🧪 Évaluation finale sur test set...")
        test_metrics = self.validate(model, test_loader, epoch=-1)

        # Sauvegarder rapport final
        report = {
            'best_mAP_50': float(best_map),
            'test_mAP_50': float(test_metrics['map_50']),
            'test_mAP': float(test_metrics['map']),
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': lr,
        }

        with open(self.output_dir / "training_report.json", 'w') as f:
            json.dump(report, f, indent=2)

        return model, report


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Fine-tune RT-DETR pour détection déchets")

    parser.add_argument('--config', type=str, default='./data/taco_processed/dataset.yaml',
                        help='Chemin vers dataset.yaml')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Nombre époques (default: 50)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Taille batch (default: 16)')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate (default: 1e-4)')
    parser.add_argument('--device', type=str, default=None,
                        help='Device (cuda/cpu, default: auto)')
    parser.add_argument('--wandb', action='store_true',
                        help='Utiliser Weights & Biases')

    args = parser.parse_args()

    # Créer trainer
    trainer = RTDETRTrainer(
        config_path=args.config,
        device=args.device,
        use_wandb=args.wandb
    )

    # Entraîner
    model, report = trainer.train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )

    print("\n🎉 Fine-tuning RT-DETR terminé avec succès!")
    print(f"\n📊 Résultats finaux:")
    print(f"  - mAP@0.5 (best): {report['best_mAP_50']:.4f}")
    print(f"  - mAP@0.5 (test): {report['test_mAP_50']:.4f}")
    print(f"  - mAP@0.5:0.95 (test): {report['test_mAP']:.4f}")


if __name__ == "__main__":
    main()
