"""
Analyseur IA avec Gemini 2.0 Flash pour analyser les détections de déchets.

Ce service prend les détections RF-DETR et génère des analyses intelligentes,
recommandations et rapports en langage naturel.
"""

import os
from typing import List, Dict, Optional
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai non installé. Installez avec: pip install google-generativeai")


class GeminiWasteAnalyzer:
    """Analyseur intelligent de déchets avec Gemini 2.0 Flash."""

    def __init__(self, api_key: str = None):
        """
        Initialise l'analyseur Gemini.

        Args:
            api_key: Clé API Gemini (ou depuis .env)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai requis: pip install google-generativeai")

        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY requis dans .env")

        # Configurer Gemini
        genai.configure(api_key=self.api_key)

        # Utiliser Gemini 2.0 Flash (rapide et performant)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.model = genai.GenerativeModel(model_name)

        print(f"✅ Gemini Analyzer initialisé avec modèle: {model_name}")

    def analyze_detections(
        self,
        detections: List[Dict],
        location: Optional[Dict] = None,
        image_context: str = ""
    ) -> Dict:
        """
        Analyse complète des détections avec contexte.

        Args:
            detections: Liste des détections RF-DETR
            location: Localisation GPS optionnelle
            image_context: Contexte additionnel (ex: "zone résidentielle")

        Returns:
            Analyse structurée avec recommandations
        """
        if not detections:
            return {
                'summary': "Aucun déchet détecté sur l'image.",
                'severity': 'none',
                'recommendations': []
            }

        # Préparer contexte pour Gemini
        context = self._prepare_context(detections, location, image_context)

        # Prompt structuré pour Gemini
        prompt = f"""Tu es un expert en gestion des déchets urbains et environnement.

Analyse les déchets détectés ci-dessous et fournis une évaluation professionnelle.

DONNÉES DE DÉTECTION:
{context}

INSTRUCTIONS:
1. Résume la situation en 2-3 phrases claires et concises
2. Évalue la sévérité (faible/moyenne/élevée/critique)
3. Identifie les risques environnementaux et sanitaires
4. Fournis 3-5 recommandations d'action concrètes et priorisées
5. Estime l'urgence d'intervention (0-10)
6. Suggère le type d'équipe nécessaire (manuel/mécanisé)

