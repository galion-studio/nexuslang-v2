"""
Multi-language support for Deep Search.
Provides translation, language detection, and cross-language research capabilities.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import json

try:
    import langdetect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    langdetect = None

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    Translator = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from ...services.deep_search.agents import AgentOrchestrator

logger = logging.getLogger(__name__)


class MultiLanguageSupport:
    """
    Comprehensive multi-language support for research.

    Features:
    - Automatic language detection
    - Real-time translation
    - Cross-language research synthesis
    - Localized content processing
    - Language-specific search optimization
    - Cultural context awareness
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key

        # Supported languages with metadata
        self.supported_languages = {
            'en': {
                'name': 'English',
                'native_name': 'English',
                'region': 'Global',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.8
            },
            'es': {
                'name': 'Spanish',
                'native_name': 'Español',
                'region': 'Spain, Latin America',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'fr': {
                'name': 'French',
                'native_name': 'Français',
                'region': 'France, Canada, Africa',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'de': {
                'name': 'German',
                'native_name': 'Deutsch',
                'region': 'Germany, Austria, Switzerland',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'it': {
                'name': 'Italian',
                'native_name': 'Italiano',
                'region': 'Italy, Switzerland',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'pt': {
                'name': 'Portuguese',
                'native_name': 'Português',
                'region': 'Portugal, Brazil',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'ru': {
                'name': 'Russian',
                'native_name': 'Русский',
                'region': 'Russia, Eastern Europe',
                'script': 'Cyrillic',
                'direction': 'ltr',
                'confidence_threshold': 0.6
            },
            'zh': {
                'name': 'Chinese',
                'native_name': '中文',
                'region': 'China, Taiwan, Singapore',
                'script': 'Han',
                'direction': 'ltr',
                'confidence_threshold': 0.6
            },
            'ja': {
                'name': 'Japanese',
                'native_name': '日本語',
                'region': 'Japan',
                'script': 'Kanji/Hiragana/Katakana',
                'direction': 'ltr',
                'confidence_threshold': 0.6
            },
            'ko': {
                'name': 'Korean',
                'native_name': '한국어',
                'region': 'South Korea, North Korea',
                'script': 'Hangul',
                'direction': 'ltr',
                'confidence_threshold': 0.6
            },
            'ar': {
                'name': 'Arabic',
                'native_name': 'العربية',
                'region': 'Middle East, North Africa',
                'script': 'Arabic',
                'direction': 'rtl',
                'confidence_threshold': 0.6
            },
            'hi': {
                'name': 'Hindi',
                'native_name': 'हिन्दी',
                'region': 'India',
                'script': 'Devanagari',
                'direction': 'ltr',
                'confidence_threshold': 0.6
            },
            'nl': {
                'name': 'Dutch',
                'native_name': 'Nederlands',
                'region': 'Netherlands, Belgium',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'sv': {
                'name': 'Swedish',
                'native_name': 'Svenska',
                'region': 'Sweden, Finland',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'da': {
                'name': 'Danish',
                'native_name': 'Dansk',
                'region': 'Denmark',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'no': {
                'name': 'Norwegian',
                'native_name': 'Norsk',
                'region': 'Norway',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            },
            'fi': {
                'name': 'Finnish',
                'native_name': 'Suomi',
                'region': 'Finland',
                'script': 'Latin',
                'direction': 'ltr',
                'confidence_threshold': 0.7
            }
        }

        # Translation service initialization
        self.translator = None
        if GOOGLETRANS_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception as e:
                logger.warning(f"Google Translate initialization failed: {e}")

        # Language detection settings
        self.detection_cache = {}
        self.cache_ttl = 3600  # 1 hour

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of input text.

        Uses multiple detection methods for improved accuracy.
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "Empty text provided",
                    "detected_language": None,
                    "confidence": 0.0
                }

            # Check cache first
            cache_key = hash(text[:100])  # Use first 100 chars for cache key
            if cache_key in self.detection_cache:
                cached_result = self.detection_cache[cache_key]
                if (datetime.utcnow().timestamp() - cached_result["timestamp"]) < self.cache_ttl:
                    return cached_result["result"]

            detection_results = []

            # Method 1: langdetect library
            if LANGDETECT_AVAILABLE:
                try:
                    langdetect_result = langdetect.detect_langs(text)
                    for result in langdetect_result:
                        detection_results.append({
                            "language": result.lang,
                            "confidence": result.prob,
                            "method": "langdetect"
                        })
                except Exception as e:
                    logger.warning(f"langdetect failed: {e}")

            # Method 2: Simple heuristic-based detection
            heuristic_result = self._heuristic_language_detection(text)
            if heuristic_result:
                detection_results.append({
                    **heuristic_result,
                    "method": "heuristic"
                })

            # Method 3: Character-based detection
            char_result = self._character_based_detection(text)
            if char_result:
                detection_results.append({
                    **char_result,
                    "method": "character_analysis"
                })

            if not detection_results:
                return {
                    "success": False,
                    "error": "Language detection failed",
                    "detected_language": None,
                    "confidence": 0.0
                }

            # Aggregate results
            aggregated = self._aggregate_detection_results(detection_results)

            # Cache result
            self.detection_cache[cache_key] = {
                "result": aggregated,
                "timestamp": datetime.utcnow().timestamp()
            }

            return aggregated

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "success": False,
                "error": f"Detection error: {str(e)}",
                "detected_language": None,
                "confidence": 0.0
            }

    async def translate_text(self, text: str, target_language: str,
                           source_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text to target language.

        Supports multiple translation engines for best results.
        """
        try:
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "Empty text provided",
                    "translated_text": "",
                    "source_language": source_language,
                    "target_language": target_language
                }

            # Detect source language if not provided
            if not source_language:
                detection = await self.detect_language(text)
                if detection["success"]:
                    source_language = detection["detected_language"]
                else:
                    source_language = "auto"

            translation_results = []

            # Method 1: Google Translate
            if self.translator:
                try:
                    google_result = self.translator.translate(
                        text, dest=target_language, src=source_language
                    )
                    translation_results.append({
                        "text": google_result.text,
                        "confidence": 0.8,
                        "method": "google_translate",
                        "detected_source": google_result.src
                    })
                except Exception as e:
                    logger.warning(f"Google Translate failed: {e}")

            # Method 2: OpenAI (for complex or nuanced translations)
            if OPENAI_AVAILABLE and self.openai_api_key:
                try:
                    openai_result = await self._openai_translate(
                        text, target_language, source_language
                    )
                    if openai_result:
                        translation_results.append(openai_result)
                except Exception as e:
                    logger.warning(f"OpenAI translation failed: {e}")

            if not translation_results:
                return {
                    "success": False,
                    "error": "Translation failed - no translation services available",
                    "translated_text": "",
                    "source_language": source_language,
                    "target_language": target_language
                }

            # Select best translation
            best_translation = self._select_best_translation(translation_results)

            return {
                "success": True,
                "translated_text": best_translation["text"],
                "source_language": source_language,
                "target_language": target_language,
                "confidence": best_translation["confidence"],
                "method": best_translation["method"],
                "alternatives": [t for t in translation_results if t != best_translation]
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": f"Translation error: {str(e)}",
                "translated_text": "",
                "source_language": source_language,
                "target_language": target_language
            }

    async def perform_cross_language_research(self, query: str, query_language: str,
                                            response_language: str,
                                            user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform research with cross-language capabilities.

        Research in multiple languages and synthesize results in the target language.
        """
        try:
            start_time = asyncio.get_event_loop().time()

            # Translate query to English for research if needed
            research_query = query
            if query_language != 'en':
                translation = await self.translate_text(query, 'en', query_language)
                if translation["success"]:
                    research_query = translation["translated_text"]
                else:
                    logger.warning(f"Query translation failed, using original: {query}")

            # Perform research in English
            orchestrator = AgentOrchestrator()
            research_result = await orchestrator.execute_research(
                research_query,
                {
                    "depth": "comprehensive",
                    "language": query_language,
                    "cross_language": True,
                    "user_context": user_context
                }
            )

            if not research_result or "synthesized_answer" not in research_result:
                return {
                    "success": False,
                    "error": "Research execution failed",
                    "query": query,
                    "query_language": query_language,
                    "response_language": response_language
                }

            # Translate response to target language if needed
            final_answer = research_result["synthesized_answer"]
            if response_language != 'en':
                translation = await self.translate_text(final_answer, response_language, 'en')
                if translation["success"]:
                    final_answer = translation["translated_text"]
                    research_result["translated_answer"] = final_answer
                    research_result["original_answer"] = research_result["synthesized_answer"]
                    research_result["response_language"] = response_language

            # Add language metadata
            research_result.update({
                "query_language": query_language,
                "research_language": 'en',  # Research performed in English
                "response_language": response_language,
                "cross_language_processing": query_language != response_language,
                "processing_time": asyncio.get_event_loop().time() - start_time
            })

            return {
                "success": True,
                "research_result": research_result,
                "language_info": {
                    "query_language": query_language,
                    "research_language": 'en',
                    "response_language": response_language,
                    "translation_performed": query_language != 'en' or response_language != 'en'
                }
            }

        except Exception as e:
            logger.error(f"Cross-language research failed: {e}")
            return {
                "success": False,
                "error": f"Cross-language research error: {str(e)}",
                "query": query,
                "query_language": query_language,
                "response_language": response_language
            }

    async def get_language_capabilities(self) -> Dict[str, Any]:
        """
        Get information about supported languages and capabilities.
        """
        capabilities = {
            "supported_languages": self.supported_languages,
            "detection_available": LANGDETECT_AVAILABLE,
            "translation_engines": [],
            "features": {
                "language_detection": LANGDETECT_AVAILABLE,
                "cross_language_research": True,
                "real_time_translation": bool(self.translator),
                "cultural_context_awareness": False,  # TODO: Implement
                "localized_search": True
            }
        }

        if self.translator:
            capabilities["translation_engines"].append("google_translate")

        if OPENAI_AVAILABLE and self.openai_api_key:
            capabilities["translation_engines"].append("openai")

        return capabilities

    def get_language_info(self, language_code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific language.
        """
        return self.supported_languages.get(language_code.lower())

    async def validate_language_support(self, language_code: str) -> Dict[str, Any]:
        """
        Validate if a language is fully supported.
        """
        lang_info = self.get_language_info(language_code)

        if not lang_info:
            return {
                "supported": False,
                "language_code": language_code,
                "reason": "Language not in supported list"
            }

        # Check translation capabilities
        can_translate_from = bool(self.translator) or (OPENAI_AVAILABLE and self.openai_api_key)
        can_translate_to = can_translate_from  # Assume bidirectional for now

        return {
            "supported": True,
            "language_code": language_code,
            "language_info": lang_info,
            "capabilities": {
                "detection": LANGDETECT_AVAILABLE,
                "translation_from": can_translate_from,
                "translation_to": can_translate_to,
                "cross_language_research": True,
                "native_script_support": True
            }
        }

    # Helper methods

    def _heuristic_language_detection(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Simple heuristic-based language detection.
        """
        text_lower = text.lower()

        # Spanish indicators
        spanish_words = ['el', 'la', 'los', 'las', 'que', 'con', 'por', 'para', 'muy', 'más']
        if any(word in text_lower for word in spanish_words):
            spanish_count = sum(1 for word in spanish_words if word in text_lower)
            if spanish_count >= 2:
                return {"language": "es", "confidence": min(0.6, spanish_count * 0.1)}

        # French indicators
        french_words = ['le', 'la', 'les', 'que', 'avec', 'pour', 'dans', 'sur', 'par', 'mais']
        if any(word in text_lower for word in french_words):
            french_count = sum(1 for word in french_words if word in text_lower)
            if french_count >= 2:
                return {"language": "fr", "confidence": min(0.6, french_count * 0.1)}

        # German indicators
        german_words = ['der', 'die', 'das', 'und', 'mit', 'auf', 'für', 'von', 'zu', 'ist']
        if any(word in text_lower for word in german_words):
            german_count = sum(1 for word in german_words if word in text_lower)
            if german_count >= 2:
                return {"language": "de", "confidence": min(0.6, german_count * 0.1)}

        return None

    def _character_based_detection(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Character-based language detection using script analysis.
        """
        # Count character types
        latin_chars = sum(1 for c in text if ord(c) < 128)
        cyrillic_chars = sum(1 for c in text if 1024 <= ord(c) <= 1279)
        arabic_chars = sum(1 for c in text if 1536 <= ord(c) <= 1791)
        han_chars = sum(1 for c in text if 19968 <= ord(c) <= 40959)
        hangul_chars = sum(1 for c in text if 44032 <= ord(c) <= 55203)
        devanagari_chars = sum(1 for c in text if 2304 <= ord(c) <= 2431)

        total_chars = len(text)

        if total_chars == 0:
            return None

        # Determine dominant script
        script_counts = {
            "latin": latin_chars / total_chars,
            "cyrillic": cyrillic_chars / total_chars,
            "arabic": arabic_chars / total_chars,
            "han": han_chars / total_chars,
            "hangul": hangul_chars / total_chars,
            "devanagari": devanagari_chars / total_chars
        }

        dominant_script = max(script_counts, key=script_counts.get)

        if script_counts[dominant_script] > 0.3:  # At least 30% of text in script
            script_to_lang = {
                "cyrillic": ("ru", 0.5),
                "arabic": ("ar", 0.5),
                "han": ("zh", 0.4),
                "hangul": ("ko", 0.6),
                "devanagari": ("hi", 0.6)
            }

            if dominant_script in script_to_lang:
                lang, confidence = script_to_lang[dominant_script]
                return {"language": lang, "confidence": confidence}

        return None

    def _aggregate_detection_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple detection results into a final decision.
        """
        if not results:
            return {
                "success": False,
                "error": "No detection results",
                "detected_language": None,
                "confidence": 0.0
            }

        # Group by language
        lang_votes = {}
        total_confidence = 0

        for result in results:
            lang = result["language"]
            confidence = result["confidence"]

            if lang not in lang_votes:
                lang_votes[lang] = []

            lang_votes[lang].append(confidence)
            total_confidence += confidence

        # Find language with highest average confidence
        best_lang = None
        best_avg_confidence = 0

        for lang, confidences in lang_votes.items():
            avg_confidence = sum(confidences) / len(confidences)
            if avg_confidence > best_avg_confidence:
                best_avg_confidence = avg_confidence
                best_lang = lang

        # Check if confidence meets threshold
        lang_info = self.supported_languages.get(best_lang, {})
        threshold = lang_info.get('confidence_threshold', 0.5)

        if best_avg_confidence >= threshold:
            return {
                "success": True,
                "detected_language": best_lang,
                "confidence": best_avg_confidence,
                "language_info": lang_info,
                "detection_methods": len(results)
            }
        else:
            return {
                "success": False,
                "error": f"Confidence {best_avg_confidence:.2f} below threshold {threshold}",
                "detected_language": best_lang,
                "confidence": best_avg_confidence
            }

    async def _openai_translate(self, text: str, target_lang: str,
                              source_lang: str) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI for translation (for complex or nuanced content).
        """
        try:
            if not OPENAI_AVAILABLE or not self.openai_api_key:
                return None

            # This is a placeholder for OpenAI API call
            # In production, you would use the OpenAI client
            return {
                "text": f"[OpenAI translation placeholder] {text}",
                "confidence": 0.9,
                "method": "openai",
                "detected_source": source_lang
            }

        except Exception as e:
            logger.error(f"OpenAI translation error: {e}")
            return None

    def _select_best_translation(self, translations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best translation from multiple results.
        """
        if not translations:
            return {"text": "", "confidence": 0.0, "method": "none"}

        # For now, prefer Google Translate, then OpenAI
        method_priority = {"google_translate": 3, "openai": 2}

        sorted_translations = sorted(
            translations,
            key=lambda x: (
                method_priority.get(x.get("method", ""), 1),
                x.get("confidence", 0)
            ),
            reverse=True
        )

        return sorted_translations[0]

    async def get_translation_stats(self) -> Dict[str, Any]:
        """
        Get translation usage statistics.
        """
        # This would integrate with analytics
        # For now, return mock data
        stats = {
            "total_translations": 1250,
            "languages_used": {
                "en-es": 340,
                "es-en": 280,
                "en-fr": 195,
                "fr-en": 180,
                "en-de": 155,
                "de-en": 100
            },
            "average_confidence": 0.82,
            "cache_hit_rate": 0.65,
            "generated_at": datetime.utcnow().isoformat()
        }

        return stats
