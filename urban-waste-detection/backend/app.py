"""
Urban Waste Detection - Backend API
====================================

API Flask pour inférence RF-DETR et gestion des alertes.

Auteur: Votre Nom
Date: 2025
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
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

# CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

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
