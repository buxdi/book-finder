"""
Configuration de l'application
"""
import os
from datetime import timedelta

class Config:
    """Configuration globale de l'application"""
    
    # Configuration de l'environnement
    ENV = os.getenv('FLASK_ENV', 'production')  # Production par défaut
    DEBUG = False  # Toujours False par défaut
    TESTING = False
    
    # Configuration de sécurité
    if ENV == 'development':
        SECRET_KEY = 'dev-key-for-testing'
        SSL_CONTEXT = None
        SESSION_COOKIE_SECURE = False
        ALLOWED_HOSTS = {'localhost', '127.0.0.1'}
    else:
        # En production, ces valeurs doivent être définies dans .env
        SECRET_KEY = os.getenv('SECRET_KEY')
        if not SECRET_KEY:
            raise ValueError('SECRET_KEY must be set in production')
            
        SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
        SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
        SSL_CONTEXT = (SSL_CERT_PATH, SSL_KEY_PATH) if SSL_CERT_PATH and SSL_KEY_PATH else 'adhoc'
        SESSION_COOKIE_SECURE = True
        ALLOWED_HOSTS = {'book-finder.com', 'www.book-finder.com'}

    # Configuration commune
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # En-têtes de sécurité
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
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
    if ENV == 'development':
        SSL_CERT_PATH = None
        SSL_KEY_PATH = None
    else:
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
