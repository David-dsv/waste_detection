"""
Routes API pour gestion des alertes.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from models.detection import Alert
from database import db

bp = Blueprint('alerts', __name__)


@bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Récupère les alertes."""
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status')  # pending, sent, resolved

    query = Alert.query
    if status:
        query = query.filter_by(status=status)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

    return jsonify({
        'alerts': [a.to_dict() for a in alerts],
        'total': query.count()
    }), 200


@bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Marque une alerte comme résolue."""
    alert = Alert.query.get_or_404(alert_id)
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'alert': alert.to_dict()}), 200
