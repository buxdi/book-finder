#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application web Book Finder
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
import bleach
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajoute le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Config
from app.core.search_engine import SearchEngine

app = Flask(__name__)
app.config.from_object(Config)

# Configurer la clé secrète depuis l'environnement
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialiser les extensions de sécurité
talisman = Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net'],
        'style-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.googleapis.com'],
        'font-src': ["'self'", 'cdnjs.cloudflare.com', 'fonts.googleapis.com', 'fonts.gstatic.com'],
        'img-src': ["'self'", 'data:', '*'],
    },
    feature_policy={
        'geolocation': "'none'",
        'midi': "'none'",
        'notifications': "'none'",
        'push': "'none'",
        'sync-xhr': "'none'",
        'microphone': "'none'",
        'camera': "'none'",
        'magnetometer': "'none'",
        'gyroscope': "'none'",
        'speaker': "'none'",
        'vibrate': "'none'",
        'fullscreen': "'none'",
        'payment': "'none'",
    },
    referrer_policy='same-origin'
)

# Protection CSRF avec configuration renforcée
csrf = SeaSurf(app)
app.config['CSRF_COOKIE_SECURE'] = True
app.config['CSRF_COOKIE_HTTPONLY'] = True

# Limiteur de taux avec configuration plus stricte
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialise le moteur de recherche
search_engine = SearchEngine()

@app.before_request
def before_request():
    """Vérifications avant chaque requête"""
    # Forcer HTTPS en production
    if not request.is_secure and not app.debug:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url), 301

@app.after_request
def add_security_headers(response):
    """Ajouter des en-têtes de sécurité supplémentaires"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/')
@limiter.limit("60 per minute")
def index():
    """Page d'accueil"""
    lang = bleach.clean(request.args.get('lang', 'fr'))
    if lang not in Config.SUPPORTED_LANGUAGES:
        lang = Config.DEFAULT_LANGUAGE
        
    translations = {
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
    }
    
    return render_template('index.html',
                         translations=translations,
                         languages=Config.SUPPORTED_LANGUAGES,
                         lang=lang,
                         config=Config)

@app.route('/search')
@limiter.limit("30 per minute")
async def search():
    """Endpoint de recherche"""
    # Nettoyer et valider les entrées
    query = bleach.clean(request.args.get('q', ''))
    lang = bleach.clean(request.args.get('lang', ''))
    
    if not query or lang not in Config.SUPPORTED_LANGUAGES:
        return jsonify([])
    
    try:
        results = await search_engine.search_async(query, lang)
        # Nettoyer les résultats avant de les renvoyer
        clean_results = []
        for result in results:
            clean_results.append({
                'title': bleach.clean(result.get('title', '')),
                'author': bleach.clean(result.get('author', '')),
                'url': bleach.clean(result.get('url', '')),
                'source': bleach.clean(result.get('source', '')),
                'series_name': bleach.clean(result.get('series_name', '')),
                'series_volume': bleach.clean(str(result.get('series_volume', '')))
            })
        return jsonify(clean_results)
    except Exception as e:
        app.logger.error(f"Erreur lors de la recherche: {str(e)}")
        return jsonify({'error': 'Une erreur est survenue'}), 500

@app.route('/favicon.ico')
def favicon():
    """Endpoint pour le favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.errorhandler(429)
def ratelimit_handler(e):
    """Gestionnaire pour les limites de taux dépassées"""
    return jsonify(error="Trop de requêtes. Veuillez réessayer plus tard."), 429

if __name__ == '__main__':
    # En production, utiliser un serveur WSGI comme gunicorn
    if app.debug:
        app.run(debug=True, host='0.0.0.0', port=5002)
    else:
        app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')
