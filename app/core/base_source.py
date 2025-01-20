"""
Classe de base pour toutes les sources de livres
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

class BookSource(ABC):
    """Classe de base abstraite pour toutes les sources de livres"""
    
    def __init__(self, name: str, base_url: str):
        """
        Initialise une source de livres
        
        Args:
            name: Nom de la source
            base_url: URL de base de la source
        """
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Mapping des codes de langue
        self.language_map = {
            'fr': 'french',
            'en': 'english',
            'es': 'spanish',
            'de': 'german',
            'it': 'italian',
            'pt': 'portuguese',
            'ru': 'russian',
            'zh': 'chinese',
            'ja': 'japanese',
            'ko': 'korean'
        }
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calcule un score de similarité entre deux chaînes
        
        Args:
            str1: Première chaîne
            str2: Deuxième chaîne
            
        Returns:
            Score entre 0 et 1, où 1 signifie que les chaînes sont identiques
        """
        # Normalise les chaînes pour la comparaison
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Utilise SequenceMatcher pour calculer la similarité
        return SequenceMatcher(None, str1, str2).ratio()
    
    @abstractmethod
    def search(self, query: str, language: str = 'fr') -> List[Dict[str, Any]]:
        """
        Recherche des livres
        
        Args:
            query: Terme de recherche
            language: Code de langue (fr, en, etc.)
            
        Returns:
            Liste de résultats
        """
        pass
    
    def get_language_code(self, language: str) -> str:
        """Retourne le code de langue approprié pour la source"""
        return self.language_map.get(language, 'english')
    
    def create_search_result(self, title: str, author: str, url: str, language: str, 
                           preview: str = '', score: float = 1.0) -> Dict[str, Any]:
        """
        Crée un résultat de recherche standardisé
        
        Args:
            title: Titre du livre
            author: Auteur du livre
            url: URL du livre
            language: Langue du livre
            preview: Aperçu ou description
            score: Score de pertinence
            
        Returns:
            Dictionnaire contenant les informations du livre
        """
        return {
            'title': title,
            'author': author,
            'source': self.name,
            'url': url,
            'language': language,
            'preview': preview,
            'score': score
        }
    
    def format_result(self, title: str, author: str, url: str, 
                     series_name: str = None, series_volume: int = None) -> Dict[str, Any]:
        """
        Formate un résultat de recherche de manière standardisée.
        
        Args:
            title (str): Titre du livre
            author (str): Auteur du livre
            url (str): URL du livre
            series_name (str, optional): Nom de la série
            series_volume (int, optional): Numéro du volume dans la série
            
        Returns:
            Dict[str, Any]: Résultat formaté
        """
        result = {
            'title': title,
            'author': author,
            'url': url,
            'source': self.name
        }
        
        if series_name:
            result['series'] = {
                'name': series_name,
                'volume': series_volume if series_volume is not None else 1
            }
            
        return result
    
    def make_request(self, url: str, method: str = 'get', **kwargs) -> requests.Response:
        """
        Effectue une requête HTTP avec gestion des erreurs
        
        Args:
            url: URL à requêter
            method: Méthode HTTP (get, post)
            **kwargs: Arguments supplémentaires pour la requête
            
        Returns:
            Réponse HTTP
            
        Raises:
            requests.RequestException: En cas d'erreur de requête
        """
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Erreur lors de la requête vers {url}: {str(e)}")
            raise
    
    def parse_html(self, content: str) -> BeautifulSoup:
        """Parse le contenu HTML avec BeautifulSoup"""
        return BeautifulSoup(content, 'lxml')
    
    def extract_text(self, element: BeautifulSoup) -> str:
        """Extrait le texte d'un élément BeautifulSoup de manière sécurisée"""
        return element.get_text(strip=True) if element else ''
