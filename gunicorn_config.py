"""Configuration Gunicorn pour la production"""
import multiprocessing
import os

# Paramètres du serveur
bind = "127.0.0.1:5002"  # Bind sur localhost uniquement
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120

# Sécurité
umask = 0o027  # Permissions restrictives pour les nouveaux fichiers
user = 'bookfinder'
group = 'bookfinder'

# Logging
if not os.path.exists('/var/log/book-finder'):
    os.makedirs('/var/log/book-finder', mode=0o755)

accesslog = "/var/log/book-finder/access.log"
errorlog = "/var/log/book-finder/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# SSL (si utilisé)
# keyfile = "/chemin/vers/votre/clé.pem"
# certfile = "/chemin/vers/votre/certificat.pem"

# Protection supplémentaire
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Utiliser /dev/shm pour les fichiers temporaires (plus sécurisé)
worker_tmp_dir = "/dev/shm"
