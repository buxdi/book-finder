"""
Configuration de l'application
"""
import os
from datetime import timedelta

class Config:
    """Configuration globale de l'application"""
    
    # Configuration de l'application
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Configuration de sécurité
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # En-têtes de sécurité
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Configuration des langues
    DEFAULT_LANGUAGE = 'fr'
    SUPPORTED_LANGUAGES = {
        'fr': 'Français',
        'en': 'English'
    }
    
    # Configuration des sources
    SOURCES = [
        'gallica',
        'libgen',
        'gutenberg',
        'openlibrary'
    ]
    
    # Limites de taux par défaut
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Configuration SSL/TLS
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
    
    # Validation des entrées
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB max
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuration de la recherche
    MAX_SEARCH_RESULTS = 10  # Nombre maximum de résultats par source
    SEARCH_TIMEOUT = 10  # Timeout en secondes pour les requêtes
    
    # Configuration des traductions
    TRANSLATIONS = {
        'fr': {
            'search': 'Rechercher',
            'title': 'Titre',
            'author': 'Auteur',
            'language': 'Langue',
            'source': 'Source',
            'results': 'résultats',
            'no_results': 'Aucun résultat',
            'error': 'Erreur',
            'loading': 'Chargement...',
            'search_placeholder': 'Rechercher un livre...',
        },
        'en': {
            'search': 'Search',
            'title': 'Title',
            'author': 'Author',
            'language': 'Language',
            'source': 'Source',
            'results': 'results',
            'no_results': 'No results',
            'error': 'Error',
            'loading': 'Loading...',
            'search_placeholder': 'Search for a book...',
        }
    }
    
    @classmethod
    def get_translation(cls, lang: str, key: str) -> str:
        """Retourne la traduction d'une clé dans la langue spécifiée"""
        return cls.TRANSLATIONS.get(lang, cls.TRANSLATIONS['en']).get(key, key)

    @staticmethod
    def init_app(app):
        """Initialisation de l'application avec les paramètres de sécurité"""
        # Ajouter les en-têtes de sécurité par défaut
        @app.after_request
        def add_security_headers(response):
            for header, value in Config.SECURITY_HEADERS.items():
                response.headers[header] = value
            return response
