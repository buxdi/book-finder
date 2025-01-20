# Book Finder

Un moteur de recherche pour trouver des livres gratuits à travers différentes sources en ligne.

![la page d'accueil](screenshot/screenshot.png)

## Description

Book Finder est une application web qui permet de rechercher des livres gratuits sur différentes plateformes en ligne, notamment :

- Library Genesis
- Open Library
- Gallica
- Project Gutenberg

Futurs ajouts :

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

## Licence

MIT
