"""
Routes API pour statistiques.
"""

import json
from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
from models.detection import Detection, Alert
from database import db

bp = Blueprint('statistics', __name__)


@bp.route('/statistics/overview', methods=['GET'])
def get_overview():
    """Statistiques générales."""
    total_detections = Detection.query.count()
    total_objects = db.session.query(func.sum(Detection.num_objects)).scalar() or 0
    total_alerts = Alert.query.count()
    avg_confidence = db.session.query(func.avg(Detection.confidence_avg)).scalar() or 0

    return jsonify({
        'total_detections': total_detections,
        'total_objects': int(total_objects),
        'total_alerts': total_alerts,
        'avg_confidence': float(avg_confidence)
    }), 200


@bp.route('/statistics/daily', methods=['GET'])
def get_daily_stats():
    """Statistiques quotidiennes (7 derniers jours)."""
    stats = []
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = Detection.query.filter(
            func.date(Detection.detected_at) == date
        ).count()
        stats.append({'date': str(date), 'count': count})

    return jsonify(stats), 200


@bp.route('/statistics/by-class', methods=['GET'])
def get_class_distribution():
    """Distribution par classe de déchets."""
    detections = Detection.query.all()

    class_counts = {}
    for det in detections:
        if det.objects_detected:
            # Parser si c'est une string JSON
            objects = det.objects_detected
            if isinstance(objects, str):
                try:
                    objects = json.loads(objects)
                except (json.JSONDecodeError, TypeError):
                    objects = []

            # Compter les objets
            if isinstance(objects, list):
                for obj in objects:
                    if isinstance(obj, dict):
                        # Essayer différents noms de champs
                        class_name = obj.get('class') or obj.get('class_name') or 'unknown'
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    return jsonify(class_counts), 200
