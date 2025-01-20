"""
Source Open Library
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from app.core.base_source import BookSource

class OpenLibrarySource(BookSource):
    """Source Open Library"""
    
    def __init__(self):
        super().__init__('Open Library', 'https://openlibrary.org')
        
        # Mapping des codes de langue pour OpenLibrary
        self.language_map = {
            'fr': 'fre',
            'en': 'eng',
            'es': 'spa',
            'de': 'ger',
            'it': 'ita'
        }
        
        # Mapping des noms de langues complets vers codes courts
        self.full_name_to_code = {
            'french': 'FR',
            'english': 'EN',
            'spanish': 'ES',
            'german': 'DE',
            'italian': 'IT'
        }
    
    def search(self, query: str, language: str = 'en') -> List[Dict[str, Any]]:
        results = []
        no_read_button_count = 0  # Compteur pour les livres sans bouton Read
        print(f"\nRecherche sur OpenLibrary pour: '{query}' (langue: {language})")
        
        try:
            # Conversion de la langue au format OpenLibrary
            ol_language = self.language_map.get(language, language)
            
            # Construction des paramètres de recherche pour les ebooks gratuits
            search_params = {
                'q': query,
                'mode': 'ebooks',
                'has_fulltext': 'true',
                'language': ol_language
            }
            
            search_url = f"{self.base_url}/search"
            # Construction de l'URL complète pour les logs
            params_str = '&'.join([f"{k}={v}" for k, v in search_params.items()])
            full_search_url = f"{search_url}?{params_str}"
            print(f"🔍 URL de recherche: {full_search_url}")
            
            response = requests.get(search_url, params=search_params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Erreur lors de la recherche: {response.status_code}")
                return results
            search_soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"📚 Analyse des résultats...")
            
            for link in search_soup.find_all('li', class_='searchResultItem'):
                try:
                    # Vérifie d'abord si le bouton Read est disponible dans les résultats de recherche
                    read_button = link.find('a', class_='cta-btn', string=lambda text: text and 'Read' in text)
                    if not read_button:
                        no_read_button_count += 1
                        continue  # Passe au résultat suivant si pas de bouton Read
                    
                    title = link.find('h3', class_='booktitle').get_text(strip=True)
                    book_url = "https://openlibrary.org" + link.find('a')['href']
                    print(f"\nVérification: {title}")
                    print(f"🔗 URL du livre: {book_url}")
                    
                    book_response = requests.get(book_url, timeout=30)
                    
                    if book_response.status_code != 200:
                        print(f"❌ Erreur d'accès au livre: {book_response.status_code}")
                        continue
                    book_soup = BeautifulSoup(book_response.text, 'html.parser')
                    
                    # Extraction des informations
                    author = link.find('span', class_='bookauthor').get_text(strip=True)
                    print(f"👤 Auteur trouvé: {author}")
                    
                    # Vérifie la langue dans les métadonnées
                    language_tag = book_soup.find('span', itemprop="inLanguage")
                    book_language = language_tag.get_text(strip=True) if language_tag else None
                    # Convertit le nom de langue complet en code court
                    if book_language:
                        book_language = self.full_name_to_code.get(book_language.lower(), book_language)
                    print(f"🌍 Langue trouvée: {book_language}")
                    
                    # Récupération du lien de lecture
                    read_url = "https://openlibrary.org" + read_button['href'] if read_button['href'].startswith('/') else read_button['href']
                    print(f"📖 Lien de lecture trouvé: {read_url}")
                    print(f"✨ Bouton Read disponible pour: '{title}'")
                    
                    results.append({
                        'title': title,
                        'author': author,
                        'url': book_url,
                        'source': self.name,
                        'language': book_language,
                        'is_free': True,
                        'read_url': read_url,
                        'download_url': None
                    })
                    print(f"✅ Ajouté: {title}")
                    
                except Exception as e:
                    print(f"❌ Erreur lors de l'extraction des informations: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ Erreur de recherche: {str(e)}")
            
        print(f"\n📊 Nombre de résultats trouvés: {len(results)}")
        if no_read_button_count > 0:
            print(f"ℹ️ {no_read_button_count} livres ignorés car pas de bouton Read disponible")
            
        return results