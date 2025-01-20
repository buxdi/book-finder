#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application web Book Finder
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
import bleach
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import urllib.parse

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

# Configuration du logging
if app.config['ENV'] == 'production':
    # S'assurer que le répertoire de logs existe
    os.makedirs('/var/log/book-finder', exist_ok=True)
    
    # Configurer le logging de l'application
    file_handler = RotatingFileHandler('/var/log/book-finder/app.log', 
                                     maxBytes=1024 * 1024,  # 1MB
                                     backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Book Finder startup')

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
    if request.is_secure or app.config['ENV'] == 'development':
        return

    # Liste des chemins autorisés pour la redirection
    ALLOWED_PATHS = {'/', '/search', '/about', '/contact'}
    
    # Rediriger vers HTTPS en production de manière sécurisée
    if app.config['ENV'] == 'production':
        if request.host not in app.config['ALLOWED_HOSTS']:
            app.logger.warning(f'Tentative d\'accès avec hôte non autorisé: {request.host}')
            return jsonify({"error": "Hôte non autorisé"}), 403
            
        # Valider le chemin
        if request.path not in ALLOWED_PATHS:
            app.logger.warning(f'Tentative d\'accès à un chemin non autorisé: {request.path}')
            return redirect('/', code=302)
            
        app.logger.info(f'Redirection HTTPS pour {request.host}')
        
        # Construction sécurisée de l'URL HTTPS
        secure_url = 'https://{}{}'.format(
            request.host,
            request.path
        )
        
        # Validation et nettoyage des paramètres de requête
        if request.query_string:
            # Ne permettre que les paramètres autorisés
            allowed_params = {'q', 'lang', 'page', 'sort'}
            query_params = request.args.copy()
            cleaned_params = {
                k: bleach.clean(v) 
                for k, v in query_params.items() 
                if k in allowed_params
            }
            
            if cleaned_params:
                secure_url += '?' + urllib.parse.urlencode(cleaned_params)
        
        return redirect(secure_url, code=301)

@app.after_request
def add_security_headers(response):
    """Ajouter des en-têtes de sécurité supplémentaires"""
    for key, value in app.config['SECURITY_HEADERS'].items():
        response.headers[key] = value
    return response

@app.route('/')
@limiter.limit("60 per minute")
def index():
    """Page d'accueil"""
    app.logger.info(f'Accès à la page d\'accueil depuis {request.remote_addr}')
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
    query = bleach.clean(request.args.get('q', ''))
    # Ne pas logger la requête complète, uniquement sa longueur pour la sécurité
    app.logger.info(f'Recherche depuis {request.remote_addr} - longueur: {len(query)}')
    lang = bleach.clean(request.args.get('lang', ''))
    
    if not query or lang not in Config.SUPPORTED_LANGUAGES:
        return jsonify([])
    
    try:
        results = await search_engine.search_async(query, lang)
        app.logger.info(f'Résultats trouvés: {len(results)}')
        # Nettoyer les résultats avant de les renvoyer
        clean_results = []
        for result in results:
            clean_results.append({
                'title': bleach.clean(result.get('title', '')),
                'author': bleach.clean(result.get('author', '')),
                'url': bleach.clean(result.get('url', '')),
                'source': bleach.clean(result.get('source', '')),
                'language': bleach.clean(result.get('language', ''))
            })
        return jsonify(clean_results)
    except Exception as e:
        # Ne pas logger l'exception complète qui pourrait contenir des données sensibles
        app.logger.error(f'Erreur pendant la recherche depuis {request.remote_addr}: {type(e).__name__}')
        return jsonify({"error": "Une erreur est survenue"}), 500

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
    app.logger.warning(f'Rate limit dépassé pour {request.remote_addr}')
    return jsonify(error="Trop de requêtes. Veuillez réessayer plus tard."), 429

if __name__ == '__main__':
    # Configuration selon l'environnement
    port = int(os.getenv('PORT', 5002))
    if app.config['ENV'] == 'development':
        app.run(host='127.0.0.1', port=port)
    else:
        # En production, utiliser le SSL et les paramètres de sécurité
        ssl_context = app.config.get('SSL_CONTEXT', None)
        app.run(host='127.0.0.1', 
               port=port,
               ssl_context=ssl_context,
               debug=False)  # Forcer debug=False en production
