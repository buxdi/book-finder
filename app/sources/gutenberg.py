"""
Source Project Gutenberg
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from app.core.base_source import BookSource

class GutenbergSource(BookSource):
    """Source Project Gutenberg"""
    
    def __init__(self):
        super().__init__('Project Gutenberg', 'https://www.gutenberg.org')
    
    def search(self, query: str, language: str = 'fr') -> List[Dict[str, Any]]:
        results = []
        
        try:
            search_url = f"{self.base_url}/ebooks/search/"
            response = requests.get(search_url, params={'query': query}, timeout=10)
            search_soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in search_soup.find_all('li', class_='booklink'):
                try:
                    book_url = "https://www.gutenberg.org" + link.find('a')['href']
                    print(f"\nVérification: {book_url}")
                    book_response = requests.get(book_url, timeout=10)
                    book_soup = BeautifulSoup(book_response.text, 'html.parser')
                    
                    # Vérifie la section 'bibrec' pour extraire les informations
                    bibrec_table = book_soup.find('table', class_='bibrec')
                    if bibrec_table:
                        # Extraction des informations
                        title = bibrec_table.find('td', itemprop='headline')
                        title = title.get_text(strip=True) if title else "Titre inconnu"
                        print(f"Titre trouvé: {title}")
                        
                        author_tag = bibrec_table.find('a', itemprop='creator')
                        author = author_tag.get_text(strip=True) if author_tag else "Auteur inconnu"
                        print(f"Auteur trouvé: {author}")
                        
                        # Extraction de la langue à partir de la balise <tr property="dcterms:language">
                        language_tag = bibrec_table.find('tr', property='dcterms:language')
                        if language_tag and language_tag.has_attr('content'):
                            language_content = language_tag['content']
                            print(f"Langue trouvée: {language_content}")
                        else:
                            language_content = "Langue inconnue"
                            print("❌ Langue non trouvée")
                        
                        # Vérifie si la langue correspond à celle choisie
                        if language_content != language:
                            print(f"❌ Mauvaise langue - ignoré (trouvé: {language_content})")
                            continue
                        
                        results.append({
                            'title': title,
                            'author': author,
                            'url': book_url,
                            'source': self.name,
                            'language': language_content,
                            'is_free': True,
                            'read_url': book_url,
                            'download_url': None
                        })
                        print(f"✅ Ajouté: {title}")
                    else:
                        print("❌ Table bibrec non trouvée")
                    
                except Exception as e:
                    print(f"Erreur lors de l'extraction des informations: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Erreur de recherche: {str(e)}")
            
        print(f"Nombre de résultats trouvés: {len(results)}")
        return results
