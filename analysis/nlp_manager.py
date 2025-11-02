"""
NLP Model Manager - Gestisce caricamento dinamico modelli multi-lingua

Questo modulo fornisce un singleton per gestire il caricamento lazy e il caching
dei modelli NLP (spaCy e LanguageTool) per diverse lingue.

Supported Languages:
    - it: Italian
    - en: English
    - es: Spanish
    - fr: French
    - de: German
"""
import os
import sys
import spacy
import language_tool_python
import textstat
from typing import Optional, Dict
from utils.logger import AppLogger

# PyInstaller compatibility
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NLPModelManager:
    """
    Singleton per gestire modelli NLP multi-lingua con caching

    Features:
        - Lazy loading: modelli caricati solo quando necessari
        - Caching: modelli rimangono in memoria per performance
        - Multi-lingua: supporto per 5 lingue
        - Fallback: gestione errori con fallback a italiano
    """

    _instance = None

    # Mappatura lingua -> modello spaCy
    SPACY_MODELS = {
        'it': 'it_core_news_sm',
        'en': 'en_core_web_sm',
        'es': 'es_core_news_sm',
        'fr': 'fr_core_news_sm',
        'de': 'de_core_news_sm'
    }

    # Mappatura lingua -> codice LanguageTool
    LANGUAGETOOL_CODES = {
        'it': 'it',
        'en': 'en-US',
        'es': 'es',
        'fr': 'fr',
        'de': 'de-DE'
    }

    # Mappatura lingua -> codice textstat
    TEXTSTAT_CODES = {
        'it': 'it',
        'en': 'en',
        'es': 'es',
        'fr': 'fr',
        'de': 'de'
    }

    def __new__(cls):
        """Implementa pattern Singleton"""
        if cls._instance is None:
            cls._instance = super(NLPModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inizializza il manager (chiamato solo una volta)"""
        if self._initialized:
            return

        self._spacy_models: Dict[str, spacy.Language] = {}
        self._language_tools: Dict[str, language_tool_python.LanguageTool] = {}
        self._current_language: Optional[str] = None
        self._initialized = True

        AppLogger.info("NLPModelManager initialized")

    def set_language(self, language_code: str) -> bool:
        """
        Imposta la lingua corrente e prepara i modelli

        Args:
            language_code: Codice lingua ('it', 'en', etc.)

        Returns:
            bool: True se successo, False se lingua non supportata
        """
        if language_code not in self.SPACY_MODELS:
            AppLogger.warning(f"Language {language_code} not supported, falling back to 'it'")
            language_code = 'it'

        if self._current_language == language_code:
            AppLogger.debug(f"Language already set to {language_code}")
            return True

        AppLogger.info(f"Setting language to: {language_code}")
        self._current_language = language_code

        # Configura textstat per la nuova lingua
        textstat_code = self.TEXTSTAT_CODES.get(language_code, 'en')
        textstat.set_lang(textstat_code)

        return True

    def get_spacy_model(self, language_code: Optional[str] = None) -> Optional[spacy.Language]:
        """
        Ottiene il modello spaCy per la lingua specificata (lazy loading)

        Args:
            language_code: Codice lingua (usa current_language se None)

        Returns:
            spacy.Language o None se modello non disponibile
        """
        lang = language_code or self._current_language

        if not lang:
            AppLogger.error("No language set, cannot load spaCy model")
            return None

        # Controlla se già in cache
        if lang in self._spacy_models:
            AppLogger.debug(f"Using cached spaCy model for {lang}")
            return self._spacy_models[lang]

        # Carica modello
        model_name = self.SPACY_MODELS.get(lang)
        if not model_name:
            AppLogger.error(f"No spaCy model defined for language: {lang}")
            return None

        try:
            AppLogger.info(f"Loading spaCy model: {model_name}")

            # Try standard load first (works in dev environment)
            try:
                nlp = spacy.load(model_name)
            except OSError:
                # If running in PyInstaller bundle, try loading from extracted path
                if getattr(sys, 'frozen', False):
                    # Map model names to their bundle paths
                    model_paths = {
                        'it_core_news_sm': os.path.join(BASE_PATH, 'it_core_news_sm', 'it_core_news_sm-3.8.0'),
                        'en_core_web_sm': os.path.join(BASE_PATH, 'en_core_web_sm', 'en_core_web_sm-3.8.0'),
                        # Add other models as needed
                    }

                    model_path = model_paths.get(model_name)
                    if model_path and os.path.exists(model_path):
                        AppLogger.info(f"Loading from bundle path: {model_path}")
                        nlp = spacy.load(model_path)
                    else:
                        raise OSError(f"Model {model_name} not found in bundle")
                else:
                    raise

            self._spacy_models[lang] = nlp
            AppLogger.info(f"✓ spaCy model loaded successfully: {model_name}")
            return nlp

        except OSError as e:
            AppLogger.error(
                f"spaCy model '{model_name}' not found. "
                f"Install with: python -m spacy download {model_name}",
                exc_info=False
            )

            # Fallback a italiano se disponibile
            if lang != 'it' and 'it' in self._spacy_models:
                AppLogger.warning(f"Falling back to Italian model")
                return self._spacy_models['it']

            return None

        except Exception as e:
            AppLogger.error(f"Error loading spaCy model: {e}")
            return None

    def get_language_tool(self, language_code: Optional[str] = None) -> Optional[language_tool_python.LanguageTool]:
        """
        Ottiene LanguageTool per la lingua specificata (lazy loading)

        Args:
            language_code: Codice lingua (usa current_language se None)

        Returns:
            LanguageTool o None se non disponibile
        """
        lang = language_code or self._current_language

        if not lang:
            AppLogger.error("No language set, cannot load LanguageTool")
            return None

        # Controlla se già in cache
        if lang in self._language_tools:
            AppLogger.debug(f"Using cached LanguageTool for {lang}")
            return self._language_tools[lang]

        # Ottieni codice LanguageTool
        lt_code = self.LANGUAGETOOL_CODES.get(lang)
        if not lt_code:
            AppLogger.error(f"No LanguageTool code for language: {lang}")
            return None

        try:
            AppLogger.info(f"Initializing LanguageTool: {lt_code}")
            tool = language_tool_python.LanguageTool(lt_code)
            self._language_tools[lang] = tool
            AppLogger.info(f"✓ LanguageTool initialized successfully: {lt_code}")
            return tool

        except Exception as e:
            AppLogger.error(f"Error initializing LanguageTool for {lang}: {e}")

            # Fallback a italiano se disponibile
            if lang != 'it' and 'it' in self._language_tools:
                AppLogger.warning(f"Falling back to Italian LanguageTool")
                return self._language_tools['it']

            return None

    def preload_language(self, language_code: str) -> bool:
        """
        Pre-carica tutti i modelli per una lingua (operazione in background)

        Args:
            language_code: Codice lingua

        Returns:
            bool: True se tutti i modelli sono stati caricati
        """
        AppLogger.info(f"Preloading models for language: {language_code}")

        success = True

        # Carica spaCy
        if self.get_spacy_model(language_code) is None:
            success = False

        # Carica LanguageTool
        if self.get_language_tool(language_code) is None:
            success = False

        if success:
            AppLogger.info(f"✓ All models preloaded for {language_code}")
        else:
            AppLogger.warning(f"⚠ Some models failed to load for {language_code}")

        return success

    def is_model_available(self, language_code: str) -> Dict[str, bool]:
        """
        Controlla disponibilità modelli per una lingua SENZA caricarli

        Args:
            language_code: Codice lingua

        Returns:
            dict: {'spacy': bool, 'languagetool': bool}
        """
        result = {
            'spacy': False,
            'languagetool': False
        }

        # Check spaCy
        model_name = self.SPACY_MODELS.get(language_code)
        if model_name:
            try:
                # Check if model is installed
                available_models = spacy.util.get_installed_models()
                result['spacy'] = model_name in available_models
            except Exception:
                result['spacy'] = False

        # Check LanguageTool (sempre disponibile, scarica on-demand)
        result['languagetool'] = language_code in self.LANGUAGETOOL_CODES

        return result

    def unload_language(self, language_code: str):
        """
        Rimuove i modelli di una lingua dalla cache (per liberare memoria)

        Args:
            language_code: Codice lingua
        """
        if language_code in self._spacy_models:
            del self._spacy_models[language_code]
            AppLogger.info(f"Unloaded spaCy model for {language_code}")

        if language_code in self._language_tools:
            try:
                self._language_tools[language_code].close()
            except Exception:
                pass
            del self._language_tools[language_code]
            AppLogger.info(f"Unloaded LanguageTool for {language_code}")

    def get_current_language(self) -> Optional[str]:
        """Ritorna la lingua corrente"""
        return self._current_language

    def get_supported_languages(self) -> list:
        """Ritorna lista lingue supportate"""
        return list(self.SPACY_MODELS.keys())

    def cleanup(self):
        """Chiude tutti i tool e libera memoria"""
        AppLogger.info("Cleaning up NLP models...")

        for lang in list(self._language_tools.keys()):
            try:
                self._language_tools[lang].close()
            except Exception:
                pass

        self._spacy_models.clear()
        self._language_tools.clear()
        AppLogger.info("NLP models cleaned up")


# Istanza globale singleton
nlp_manager = NLPModelManager()
