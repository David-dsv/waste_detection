"""
Agent IA avec LangChain pour rapports automatisés.
"""

import os
from typing import List, Dict
from datetime import datetime, timedelta

try:
    from langchain.llms import OpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.agents import initialize_agent, Tool, AgentType
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain non installé - Agent IA désactivé")


class WasteReportAgent:
    """Agent IA pour génération de rapports automatisés."""

    def __init__(self, openai_api_key: str = None):
        """
        Args:
            openai_api_key: Clé API OpenAI
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain requis: pip install langchain langchain-openai")

        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY requis")

        # Initialiser LLM
        self.llm = OpenAI(
            temperature=0.7,
            openai_api_key=self.api_key,
            model_name="gpt-3.5-turbo-instruct"
        )

    def generate_daily_report(
        self,
        detections_data: List[Dict],
        date: datetime = None
    ) -> str:
        """
        Génère un rapport quotidien automatisé.

        Args:
            detections_data: Données des détections de la journée
            date: Date du rapport (défaut: aujourd'hui)

        Returns:
            Rapport textuel
        """
        date = date or datetime.utcnow()
        date_str = date.strftime('%Y-%m-%d')

        # Préparer statistiques
        total_detections = len(detections_data)
        if total_detections == 0:
            return f"Aucune détection pour le {date_str}."

        # Compter par classe
        class_counts = {}
        locations = []

        for det in detections_data:
            for obj in det.get('objects', []):
                class_name = obj['class_name']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

            if det.get('location'):
                locations.append(det['location'])

        # Créer prompt
        prompt_template = PromptTemplate(
            input_variables=["date", "total", "classes", "num_locations"],
            template="""
Tu es un expert en gestion des déchets urbains. Génère un rapport quotidien professionnel basé sur les données suivantes:

Date: {date}
Nombre total de déchets détectés: {total}
Répartition par type: {classes}
Nombre de lieux différents: {num_locations}

Génère un rapport structuré avec:
1. Résumé exécutif (2-3 phrases)
2. Analyse détaillée par type de déchet
3. Zones à priorité élevée (si applicable)
4. Recommandations d'action
5. Impact environnemental estimé

Ton de voix: Professionnel, factuel, orienté action.
"""
        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Générer rapport
        report = chain.run(
            date=date_str,
            total=total_detections,
            classes=str(class_counts),
            num_locations=len(locations)
        )

        return report

    def generate_alert_summary(
        self,
        alert_type: str,
        detections: List[Dict],
        location: Dict = None
    ) -> str:
        """
        Génère un résumé d'alerte enrichi par IA.

        Args:
            alert_type: Type d'alerte
            detections: Détections
            location: Localisation

        Returns:
            Résumé textuel
        """
        prompt_template = PromptTemplate(
            input_variables=["alert_type", "num_objects", "details", "location_info"],
            template="""
Génère un résumé concis (3-4 phrases) pour une alerte de déchet urbain:

Type d'alerte: {alert_type}
Nombre d'objets: {num_objects}
Détails: {details}
Localisation: {location_info}

Le résumé doit:
- Être factuel et actionnable
- Indiquer la priorité
- Suggérer une action immédiate si nécessaire
"""
        )

        # Préparer détails
        class_counts = {}
        for det in detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        location_info = "Non spécifiée"
        if location:
            location_info = f"Lat: {location.get('latitude')}, Lon: {location.get('longitude')}"

        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        summary = chain.run(
            alert_type=alert_type,
            num_objects=len(detections),
            details=str(class_counts),
            location_info=location_info
        )

        return summary

    def analyze_trends(
        self,
        historical_data: List[Dict],
        period_days: int = 7
    ) -> str:
        """
        Analyse les tendances sur une période.

        Args:
            historical_data: Données historiques
            period_days: Période en jours

        Returns:
            Analyse textuelle
        """
        if not historical_data:
            return "Données insuffisantes pour analyse."

        # Statistiques temporelles
        daily_counts = {}
        total_detections = 0

        for data in historical_data:
            date = data['detected_at'][:10]  # YYYY-MM-DD
            count = data.get('num_objects', 0)
            daily_counts[date] = daily_counts.get(date, 0) + count
            total_detections += count

        avg_daily = total_detections / max(len(daily_counts), 1)

        prompt_template = PromptTemplate(
            input_variables=["period", "total", "avg_daily", "daily_data"],
            template="""
Analyse les tendances de déchets urbains sur {period} jours:

Total de déchets détectés: {total}
Moyenne quotidienne: {avg_daily:.1f}
Données quotidiennes: {daily_data}

Fournis:
1. Tendance générale (hausse/baisse/stable)
2. Jours à forte activité
3. Patterns identifiés (jour de la semaine, etc.)
4. Recommandations pour optimiser les collectes

Analyse concise (5-6 phrases).
"""
        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        analysis = chain.run(
            period=period_days,
            total=total_detections,
            avg_daily=avg_daily,
            daily_data=str(daily_counts)
        )

        return analysis

    def suggest_collection_route(
        self,
        hotspots: List[Dict]
    ) -> str:
        """
        Suggère un itinéraire de collecte optimal.

        Args:
            hotspots: Liste de points chauds avec localisation et priorité

        Returns:
            Suggestion d'itinéraire
        """
        if not hotspots:
            return "Aucun point chaud identifié."

        # Trier par priorité
        sorted_hotspots = sorted(
            hotspots,
            key=lambda x: x.get('priority', 0),
            reverse=True
        )

        prompt_template = PromptTemplate(
            input_variables=["num_hotspots", "hotspots_data"],
            template="""
Suggère un itinéraire de collecte optimal pour {num_hotspots} points chauds:

Points chauds (priorité décroissante):
{hotspots_data}

Génère:
1. Ordre de visite recommandé
2. Justification de l'itinéraire
3. Estimation du temps nécessaire
4. Ressources recommandées (équipes, véhicules)

Réponse concise (4-5 phrases).
"""
        )

        # Formater données
        hotspots_str = ""
        for i, hs in enumerate(sorted_hotspots[:10], 1):  # Max 10
            loc = hs.get('location', {})
            priority = hs.get('priority', 'medium')
            waste_count = hs.get('waste_count', 0)
            hotspots_str += f"{i}. Priorité {priority}, {waste_count} déchets, Lat: {loc.get('latitude')}, Lon: {loc.get('longitude')}\n"

        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        suggestion = chain.run(
            num_hotspots=len(sorted_hotspots),
            hotspots_data=hotspots_str
        )

        return suggestion
