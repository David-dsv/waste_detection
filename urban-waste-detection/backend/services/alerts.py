"""
Service de gestion des alertes (email, SMS, webhooks).
"""

import os
from datetime import datetime
from typing import List, Dict
from flask_mail import Mail, Message
from twilio.rest import Client as TwilioClient


class AlertService:
    """Service pour envoyer des alertes aux autorités."""

    # Règles de sévérité
    SEVERITY_RULES = {
        'overflowing_bin': 'high',
        'illegal_dump': 'critical',
        'plastic_accumulation': 'medium',
        'single_item': 'low'
    }

    def __init__(self, mail: Mail = None):
        """
        Args:
            mail: Instance Flask-Mail
        """
        self.mail = mail

        # Twilio (SMS)
        self.twilio_client = None
        if os.getenv('TWILIO_ACCOUNT_SID'):
            self.twilio_client = TwilioClient(
                os.getenv('TWILIO_ACCOUNT_SID'),
                os.getenv('TWILIO_AUTH_TOKEN')
            )
            self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')

    def determine_alert_type(self, detections: List[Dict]) -> str:
        """
        Détermine le type d'alerte basé sur les détections.

        Args:
            detections: Liste de détections

        Returns:
            Type d'alerte
        """
        if not detections:
            return None

        # Vérifier poubelle débordante
        for det in detections:
            if det['class_name'] == 'overflowing_bin':
                return 'overflowing_bin'

        # Vérifier accumulation importante
        if len(detections) > 10:
            return 'illegal_dump'

        # Vérifier accumulation plastique
        plastic_count = sum(
            1 for d in detections
            if 'plastic' in d['class_name']
        )
        if plastic_count > 5:
            return 'plastic_accumulation'

        # Par défaut
        if len(detections) > 0:
            return 'single_item'

        return None

    def calculate_severity(self, alert_type: str, detections: List[Dict]) -> str:
        """
        Calcule la sévérité de l'alerte.

        Args:
            alert_type: Type d'alerte
            detections: Détections

        Returns:
            Niveau de sévérité: 'low', 'medium', 'high', 'critical'
        """
        base_severity = self.SEVERITY_RULES.get(alert_type, 'low')

        # Augmenter sévérité si beaucoup d'objets
        if len(detections) > 20:
            if base_severity == 'high':
                return 'critical'
            elif base_severity == 'medium':
                return 'high'

        return base_severity

    def create_alert_message(
        self,
        alert_type: str,
        severity: str,
        detections: List[Dict],
        location: Dict = None
    ) -> str:
        """
        Crée le message d'alerte.

        Args:
            alert_type: Type d'alerte
            severity: Sévérité
            detections: Détections
            location: {'latitude': float, 'longitude': float}

        Returns:
            Message formaté
        """
        # Header
        message = f"⚠️ ALERTE DÉCHET URBAIN - {severity.upper()}\n\n"

        # Type d'alerte
        alert_descriptions = {
            'overflowing_bin': "Poubelle débordante détectée",
            'illegal_dump': "Dépôt sauvage de déchets détecté",
            'plastic_accumulation': "Accumulation importante de plastique",
            'single_item': "Déchet détecté"
        }
        message += f"Type: {alert_descriptions.get(alert_type, alert_type)}\n\n"

        # Détails détections
        message += f"Nombre d'objets détectés: {len(detections)}\n\n"

        # Distribution par classe
        class_counts = {}
        for det in detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        message += "Répartition:\n"
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            message += f"  - {class_name}: {count}\n"

        # Localisation
        if location and location.get('latitude'):
            message += f"\nLocalisation:\n"
            message += f"  Latitude: {location['latitude']}\n"
            message += f"  Longitude: {location['longitude']}\n"
            message += f"  Google Maps: https://maps.google.com/?q={location['latitude']},{location['longitude']}\n"

        # Timestamp
        message += f"\nDétecté le: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"

        # Footer
        message += "\n---\n"
        message += "Urban Waste Detection System\n"
        message += "Ne pas répondre à ce message automatique."

        return message

    def send_email_alert(
        self,
        recipients: List[str],
        subject: str,
        message: str
    ) -> bool:
        """
        Envoie une alerte par email.

        Args:
            recipients: Liste d'emails
            subject: Sujet
            message: Corps du message

        Returns:
            Succès (True/False)
        """
        if not self.mail:
            print("⚠️ Flask-Mail non configuré")
            return False

        try:
            msg = Message(
                subject=subject,
                recipients=recipients,
                body=message
            )
            self.mail.send(msg)
            print(f"✅ Email envoyé à {len(recipients)} destinataires")
            return True

        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")
            return False

    def send_sms_alert(
        self,
        phone_numbers: List[str],
        message: str
    ) -> bool:
        """
        Envoie une alerte par SMS (Twilio).

        Args:
            phone_numbers: Liste de numéros
            message: Message (max 160 caractères)

        Returns:
            Succès
        """
        if not self.twilio_client:
            print("⚠️ Twilio non configuré")
            return False

        # Tronquer message si trop long
        if len(message) > 160:
            message = message[:157] + "..."

        try:
            for phone in phone_numbers:
                self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=phone
                )
            print(f"✅ SMS envoyé à {len(phone_numbers)} numéros")
            return True

        except Exception as e:
            print(f"❌ Erreur envoi SMS: {e}")
            return False

    def send_webhook(
        self,
        webhook_url: str,
        payload: Dict
    ) -> bool:
        """
        Envoie une alerte via webhook.

        Args:
            webhook_url: URL du webhook
            payload: Données JSON

        Returns:
            Succès
        """
        import requests

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✅ Webhook envoyé: {webhook_url}")
            return True

        except Exception as e:
            print(f"❌ Erreur webhook: {e}")
            return False

    def trigger_alert(
        self,
        detections: List[Dict],
        location: Dict = None,
        recipients_email: List[str] = None,
        recipients_sms: List[str] = None,
        webhook_url: str = None
    ) -> Dict:
        """
        Déclenche une alerte complète.

        Args:
            detections: Détections
            location: Localisation GPS
            recipients_email: Emails destinataires
            recipients_sms: Numéros SMS
            webhook_url: URL webhook

        Returns:
            Résultat avec statuts
        """
        # Déterminer type et sévérité
        alert_type = self.determine_alert_type(detections)
        if not alert_type:
            return {'triggered': False, 'reason': 'No alert needed'}

        severity = self.calculate_severity(alert_type, detections)

        # Créer message
        message = self.create_alert_message(
            alert_type,
            severity,
            detections,
            location
        )

        result = {
            'triggered': True,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'email_sent': False,
            'sms_sent': False,
            'webhook_sent': False
        }

        # Envoyer email
        if recipients_email:
            subject = f"[{severity.upper()}] Alerte Déchet Urbain - {alert_type}"
            result['email_sent'] = self.send_email_alert(
                recipients_email,
                subject,
                message
            )

        # Envoyer SMS
        if recipients_sms:
            sms_message = f"[{severity.upper()}] {alert_type}: {len(detections)} objets détectés"
            if location:
                sms_message += f" à ({location['latitude']}, {location['longitude']})"
            result['sms_sent'] = self.send_sms_alert(recipients_sms, sms_message)

        # Webhook
        if webhook_url:
            payload = {
                'alert_type': alert_type,
                'severity': severity,
                'detections': detections,
                'location': location,
                'timestamp': datetime.utcnow().isoformat()
            }
            result['webhook_sent'] = self.send_webhook(webhook_url, payload)

        return result
