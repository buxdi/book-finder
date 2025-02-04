# Book Finder ![Status](https://img.shields.io/badge/status-alpha-orange)

![la page d'accueil](screenshot/screenshot.png)

## Description

Book Finder est un moteur de recherche qui utilise le scraping pour trouver des livres gratuits sur différents sites web, notamment :
- Library Genesis
- Open Library
- Gallica
- Project Gutenberg

Ajouts à venir :
- Z-Library
- Standard Ebooks
- Feedbooks
- Manybooks
- Internet Archive
- Wikisource

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/buxdi/book-finder.git
cd book-finder
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
# ou
venv\Scripts\activate  # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancer l'application :
```bash
python app/app.py
```

2. Ouvrir un navigateur et aller à `http://localhost:5000`

## Structure du projet

```
book_finder/
├── app/
│   ├── core/           # Fonctionnalités principales
│   ├── sources/        # Sources de livres
│   ├── static/         # Assets statiques
│   ├── templates/      # Templates HTML
│   └── app.py         # Point d'entrée de l'application
├── tests/             # Tests unitaires
├── requirements.txt   # Dépendances
└── README.md
```

## Avertissements
- Ce projet n'est pas encore finalisé, certaines fonctionnalités sont en phase de test.
- Ne l'utilisez pas dans un environnement de production.

## Licence
MIT
