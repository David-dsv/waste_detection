#!/usr/bin/env python3
"""
Script de test pour la détection YOLO + Gemini
"""

import requests
import json
from pathlib import Path

# URL de l'API
API_URL = "http://localhost:5001/api/detect"

# Télécharger une image de test
print("📥 Téléchargement d'une image de test...")
test_image_url = "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800"
response = requests.get(test_image_url)

if response.status_code == 200:
    test_image_path = Path("test_bottle.jpg")
    test_image_path.write_bytes(response.content)
    print(f"✅ Image téléchargée: {test_image_path}")
else:
    print("❌ Erreur téléchargement image")
    exit(1)

# Envoyer à l'API
print(f"\n🚀 Envoi de l'image à {API_URL}...")
print("⏳ En attente (YOLO détection + Gemini analyse)...\n")

with open(test_image_path, 'rb') as f:
    files = {'image': f}
    data = {
        'source': 'test_script',
        'context': 'Test de détection de bouteille plastique'
    }

    try:
        response = requests.post(API_URL, files=files, data=data, timeout=60)

        if response.status_code == 200:
            result = response.json()

            print("=" * 70)
            print("✅ DÉTECTION RÉUSSIE")
            print("=" * 70)

            # Détections
            detections = result.get('detections', [])
            print(f"\n🔍 YOLO détecté: {len(detections)} objets/déchets\n")

            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class']} ({det['category']})")
                print(f"     Confiance: {det['confidence']:.1%}")
                print(f"     Bbox: {det['bbox']}")
                print()

            # Analyse Gemini
            ai_analysis = result.get('ai_analysis')
            if ai_analysis:
                print("\n" + "=" * 70)
                print("🧠 ANALYSE GEMINI 2.0 FLASH")
                print("=" * 70)
                print(f"\n📊 Sévérité: {ai_analysis.get('severity', 'N/A').upper()}")
                print(f"📈 Score d'urgence: {ai_analysis.get('urgency_score', 0)}/10")
                print(f"🔧 Type d'intervention: {ai_analysis.get('intervention_type', 'N/A')}")

                print(f"\n📝 Résumé:")
                print(f"   {ai_analysis.get('summary', 'N/A')}")

                if ai_analysis.get('recommendations'):
                    print(f"\n💡 Recommandations:")
                    for rec in ai_analysis['recommendations']:
                        print(f"   [{rec['priority']}] {rec['action']}")

                if ai_analysis.get('environmental_risks'):
                    print(f"\n🌍 Risques environnementaux:")
                    for risk in ai_analysis['environmental_risks']:
                        print(f"   - {risk}")

                print("\n" + "=" * 70)
            else:
                print("\n⚠️  Pas d'analyse Gemini disponible")

            # Fichiers générés
            print(f"\n📁 Fichiers générés:")
            print(f"   Original: uploads/{result.get('filename')}")
            print(f"   Annoté: uploads/{result.get('annotated_image')}")

        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Le serveur met trop de temps à répondre")
    except Exception as e:
        print(f"❌ Erreur: {e}")

print("\n✅ Test terminé!")