FORMAT DE RÉPONSE (JSON):
{{
    "summary": "Résumé de la situation",
    "severity": "faible|moyenne|élevée|critique",
    "severity_score": 0-10,
    "environmental_risks": ["risque1", "risque2"],
    "health_risks": ["risque1", "risque2"],
    "recommendations": [
        {{"action": "action1", "priority": "haute|moyenne|basse", "reason": "justification"}},
        {{"action": "action2", "priority": "haute|moyenne|basse", "reason": "justification"}}
    ],
    "urgency_score": 0-10,
    "intervention_type": "manuel|mécanisé|mixte",
    "estimated_time": "temps estimé",
    "insights": "observations supplémentaires"
}}

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""

        try:
            # Générer analyse avec Gemini
            response = self.model.generate_content(prompt)

            # Parser la réponse JSON
            result_text = response.text.strip()

            # Nettoyer markdown si présent
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]

            analysis = json.loads(result_text.strip())

            # Ajouter métadonnées
            analysis['model'] = 'gemini-2.0-flash'
            analysis['total_objects'] = len(detections)
            analysis['detection_details'] = self._summarize_detections(detections)

            return analysis

        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(f"Réponse brute: {response.text}")
            # Fallback
            return self._fallback_analysis(detections)

        except Exception as e:
            print(f"❌ Erreur Gemini: {e}")
            return self._fallback_analysis(detections)

    def generate_alert_message(
        self,
        detections: List[Dict],
        analysis: Dict,
        location: Optional[Dict] = None
    ) -> str:
        """
        Génère un message d'alerte professionnel et actionnable.

        Args:
            detections: Détections
            analysis: Analyse Gemini
            location: Localisation

        Returns:
            Message d'alerte formaté
        """
        prompt = f"""Génère un message d'alerte professionnel pour les autorités municipales.

SITUATION:
{json.dumps(analysis, indent=2, ensure_ascii=False)}

DÉTECTIONS:
{len(detections)} objets détectés
Types: {', '.join(set(d['class_name'] for d in detections))}
{f"Localisation: {location['latitude']}, {location['longitude']}" if location else ""}

INSTRUCTIONS:
- Ton professionnel et factuel
- Maximum 200 mots
- Inclure sévérité, localisation, actions recommandées
- Urgence claire
- Format email lisible

Commence directement par le message, sans formule d'appel."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ Erreur génération message: {e}")
            return self._fallback_message(detections, analysis, location)

    def generate_daily_report(
        self,
        detections_data: List[Dict],
        period: str = "aujourd'hui"
    ) -> str:
        """
        Génère un rapport quotidien automatisé.

        Args:
            detections_data: Données de toutes les détections
            period: Période du rapport

        Returns:
            Rapport formaté en markdown
        """
        # Statistiques
        total_detections = len(detections_data)
        total_objects = sum(d.get('num_objects', 0) for d in detections_data)

        # Compter par classe
        class_counts = {}
        for det in detections_data:
            for obj in det.get('objects', []):
                class_name = obj.get('class_name', 'unknown')
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        stats_text = f"""
STATISTIQUES {period.upper()}:
- Détections totales: {total_detections}
- Objets détectés: {total_objects}
- Types principaux: {', '.join(f"{k} ({v})" for k, v in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:5])}
"""

        prompt = f"""Tu es un analyste environnemental. Génère un rapport quotidien professionnel.

{stats_text}

INSTRUCTIONS:
1. Executive Summary (3-4 phrases)
2. Analyse des Tendances (augmentation/diminution)
3. Zones Critiques (si applicable)
4. Recommandations Stratégiques (3-5 points)
5. Prévisions pour demain
6. Actions Prioritaires

FORMAT: Markdown structuré
LONGUEUR: 300-400 mots
TON: Professionnel, data-driven, actionnable

Titre: "📊 Rapport Quotidien - Gestion des Déchets Urbains"
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ Erreur génération rapport: {e}")
            return f"# Rapport Quotidien\n\n{stats_text}\n\nErreur génération analyse IA."

    def suggest_collection_route(
        self,
        hotspots: List[Dict]
    ) -> Dict:
        """
        Suggère un itinéraire optimal de collecte.

        Args:
            hotspots: Points chauds avec localisation et priorité

        Returns:
            Suggestion d'itinéraire avec justification
        """
        if not hotspots:
            return {'route': [], 'reasoning': 'Aucun point chaud identifié'}

        hotspots_text = "\n".join([
            f"- Point {i+1}: {hs.get('waste_count', 0)} déchets, "
            f"Priorité: {hs.get('priority', 'medium')}, "
            f"GPS: ({hs.get('location', {}).get('latitude', 'N/A')}, "
            f"{hs.get('location', {}).get('longitude', 'N/A')})"
            for i, hs in enumerate(hotspots[:10])
        ])

        prompt = f"""Tu es un expert en optimisation logistique urbaine.

POINTS CHAUDS DÉTECTÉS:
{hotspots_text}

CONTRAINTES:
- Minimiser distance totale
- Prioriser urgences (haute priorité)
- Capacité camion standard: 10 tonnes
- Équipe disponible: 8h

TÂCHE:
Génère un itinéraire optimal de collecte.

FORMAT JSON:
{{
    "route_order": [1, 3, 2, 4, 5],
    "reasoning": "explication de la logique",
    "estimated_duration": "temps total",
    "estimated_distance": "distance totale km",
    "team_size": nombre,
    "equipment_needed": ["équipement1", "équipement2"],
    "optimization_metrics": {{
        "priority_score": 0-10,
        "efficiency_score": 0-10
    }}
}}

Réponds UNIQUEMENT avec le JSON."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Nettoyer markdown
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]

            route = json.loads(result_text.strip())
            return route

        except Exception as e:
            print(f"❌ Erreur suggestion route: {e}")
            return {
                'route_order': list(range(len(hotspots))),
                'reasoning': 'Route par ordre de priorité',
                'estimated_duration': 'N/A'
            }

    def explain_detection(
        self,
        detection: Dict,
        for_citizen: bool = False
    ) -> str:
        """
        Explique une détection en langage naturel.

        Args:
            detection: Détection unique
            for_citizen: Si True, langage accessible au public

        Returns:
            Explication textuelle
        """
        audience = "citoyen lambda" if for_citizen else "professionnel de la gestion des déchets"

        prompt = f"""Explique cette détection de déchet pour un {audience}.

