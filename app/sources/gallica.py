"""
Source Gallica
"""

import os
import sys
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import html5lib
import re

# Ajoute le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.base_source import BookSource

class GallicaSource(BookSource):
    """Source Gallica"""
    
    def __init__(self):
        super().__init__('Gallica', 'https://gallica.bnf.fr')
        
    def extract_series_info(self, title: str) -> tuple:
        """
        Extrait les informations de série du titre.
        
        Args:
            title (str): Titre complet du livre
            
        Returns:
            tuple: (titre_sans_tome, nom_serie, numero_tome)
        """
        # Motifs pour détecter les tomes
        patterns = [
            r'Tome (\d+)',
            r'Volume (\d+)',
            r'Livre (\d+)',
            r'Part(?:ie)? (\d+)',
        ]
        
        title_clean = title
        series_name = None
        volume_number = None
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                volume_number = int(match.group(1))
                # Extrait le nom de la série (tout ce qui précède "Tome X")
                series_parts = re.split(pattern, title, flags=re.IGNORECASE)
                if len(series_parts) > 0:
                    series_name = series_parts[0].strip('. ')
                    # Nettoie le titre en enlevant la partie tome
                    title_clean = series_name
                break
                
        return title_clean, series_name, volume_number
    
    def search(self, query: str, lang: str = None) -> List[Dict[str, Any]]:
        """
        Recherche des livres sur Gallica
        
        Args:
            query (str): Terme de recherche
            lang (str, optional): Code de langue (ex: 'fr')
            
        Returns:
            List[Dict[str, Any]]: Liste des résultats
        """
        print("\nRecherche sur Gallica (https://gallica.bnf.fr/SRU)")
        
        # Construit la requête SRU
        params = {
            'operation': 'searchRetrieve',
            'version': '1.2',
            'query': f'dc.title all "{query}"',
            'maximumRecords': '20',
            'startRecord': '1',
            'recordSchema': 'dc'
        }
        
        print(f"Paramètres: {params}")
        
        try:
            # Effectue la requête avec un User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/xml'
            }
            response = self.make_request('https://gallica.bnf.fr/SRU', params=params, headers=headers)
            
            # Parse le XML avec le bon parseur
            soup = BeautifulSoup(response.content, 'xml')
            
            # Trouve tous les résultats avec namespace
            ns = {'srw': 'http://www.loc.gov/zing/srw/',
                  'dc': 'http://purl.org/dc/elements/1.1/'}
                  
            records = soup.find_all('srw:record', ns)
            if not records:
                records = soup.find_all('record')  # essai sans namespace
                if not records:
                    print("❌ Aucun résultat trouvé")
                    return []
            
            results = []
            for record in records:
                try:
                    # Récupère le titre
                    title_elem = record.find('dc:title', ns) or record.find('title')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    
                    # Extraction des informations de série
                    clean_title, series_name, volume = self.extract_series_info(title)
                    
                    # Récupère l'URL
                    identifier = record.find('dc:identifier', ns) or record.find('identifier')
                    if not identifier:
                        continue
                        
                    book_url = identifier.get_text(strip=True)
                    if not book_url.startswith('http'):
                        continue
                    
                    # Récupère l'auteur
                    creator = record.find('dc:creator', ns) or record.find('creator')
                    author = creator.get_text(strip=True) if creator else "Auteur inconnu"
                    
                    # Affichage des informations trouvées
                    print(f"\n📖 Titre trouvé: {title}")
                    print(f"🔗 URL: {book_url}")
                    print(f"👤 Auteur: {author}")
                    if series_name:
                        print(f"📚 Série: {series_name} (Tome {volume})")
                    
                    # Utilise format_result pour un format cohérent
                    results.append(self.format_result(
                        title=clean_title,
                        author=author,
                        url=book_url,
                        series_name=series_name,
                        series_volume=volume
                    ))
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors du traitement d'un résultat: {str(e)}")
                    continue
            
            print(f"\n📊 Nombre de résultats trouvés: {len(results)}")
            return results
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche sur Gallica: {str(e)}")
            return []
