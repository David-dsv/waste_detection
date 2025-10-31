"""
Script d'entraînement YOLO11 sur le dataset TACO
Utilise le modèle YOLO11n (nano) pour une détection rapide des déchets
"""

from ultralytics import YOLO
import yaml
from datetime import datetime
import os

def train_yolo11_taco():
    """Entraîne YOLO11 sur le dataset TACO"""

    print("🚀 Début de l'entraînement YOLO11 sur TACO dataset")
    print("=" * 60)

    # Charger le modèle YOLO11n pré-entraîné
    print("\n📥 Chargement du modèle YOLO11n...")
    model = YOLO('yolo11n.pt')  # YOLO11 nano (le plus rapide)

    # Chemin vers le fichier de configuration du dataset
    data_yaml = 'taco_yolo_data/data.yaml'

    # Vérifier que le fichier existe
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(f"Fichier de configuration introuvable: {data_yaml}")

    # Afficher les paramètres d'entraînement
    print("\n📊 Paramètres d'entraînement:")
    print(f"   - Modèle: YOLO11n")
    print(f"   - Dataset: TACO (Trash Annotations in Context)")
    print(f"   - Epochs: 50")
    print(f"   - Image size: 640x640")
    print(f"   - Batch size: 16")
    print(f"   - Device: MPS (Apple Silicon)")

    # Timestamp pour le nom du modèle
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_name = 'runs/detect'
    run_name = f'yolo11n_taco_{timestamp}'

    print(f"\n🎯 Nom du run: {run_name}")
    print("\n" + "=" * 60)
    print("⚡ Démarrage de l'entraînement...\n")

    # Entraîner le modèle
    results = model.train(
        data=data_yaml,
        epochs=50,              # Nombre d'epochs
        imgsz=640,              # Taille des images
        batch=16,               # Batch size
        device='mps',           # MPS pour Apple Silicon
        workers=4,              # Nombre de workers
        patience=10,            # Early stopping patience
        save=True,              # Sauvegarder les checkpoints
        plots=True,             # Générer les graphiques
        project=project_name,
        name=run_name,
        exist_ok=True,

        # Augmentation de données
        hsv_h=0.015,           # Variation de teinte
        hsv_s=0.7,             # Variation de saturation
        hsv_v=0.4,             # Variation de luminosité
        degrees=10,            # Rotation aléatoire
        translate=0.1,         # Translation aléatoire
        scale=0.5,             # Zoom aléatoire
        shear=0.0,             # Distorsion
        perspective=0.0,       # Perspective
        flipud=0.0,            # Flip vertical
        fliplr=0.5,            # Flip horizontal
        mosaic=1.0,            # Mosaic augmentation
        mixup=0.1,             # Mixup augmentation

        # Optimisation
        optimizer='AdamW',     # Optimiseur AdamW
        lr0=0.001,            # Learning rate initial
        lrf=0.01,             # Learning rate final
        momentum=0.937,        # Momentum SGD
        weight_decay=0.0005,   # Weight decay
        warmup_epochs=3,       # Warmup epochs
        warmup_momentum=0.8,   # Warmup momentum
        warmup_bias_lr=0.1,    # Warmup bias learning rate

        # Autres paramètres
        amp=True,              # Automatic Mixed Precision
        fraction=1.0,          # Fraction du dataset à utiliser
        profile=False,         # Profiling
        overlap_mask=True,     # Overlap mask pour segmentation
        mask_ratio=4,          # Mask ratio
        dropout=0.0,           # Dropout
        val=True,              # Valider pendant l'entraînement
        verbose=True,          # Mode verbose
    )

    print("\n" + "=" * 60)
    print("✅ Entraînement terminé!")
    print("=" * 60)

    # Afficher les résultats
    print("\n📊 Résultats de l'entraînement:")
    print(f"   - mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   - mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    print(f"   - Precision: {results.results_dict.get('metrics/precision(B)', 'N/A')}")
    print(f"   - Recall: {results.results_dict.get('metrics/recall(B)', 'N/A')}")

    # Sauvegarder le meilleur modèle avec un nom explicite
    best_model_path = f'models/yolo11n_taco_{timestamp}.pt'
    os.makedirs('models', exist_ok=True)

    # Copier le meilleur modèle
    import shutil
    source = f'{project_name}/{run_name}/weights/best.pt'
    shutil.copy(source, best_model_path)

    print(f"\n💾 Meilleur modèle sauvegardé: {best_model_path}")
    print(f"📁 Dossier du run: {project_name}/{run_name}")

    return best_model_path

if __name__ == '__main__':
    try:
        model_path = train_yolo11_taco()
        print("\n🎉 Script terminé avec succès!")
        print(f"🔗 Utilisez ce modèle dans votre backend: {model_path}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise
