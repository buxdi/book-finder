"""
Tests pour le moteur de recherche
"""

import pytest
from app.core.search_engine import SearchEngine
from app.core.config import Config

def test_search_engine_initialization():
    """Test l'initialisation du moteur de recherche"""
    engine = SearchEngine()
    assert len(engine.sources) > 0, "Le moteur de recherche devrait avoir des sources"

def test_search_with_empty_query():
    """Test la recherche avec une requête vide"""
    engine = SearchEngine()
    results = engine.search("")
    assert len(results) == 0, "Une requête vide ne devrait pas retourner de résultats"

def test_search_with_valid_query():
    """Test la recherche avec une requête valide"""
    engine = SearchEngine()
    results = engine.search("Python programming")
    assert isinstance(results, list), "Les résultats devraient être une liste"
    
    if results:  # Si des résultats sont trouvés
        result = results[0]
        assert "title" in result, "Chaque résultat devrait avoir un titre"
        assert "author" in result, "Chaque résultat devrait avoir un auteur"
        assert "url" in result, "Chaque résultat devrait avoir une URL"
        assert "source" in result, "Chaque résultat devrait avoir une source"

def test_search_respects_max_results():
    """Test que la recherche respecte le nombre maximum de résultats"""
    engine = SearchEngine()
    results = engine.search("Python")
    assert len(results) <= Config.MAX_SEARCH_RESULTS, \
        "Le nombre de résultats ne devrait pas dépasser MAX_SEARCH_RESULTS"

def test_search_with_different_languages():
    """Test la recherche dans différentes langues"""
    engine = SearchEngine()
    for lang in Config.SUPPORTED_LANGUAGES.keys():
        results = engine.search("test", lang)
        assert isinstance(results, list), f"La recherche devrait fonctionner pour la langue {lang}"
