"""
Source Library Genesis
"""

import os
import sys
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import html5lib

# Ajoute le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.base_source import BookSource

class LibgenSource(BookSource):
    """Source Library Genesis"""
    
    def __init__(self):
        super().__init__('Library Genesis', 'https://libgen.is')
        
        # Mapping des codes de langue LibGen
        self.language_map = {
            'fr': 'french',
            'en': 'english',
            'es': 'spanish',
            'de': 'german',
            'it': 'italian'
        }
    
    def search(self, query: str, language: str = 'fr') -> List[Dict[str, Any]]:
        """
        Recherche des livres sur Library Genesis
        
        Args:
            query: Terme de recherche
            language: Code de langue (fr, en, etc.)
            
        Returns:
            Liste des résultats de recherche
        """
        results = []
        try:
            # Convertit le code de langue au format LibGen
            libgen_language = self.language_map.get(language, 'french')
            
            # Construit l'URL de recherche avec le filtre de langue
            search_url = f"{self.base_url}/search.php"
            params = {
                'req': query,
                'lg_topic': 'libgen',
                'open': '0',
                'view': 'simple',
                'phrase': '1',
                'column': 'def',
                'res': '25',
                'language': libgen_language
            }
            
            print(f"\nRecherche sur LibGen: {search_url}")
            print(f"Paramètres: {params}")
            
            # Effectue la requête avec les paramètres
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(search_url, params=params, headers=headers, verify=False, timeout=10)
            response.raise_for_status()
            
            print(f"Code de statut: {response.status_code}")
            print(f"URL finale: {response.url}")
            
            # Parse le HTML avec html5lib pour une meilleure tolérance aux erreurs
            soup = BeautifulSoup(response.text, 'html5lib')
            print("Page HTML récupérée et parsée")
            
            # Trouve la table des résultats
            table = soup.find('table', {'class': ['c']})
            if table:
                # Ignore la première ligne (en-têtes)
                rows = table.find_all('tr')[1:]
                print(f"Nombre de lignes trouvées: {len(rows)}")
                
                for row in rows:
                    try:
                        # Récupère les cellules
                        cells = row.find_all('td')
                        if len(cells) < 8:
                            print(f"❌ Pas assez de cellules: {len(cells)}")
                            continue
                        
                        # Titre et URL
                        title_cell = cells[2]
                        title_link = title_cell.find('a')
                        if not title_link:
                            print("❌ Pas de lien de titre trouvé")
                            continue
                            
                        title = title_link.get_text(strip=True)
                        href = title_link.get('href', '')
                        
                        # Vérifie si c'est un lien vers une série
                        if 'series' in href or 'search.php' in href:
                            print("❌ Lien de série ignoré")
                            continue
                            
                        # Extrait le MD5 du lien
                        try:
                            md5 = href.split('md5=')[1] if 'md5=' in href else None
                            if not md5:
                                print("❌ Pas de MD5 trouvé dans le lien")
                                continue
                            book_url = f"{self.base_url}/book/index.php?md5={md5}"
                        except Exception as e:
                            print(f"❌ Erreur lors de l'extraction du MD5: {str(e)}")
                            continue
                        
                        print(f"\n📖 Titre trouvé: {title}")
                        print(f"🔗 URL: {book_url}")
                        
                        # Auteur
                        author = cells[1].get_text(strip=True)
                        print(f"👤 Auteur: {author}")
                        
                        # Langue
                        book_language = cells[6].get_text(strip=True).lower()
                        print(f"🌍 Langue: {book_language}")
                        
                        # Lien de téléchargement
                        download_cell = cells[8] if len(cells) > 8 else None
                        download_url = None
                        if download_cell:
                            download_link = download_cell.find('a')
                            if download_link:
                                download_url = download_link.get('href', '')
                                if not download_url.startswith('http'):
                                    # Utilise l'URL de base pour le téléchargement
                                    download_url = f"{self.base_url}/get.php?md5=" + download_url.split('=')[-1]
                                print(f"⬇️ Lien de téléchargement: {download_url}")
                        
                        # Vérifie la langue
                        if book_language != libgen_language:
                            print(f"❌ Mauvaise langue ({book_language}), on cherche {libgen_language}")
                            continue
                        
                        results.append({
                            'title': title,
                            'author': author,
                            'url': book_url,
                            'source': self.name,
                            'language': language.upper(),
                            'is_free': True,
                            'read_url': None,
                            'download_url': download_url
                        })
                        print(f"✅ Livre ajouté aux résultats: {title}")
                        
                    except Exception as e:
                        print(f"❌ Erreur lors du parsing d'une ligne: {str(e)}")
                        continue
            else:
                print("❌ Aucune table de résultats trouvée")
                print("\nAperçu du HTML reçu:")
                print(response.text[:500])
                    
        except Exception as e:
            print(f"❌ Erreur de recherche: {str(e)}")
            
        print(f"\n📊 Nombre total de résultats: {len(results)}")
        return results