/* ===================================
   JOLODHAR - i18n (Language Toggle)
   Bengali + English
   =================================== */

(function () {
    "use strict";

    const translations = window.JOLODHAR && window.JOLODHAR.translations ? window.JOLODHAR.translations : {};
    let currentLang = window.JOLODHAR && window.JOLODHAR.lang ? window.JOLODHAR.lang : "bn";

    /**
     * Apply translations to all elements with data-i18n attribute
     */
    function applyTranslations(lang) {
        currentLang = lang;
        const langTranslations = translations[lang] || translations["en"] || {};

        // Text content
        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            const key = el.getAttribute("data-i18n");
            if (langTranslations[key]) {
                el.textContent = langTranslations[key];
            }
        });

        // Placeholders
        document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
            const key = el.getAttribute("data-i18n-placeholder");
            if (langTranslations[key]) {
                el.setAttribute("placeholder", langTranslations[key]);
            }
        });

        // Update html lang
        document.documentElement.lang = lang;

        // Update toggle button label
        const langLabel = document.getElementById("langLabel");
        if (langLabel) {
            langLabel.textContent = lang === "bn" ? "English" : "বাংলা";
        }
    }

    /**
     * Toggle between Bengali and English
     */
    window.toggleLanguage = function () {
        const newLang = currentLang === "bn" ? "en" : "bn";

        // Send to server to persist in session
        const url = window.JOLODHAR.endpoints.setLang(newLang);
        fetch(url, { method: "POST" })
            .then(function () {
                // Reload to get fresh translations from server
                window.location.reload();
            })
            .catch(function () {
                // Fallback: apply locally
                applyTranslations(newLang);
            });
    };

    /**
     * Get translation for a key (for use in JS code)
     */
    window.t = function (key) {
        const langTranslations = translations[currentLang] || translations["en"] || {};
        return langTranslations[key] || key;
    };

    window.getCurrentLang = function () {
        return currentLang;
    };

    // Apply on load
    document.addEventListener("DOMContentLoaded", function () {
        applyTranslations(currentLang);
    });

    // Expose for re-application
    window.applyTranslations = applyTranslations;
})();
