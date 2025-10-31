"""
Configuration de la base de données.
Fichier séparé pour éviter les imports circulaires.
"""

from flask_sqlalchemy import SQLAlchemy

# Instance SQLAlchemy
db = SQLAlchemy()