DÉTECTION:
- Type: {detection.get('class_name', 'inconnu')}
- Confiance: {detection.get('confidence', 0) * 100:.1f}%
- Localisation: {detection.get('bbox', [])}

INSTRUCTIONS:
- 2-3 phrases maximum
- Langage {"simple et pédagogique" if for_citizen else "technique"}
- {"Conseils pratiques" if for_citizen else "Implications opérationnelles"}

Pas de préambule, commence directement."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ Erreur explication: {e}")
            class_name = detection.get('class_name', 'déchet')
            conf = detection.get('confidence', 0) * 100
            return f"Un {class_name} a été détecté avec {conf:.0f}% de confiance."

    # Méthodes utilitaires privées

    def _prepare_context(
        self,
        detections: List[Dict],
        location: Optional[Dict],
        image_context: str
    ) -> str:
        """Prépare le contexte pour Gemini."""
        context_parts = []

        # Statistiques détections
        class_counts = {}
        avg_confidence = 0
        for det in detections:
            class_name = det.get('class_name', 'unknown')
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            avg_confidence += det.get('confidence', 0)

        avg_confidence /= len(detections) if detections else 1

        context_parts.append(f"Nombre total d'objets: {len(detections)}")
        context_parts.append(f"Confiance moyenne: {avg_confidence*100:.1f}%")
        context_parts.append(f"\nRépartition par type:")
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            context_parts.append(f"  - {class_name}: {count}")

        if location:
            context_parts.append(f"\nLocalisation: {location.get('latitude')}, {location.get('longitude')}")

        if image_context:
            context_parts.append(f"\nContexte: {image_context}")

        return "\n".join(context_parts)

    def _summarize_detections(self, detections: List[Dict]) -> Dict:
        """Résumé des détections."""
        class_counts = {}
        for det in detections:
            class_name = det.get('class_name', 'unknown')
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        return {
            'total': len(detections),
            'by_class': class_counts,
            'top_3': sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    def _fallback_analysis(self, detections: List[Dict]) -> Dict:
        """Analyse fallback si Gemini échoue."""
        total = len(detections)
        severity = 'faible' if total < 5 else 'moyenne' if total < 15 else 'élevée'

        return {
            'summary': f"{total} objet(s) détecté(s). Intervention recommandée.",
            'severity': severity,
            'severity_score': min(total, 10),
            'recommendations': [
                {'action': 'Collecte rapide', 'priority': 'haute', 'reason': 'Accumulation de déchets'}
            ],
            'urgency_score': min(total, 10),
            'model': 'fallback',
            'total_objects': total
        }

    def _fallback_message(
        self,
        detections: List[Dict],
        analysis: Dict,
        location: Optional[Dict]
    ) -> str:
        """Message fallback."""
        msg = f"ALERTE DÉCHETS - {analysis.get('severity', 'N/A').upper()}\n\n"
        msg += f"{len(detections)} objet(s) détecté(s).\n"
        if location:
            msg += f"Localisation: {location.get('latitude')}, {location.get('longitude')}\n"
        msg += f"\nIntervention recommandée.\n"
        return msg
