"""
Routes API pour détection de déchets.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import cv2
import numpy as np

from services.yolo_detection import get_yolo_service
from services.alerts import AlertService
from services.gemini_analyzer import GeminiWasteAnalyzer
from models.detection import Detection, Alert
from database import db

bp = Blueprint('detection', __name__)

# Services (singletons)
yolo_service = None
gemini_analyzer = None

# Extensions autorisées
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'}


def allowed_file(filename):
    """Vérifie si l'extension est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_yolo_detection_service():
    """Récupère le service YOLO (lazy loading)."""
    global yolo_service
    if yolo_service is None:
        yolo_service = get_yolo_service()  # Utilise le modèle TACO par défaut
    return yolo_service


def get_gemini_analyzer():
    """Récupère l'analyseur Gemini (lazy loading)."""
    global gemini_analyzer
    if gemini_analyzer is None and os.getenv('USE_GEMINI', 'false').lower() == 'true':
        try:
            gemini_analyzer = GeminiWasteAnalyzer()
            print("✅ Gemini Analyzer initialisé")
        except Exception as e:
            print(f"⚠️ Gemini non disponible: {e}")
            gemini_analyzer = None
    return gemini_analyzer


@bp.route('/detect', methods=['POST'])
def detect_waste():
    """
    Détecte les déchets dans une image uploadée.

    Request:
        - image: fichier image (multipart/form-data)
        - gps_lat: latitude (optionnel)
        - gps_lon: longitude (optionnel)
        - source: 'web', 'mobile', 'iot' (optionnel)
        - send_alert: true/false (optionnel)

    Response:
        {
            "success": true,
            "detection_id": 123,
            "detections": [...],
            "num_objects": 5,
            "processing_time": 0.234,
            "alert_sent": true,
            "image_url": "/uploads/..."
        }
    """
    # Vérifier fichier
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    try:
        # Sauvegarder fichier
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"

        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        filepath = upload_dir / filename
        file.save(str(filepath))

        # 🤖 DÉTECTION YOLO
        yolo = get_yolo_detection_service()
        detections = yolo.detect(str(filepath))
        processing_time = 0.0  # YOLO gère cela en interne

        # Sauvegarder image annotée
        annotated_filename = f"annotated_{filename}"
        annotated_path = upload_dir / annotated_filename
        yolo.annotate_image(str(filepath), detections, str(annotated_path))

        # Récupérer paramètres
        gps_lat = request.form.get('gps_lat', type=float)
        gps_lon = request.form.get('gps_lon', type=float)
        source = request.form.get('source', 'web')
        send_alert = request.form.get('send_alert', 'false').lower() == 'true'

        # Calculer confiance moyenne
        avg_confidence = np.mean([d['confidence'] for d in detections]) if detections else 0.0

        # 🧠 ANALYSE GEMINI - Analyse intelligente des détections
        gemini_analysis = None
        if len(detections) > 0:
            analyzer = get_gemini_analyzer()
            if analyzer:
                try:
                    location = None
                    if gps_lat and gps_lon:
                        location = {'latitude': gps_lat, 'longitude': gps_lon}

                    gemini_analysis = analyzer.analyze_detections(
                        detections=detections,
                        location=location,
                        image_context=request.form.get('context', '')
                    )
                    print(f"✅ Analyse Gemini générée: {gemini_analysis.get('severity')}")
                except Exception as e:
                    print(f"⚠️ Erreur analyse Gemini: {e}")

        # Sauvegarder en DB
        detection_record = Detection(
            image_path=str(filepath),
            latitude=gps_lat,
            longitude=gps_lon,
            num_objects=len(detections),
            objects_detected=json.dumps(detections),  # Convertir en JSON string
            confidence_avg=float(avg_confidence),
            processing_time=processing_time,
            source=source
        )
        db.session.add(detection_record)
        db.session.commit()

        response = {
            'success': True,
            'detection_id': detection_record.id,
            'detections': detections,
            'num_objects': len(detections),
            'processing_time': processing_time,
            'confidence_avg': float(avg_confidence),
            'filename': filename,
            'annotated_image': annotated_filename,
            'image_url': f"/uploads/{filename}",
            'annotated_url': f"/uploads/{annotated_filename}",
            'alert_sent': False,
            'ai_analysis': gemini_analysis  # 🆕 Analyse IA ajoutée
        }

        # Envoyer alerte si demandé
        if send_alert and len(detections) > 0:
            alert_service = AlertService()

            location = None
            if gps_lat and gps_lon:
                location = {'latitude': gps_lat, 'longitude': gps_lon}

            # Destinataires (à configurer)
            recipients_email = os.getenv('ALERT_EMAILS', '').split(',')
            if recipients_email and recipients_email[0]:
                alert_result = alert_service.trigger_alert(
                    detections=detections,
                    location=location,
                    recipients_email=recipients_email
                )

                # Sauvegarder alerte en DB
                if alert_result['triggered']:
                    alert_record = Alert(
                        detection_id=detection_record.id,
                        alert_type=alert_result['alert_type'],
                        severity=alert_result['severity'],
                        status='sent' if alert_result['email_sent'] else 'failed',
                        sent_at=datetime.utcnow() if alert_result['email_sent'] else None,
                        recipients=recipients_email,
                        message=alert_result['message']
                    )
                    db.session.add(alert_record)
                    db.session.commit()

                    response['alert_sent'] = True
                    response['alert_type'] = alert_result['alert_type']
                    response['severity'] = alert_result['severity']

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/detect/video', methods=['POST'])
def detect_video():
    """
    Détecte les déchets dans une vidéo.

    Request:
        - video: fichier vidéo (multipart/form-data)

    Response:
        {
            "success": true,
            "stats": {...},
            "output_video_url": "/uploads/..."
        }
    """
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Sauvegarder vidéo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"

        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        filepath = upload_dir / filename
        file.save(str(filepath))

        # Traiter vidéo
        service = get_detection_service()

        output_filename = f"annotated_{filename}"
        output_path = upload_dir / output_filename

        stats = service.detect_video(str(filepath), str(output_path))

        return jsonify({
            'success': True,
            'stats': stats,
            'output_video_url': f"/uploads/{output_filename}"
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/detections', methods=['GET'])
def get_detections():
    """
    Récupère la liste des détections.

    Query params:
        - limit: nombre max de résultats (défaut: 50)
        - offset: offset pour pagination (défaut: 0)
        - start_date: date début (format: YYYY-MM-DD)
        - end_date: date fin
        - source: filtrer par source (web, mobile, iot)

    Response:
        {
            "detections": [...],
            "total": 123,
            "limit": 50,
            "offset": 0
        }
    """
    try:
        # Paramètres
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        source = request.args.get('source')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Requête
        query = Detection.query

        if source:
            query = query.filter_by(source=source)

        if start_date:
            query = query.filter(Detection.detected_at >= start_date)

        if end_date:
            query = query.filter(Detection.detected_at <= end_date)

        # Total
        total = query.count()

        # Récupérer avec pagination
        detections = query.order_by(
            Detection.detected_at.desc()
        ).limit(limit).offset(offset).all()

        return jsonify({
            'detections': [d.to_dict() for d in detections],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/detections/<int:detection_id>', methods=['GET'])
def get_detection(detection_id):
    """Récupère une détection spécifique."""
    try:
        detection = Detection.query.get_or_404(detection_id)
        return jsonify(detection.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/detections/<int:detection_id>', methods=['DELETE'])
def delete_detection(detection_id):
    """Supprime une détection."""
    try:
        detection = Detection.query.get_or_404(detection_id)

        # Supprimer fichiers
        if Path(detection.image_path).exists():
            Path(detection.image_path).unlink()

        # Supprimer de DB
        db.session.delete(detection)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Detection deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
