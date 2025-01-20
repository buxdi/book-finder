// Fonctions utilitaires pour l'interface

// Fonction pour formater le nombre de résultats
function formatResultCount(count) {
    return new Intl.NumberFormat().format(count);
}

// Fonction pour échapper les caractères HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Fonction pour copier un lien dans le presse-papiers
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Lien copié !');
    }).catch(err => {
        console.error('Erreur lors de la copie :', err);
        showToast('Erreur lors de la copie', 'error');
    });
}

// Fonction pour afficher un toast de notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Force le reflow pour déclencher l'animation
    toast.offsetHeight;
    
    // Affiche le toast
    toast.classList.add('show');
    
    // Supprime le toast après 3 secondes
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Fonction pour détecter la langue du navigateur
function getBrowserLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    return lang.split('-')[0];
}

// Fonction pour mettre à jour l'URL avec les paramètres de recherche
function updateURL(params) {
    const url = new URL(window.location);
    for (const [key, value] of Object.entries(params)) {
        if (value) {
            url.searchParams.set(key, value);
        } else {
            url.searchParams.delete(key);
        }
    }
    window.history.pushState({}, '', url);
}

// Gestionnaire d'événements pour le changement de langue
document.addEventListener('DOMContentLoaded', function() {
    // Gestion du changement de langue
    const languageLinks = document.querySelectorAll('[data-language]');
    languageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.dataset.language;
            updateURL({ lang });
            window.location.reload();
        });
    });
    
    // Restauration des paramètres de recherche depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const searchInput = document.getElementById('searchInput');
    if (searchInput && urlParams.has('q')) {
        searchInput.value = urlParams.get('q');
        // Déclenche la recherche si un terme est présent
        document.getElementById('searchForm').dispatchEvent(new Event('submit'));
    }
});
