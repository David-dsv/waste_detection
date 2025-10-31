"""
Service IoT pour intégration avec capteurs de poubelles connectées.
"""

import json
from typing import Dict, List
from datetime import datetime


class BinSensor:
    """Simulateur de capteur IoT pour poubelles connectées."""

    def __init__(self, bin_id: str, mqtt_broker: str = None):
        """
        Args:
            bin_id: Identifiant unique de la poubelle
            mqtt_broker: URL du broker MQTT (optionnel)
        """
        self.bin_id = bin_id
        self.mqtt_broker = mqtt_broker

    def get_fill_level(self) -> int:
        """
        Récupère le niveau de remplissage de la poubelle.

        Returns:
            Niveau en pourcentage (0-100)
        """
        # Simuler lecture capteur ultrasonique
        # En production: lecture depuis capteur réel via MQTT/HTTP
        import random
        return random.randint(0, 100)

    def get_status(self) -> Dict:
        """
        Récupère le statut complet de la poubelle.

        Returns:
            Dictionnaire avec statut
        """
        fill_level = self.get_fill_level()

        status = {
            'bin_id': self.bin_id,
            'fill_level': fill_level,
            'status': self._determine_status(fill_level),
            'last_collection': None,  # À implémenter
            'timestamp': datetime.utcnow().isoformat(),
        }

        return status

    def _determine_status(self, fill_level: int) -> str:
        """Détermine le statut basé sur le niveau."""
        if fill_level >= 90:
            return 'critical'
        elif fill_level >= 70:
            return 'high'
        elif fill_level >= 50:
            return 'medium'
        else:
            return 'low'


class IoTManager:
    """Gestionnaire pour multiples capteurs IoT."""

    def __init__(self):
        self.sensors: Dict[str, BinSensor] = {}

    def register_sensor(self, bin_id: str) -> BinSensor:
        """Enregistre un nouveau capteur."""
        sensor = BinSensor(bin_id)
        self.sensors[bin_id] = sensor
        return sensor

    def get_all_statuses(self) -> List[Dict]:
        """Récupère les statuts de tous les capteurs."""
        return [sensor.get_status() for sensor in self.sensors.values()]

    def get_critical_bins(self) -> List[Dict]:
        """Récupère les poubelles nécessitant collecte urgente."""
        statuses = self.get_all_statuses()
        return [s for s in statuses if s['status'] in ['critical', 'high']]


# Exemple d'intégration MQTT (nécessite paho-mqtt)
"""
import paho.mqtt.client as mqtt

class MQTTBinSensor(BinSensor):
    def __init__(self, bin_id: str, mqtt_broker: str):
        super().__init__(bin_id, mqtt_broker)
        self.client = mqtt.Client()
        self.client.connect(mqtt_broker, 1883, 60)
        self.latest_data = {}

        # Subscribe au topic
        topic = f"bins/{bin_id}/status"
        self.client.subscribe(topic)
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        self.latest_data = json.loads(msg.payload)

    def get_fill_level(self) -> int:
        return self.latest_data.get('fill_level', 0)
"""
