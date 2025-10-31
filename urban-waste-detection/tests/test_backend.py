"""
Tests unitaires pour le backend Flask.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le backend au path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app import app, db
from models.detection import Detection, Alert


@pytest.fixture
def client():
    """Fixture Flask test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


class TestHealthEndpoint:
    """Tests pour /api/health."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'ok'


class TestStatisticsEndpoints:
    """Tests pour les endpoints statistiques."""

    def test_overview_empty(self, client):
        """Test overview avec DB vide."""
        response = client.get('/api/statistics/overview')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_detections'] == 0
        assert data['total_objects'] == 0

    def test_daily_stats(self, client):
        """Test statistiques quotidiennes."""
        response = client.get('/api/statistics/daily')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestDetectionModel:
    """Tests pour le modèle Detection."""

    def test_create_detection(self):
        """Test création détection."""
        detection = Detection(
            image_path='/test/image.jpg',
            latitude=48.8566,
            longitude=2.3522,
            num_objects=5,
            objects_detected=[
                {'class_name': 'plastic_bottle', 'confidence': 0.9}
            ],
            confidence_avg=0.9,
            processing_time=0.5,
            source='web'
        )

        assert detection.num_objects == 5
        assert detection.source == 'web'

    def test_detection_to_dict(self):
        """Test conversion en dict."""
        detection = Detection(
            image_path='/test/image.jpg',
            num_objects=3
        )

        data = detection.to_dict()
        assert 'id' in data
        assert 'num_objects' in data
        assert data['num_objects'] == 3


class TestAlertModel:
    """Tests pour le modèle Alert."""

    def test_create_alert(self):
        """Test création alerte."""
        alert = Alert(
            detection_id=1,
            alert_type='overflowing_bin',
            severity='high',
            status='pending'
        )

        assert alert.alert_type == 'overflowing_bin'
        assert alert.severity == 'high'


# Tests pour services (nécessite mocks)
class TestDetectionService:
    """Tests pour DetectionService."""

    def test_preprocess_image(self):
        """Test prétraitement image."""
        # Nécessite mock ou image de test
        pass

    def test_postprocess_detections(self):
        """Test post-traitement."""
        pass


class TestAlertService:
    """Tests pour AlertService."""

    def test_determine_alert_type(self):
        """Test détermination type d'alerte."""
        from services.alerts import AlertService

        service = AlertService()

        # Poubelle débordante
        detections = [{'class_name': 'overflowing_bin', 'confidence': 0.9}]
        alert_type = service.determine_alert_type(detections)
        assert alert_type == 'overflowing_bin'

        # Accumulation plastique
        detections = [{'class_name': 'plastic_bottle', 'confidence': 0.9}] * 6
        alert_type = service.determine_alert_type(detections)
        assert alert_type == 'plastic_accumulation'

    def test_calculate_severity(self):
        """Test calcul sévérité."""
        from services.alerts import AlertService

        service = AlertService()

        # Haute sévérité pour poubelle débordante
        severity = service.calculate_severity('overflowing_bin', [{}] * 5)
        assert severity == 'high'

        # Critique si beaucoup d'objets
        severity = service.calculate_severity('illegal_dump', [{}] * 25)
        assert severity == 'critical'


class TestPrivacyProtection:
    """Tests pour protection vie privée."""

    def test_anonymize_location(self):
        """Test anonymisation GPS."""
        from utils.privacy import PrivacyProtection

        privacy = PrivacyProtection()

        lat, lon = privacy.anonymize_location(48.8566, 2.3522, precision=2)

        assert lat == 48.86
        assert lon == 2.35


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
