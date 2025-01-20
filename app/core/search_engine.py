"""
Moteur de recherche principal
"""

import importlib
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from app.core.config import Config
from app.core.base_source import BookSource  # Correction du chemin d'import

class SearchEngine:
    """Moteur de recherche qui agrège les résultats de différentes sources"""
    
    def __init__(self):
        """Initialise le moteur de recherche avec les sources configurées"""
        self.sources = {}
        self._load_sources()
        
    def _load_sources(self):
        """Charge dynamiquement les sources configurées"""
        for source_name in Config.SOURCES:
            try:
                # Importe le module de la source
                module_path = f'app.sources.{source_name}'
                print(f"\nChargement de {module_path}")
                module = importlib.import_module(module_path)
                
                # Liste les attributs du module
                print(f"Attributs du module: {dir(module)}")
                
                # Vérifie d'abord si la classe existe directement dans le module
                for attr in dir(module):
                    if attr.endswith('Source') and attr != 'BookSource':
                        try:
                            source_class = getattr(module, attr)
                            if (isinstance(source_class, type) and  # Vérifie que c'est bien une classe
                                hasattr(source_class, '__base__') and  # Vérifie qu'elle a une classe parente
                                source_class.__base__.__name__ == 'BookSource'):  # Vérifie qu'elle hérite de BookSource
                                print(f"✅ Classe trouvée: {attr}")
                                self.sources[source_name] = source_class()
                                print(f"✅ Source chargée: {source_name}")
                                break
                        except Exception as e:
                            print(f"❌ Erreur lors de l'instanciation de {attr}: {str(e)}")
                else:  # Si aucune classe n'a été trouvée
                    raise AttributeError(f"Aucune classe source trouvée dans {source_name}")
                
            except Exception as e:
                print(f"❌ Erreur lors du chargement de la source {source_name}: {str(e)}")
                import traceback
                print(traceback.format_exc())
    
    async def _search_source(self, source_name: str, source, query: str, language: str) -> List[Dict[str, Any]]:
        """Effectue la recherche sur une source de manière asynchrone"""
        try:
            print(f"\nRecherche sur {source_name}...")
            # Crée une session aiohttp pour les requêtes HTTP
            async with aiohttp.ClientSession() as session:
                # Si la source a une méthode de recherche asynchrone, utilise-la
                if hasattr(source, 'search_async'):
                    print(f"Utilisation de search_async pour {source_name}")
                    results = await source.search_async(query, language, session)
                else:
                    # Sinon, exécute la méthode synchrone dans un thread séparé
                    print(f"Utilisation de search synchrone pour {source_name}")
                    with ThreadPoolExecutor() as executor:
                        results = await asyncio.get_event_loop().run_in_executor(
                            executor,
                            source.search,
                            query,
                            language
                        )
                print(f"✅ {len(results)} résultats trouvés sur {source_name}")
                for result in results:
                    print(f"  - {result.get('title', 'Sans titre')} ({result.get('source', 'Source inconnue')})")
                return results
        except Exception as e:
            print(f"❌ Erreur lors de la recherche sur {source_name}: {str(e)}")
            return []
    
    async def _calculate_result_score(self, result: Dict[str, Any], query: str, target_language: str) -> float:
        """
        Calcule un score de pertinence pour un résultat
        
        Args:
            result: Résultat de recherche
            query: Terme de recherche
            target_language: Langue cible
            
        Returns:
            Score entre 0 et 1
        """
        # Calcule la similarité avec le titre (poids: 50%)
        title_score = BookSource.calculate_similarity(query, result['title']) * 0.5
        
        # Calcule la similarité avec l'auteur (poids: 20%)
        author_score = BookSource.calculate_similarity(query, result['author']) * 0.2
        
        # Score de langue (poids: 30%)
        language_score = 0.0
        if 'language' in result:
            # Correspondance exacte de la langue
            if result['language'].lower() == target_language.lower():
                language_score = 0.3
            # Bonus partiel pour l'anglais si ce n'est pas la langue cible
            # (car c'est souvent une langue acceptable comme alternative)
            elif result['language'].lower() == 'en' and target_language.lower() != 'en':
                language_score = 0.15
        
        # Le score final est la somme des trois scores
        return title_score + author_score + language_score
    
    async def search_async(self, query: str, language: str = 'fr') -> List[Dict[str, Any]]:
        """Effectue la recherche sur toutes les sources de manière asynchrone"""
        print(f"\nDémarrage de la recherche pour '{query}' en langue '{language}'")
        tasks = []
        
        # Crée une tâche asynchrone pour chaque source
        for source_name, source in self.sources.items():
            task = asyncio.create_task(
                self._search_source(source_name, source, query, language)
            )
            tasks.append(task)
        
        # Attend que toutes les tâches soient terminées
        results = await asyncio.gather(*tasks)
        
        # Fusionne et trie les résultats
        all_results = []
        for source_results in results:
            print(f"Ajout de {len(source_results)} résultats")
            all_results.extend(source_results)
        
        print(f"Calcul des scores pour {len(all_results)} résultats...")
        # Calcule un score pour chaque résultat
        for result in all_results:
            result['score'] = await self._calculate_result_score(result, query, language)
        
        # Trie par score décroissant
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        print(f"\nRésultats finaux :")
        print(f"- Nombre total : {len(all_results)}")
        for result in all_results[:5]:  # Affiche les 5 premiers résultats
            print(f"- {result.get('title', 'Sans titre')} (score: {result.get('score', 0):.2f})")
        
        return all_results
    
    def search(self, query: str, language: str = 'fr') -> List[Dict[str, Any]]:
        """Interface synchrone pour la recherche (utilise asyncio en interne)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si une boucle est déjà en cours, utilise run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(
                    self.search_async(query, language),
                    loop
                )
                return future.result()
            else:
                # Sinon, utilise run_until_complete
                return loop.run_until_complete(self.search_async(query, language))
        except Exception as e:
            print(f"❌ Erreur lors de la recherche synchrone: {str(e)}")
            return []
