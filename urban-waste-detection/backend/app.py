"""
Urban Waste Detection - Backend API
====================================

API Flask pour inférence RF-DETR et gestion des alertes.

Auteur: Votre Nom
Date: 2025
"""

import os
import cv2
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Charger variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///waste_detection.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB

# CORS - Autoriser toutes les origines pour le streaming
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/api/*": {"origins": cors_origins},
    r"/uploads/*": {"origins": "*"}
})

# Database
from database import db
db.init_app(app)
migrate = Migrate(app, db)

# Sentry (optionnel)
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

# Importer routes
from routes import detection, alerts, statistics

# Enregistrer blueprints
app.register_blueprint(detection.bp, url_prefix='/api')
app.register_blueprint(alerts.bp, url_prefix='/api')
app.register_blueprint(statistics.bp, url_prefix='/api')


@app.route('/')
def index():
    """Page d'accueil API."""
    return jsonify({
        'name': 'Urban Waste Detection API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'detection': '/api/detect',
            'video_detection': '/api/detect/video',
            'alerts': '/api/alerts',
            'statistics': '/api/statistics',
            'health': '/api/health'
        },
        'documentation': '/api/docs'
    })


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Servir les fichiers uploadés (images originales et annotées)."""
    upload_dir = Path('uploads')
    return send_from_directory(upload_dir, filename)


# ============= STREAMING VIDEO EN TEMPS RÉEL =============

def generate_frames():
    """Génère les frames annotées en temps réel depuis la webcam."""
    from services.yolo_detection import get_yolo_service

    # Charger le service YOLO
    yolo_service = get_yolo_service()

    # Ouvrir la webcam
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)

    if not camera.isOpened():
        print("❌ Impossible d'ouvrir la webcam")
        return

    print("📹 Streaming webcam démarré...")

    # Couleurs par catégorie (BGR)
    colors = {
        'plastic': (0, 0, 255),      # Rouge
        'glass': (0, 255, 255),      # Jaune
        'metal': (192, 192, 192),    # Gris
        'paper': (255, 144, 30),     # Orange
        'organic': (0, 255, 0),      # Vert
        'other': (255, 255, 0)       # Cyan
    }

    frame_count = 0
    last_detections = []

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break

            # Détecter tous les 3 frames pour la performance
            frame_count += 1
            if frame_count % 3 == 0:
                # Convertir BGR -> RGB pour YOLO
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                last_detections = yolo_service.detect_from_array(frame_rgb)

            # Dessiner les détections sur le frame
            for det in last_detections:
                x1, y1, x2, y2 = det['bbox']
                category = det['category']
                color = colors.get(category, (255, 255, 0))

                # Rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                # Label
                label = f"{det['class']} {det['confidence']:.0%}"
                font_scale = 0.7
                thickness = 2
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

                # Fond du label
                cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), color, -1)
                cv2.putText(frame, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

            # Afficher le compteur de détections
            count_text = f"Dechets: {len(last_detections)}"
            cv2.putText(frame, count_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Encoder en JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    finally:
        camera.release()
        print("📹 Streaming webcam arrêté")


@app.route('/api/stream')
def video_stream():
    """Endpoint de streaming vidéo avec détection temps réel."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/health')
def health():
    """Health check endpoint."""
    try:
        # Vérifier connexion DB
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    return jsonify({
        'status': 'ok',
        'database': db_status,
        'model_loaded': hasattr(app, 'model'),
        'gemini_enabled': os.getenv('USE_GEMINI', 'false').lower() == 'true'
    })


@app.errorhandler(404)
def not_found(error):
    """Gestion erreur 404."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Gestion erreur 500."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Créer tables DB
    with app.app_context():
        db.create_all()

    # Charger modèle YOLO11 (nano - le plus rapide)
    try:
        from services.yolo_detection import get_yolo_service
        yolo_service = get_yolo_service()  # Utilise YOLO11n par défaut
        app.yolo_service = yolo_service
        print("✅ Modèle YOLO11 chargé avec succès (détection active)")
    except Exception as e:
        print(f"⚠️  YOLO11 non disponible: {e}")
        print("ℹ️  Le backend fonctionne en mode API-only (sans détection)")
        app.yolo_service = None

    # Lancer serveur
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"\n🚀 Urban Waste Detection API démarrée")
    print(f"📍 http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🧠 Gemini AI: {'activé' if os.getenv('USE_GEMINI') == 'true' else 'désactivé'}\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
