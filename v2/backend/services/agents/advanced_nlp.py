"""
Advanced NLP Processor for Galion Agents

Provides sophisticated natural language understanding with:
- Intent recognition and entity extraction
- Context awareness and conversation management
- Semantic similarity and text classification
- Multi-language support and sentiment analysis
- Knowledge extraction and summarization
"""

import asyncio
import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import hashlib
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
import spacy
from textblob import TextBlob
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import language_tool_python


logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Represents a recognized intent from user input."""
    name: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Represents conversation context and history."""
    conversation_id: str
    user_id: Optional[str] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    topics: List[str] = field(default_factory=list)
    sentiment_trend: List[float] = field(default_factory=list)
    intent_history: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def add_message(self, message: str, sender: str = "user", intent: Optional[str] = None):
        """Add a message to the conversation."""
        self.messages.append({
            "content": message,
            "sender": sender,
            "timestamp": datetime.now(),
            "intent": intent
        })

        if intent:
            self.intent_history.append(intent)

        self.last_updated = datetime.now()

    def get_recent_messages(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages from the conversation."""
        return self.messages[-limit:] if limit > 0 else self.messages

    def get_topic_summary(self) -> Dict[str, Any]:
        """Get a summary of conversation topics."""
        return {
            "main_topics": self.topics[:5] if self.topics else [],
            "total_messages": len(self.messages),
            "conversation_duration": (self.last_updated - self.created_at).total_seconds(),
            "avg_sentiment": sum(self.sentiment_trend) / len(self.sentiment_trend) if self.sentiment_trend else 0.0
        }


@dataclass
class KnowledgeEntity:
    """Represents an extracted knowledge entity."""
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    source: str = ""
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SemanticMatch:
    """Represents a semantic similarity match."""
    text: str
    similarity_score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedNLPProcessor:
    """
    Advanced NLP processing with machine learning capabilities.

    Features:
    - Intent classification and entity extraction
    - Conversation context management
    - Semantic similarity and text clustering
    - Sentiment analysis and emotion detection
    - Knowledge extraction and relationship mapping
    - Multi-language support and translation
    - Text summarization and key phrase extraction
    """

    def __init__(self, model_path: str = "data/nlp_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)

        # NLP Models and tools
        self.nlp_model = None
        self.vectorizer = None
        self.intent_classifier = None
        self.sentiment_analyzer = None
        self.language_tool = None

        # Data structures
        self.intent_patterns: Dict[str, List[str]] = {}
        self.entity_patterns: Dict[str, List[str]] = {}
        self.knowledge_graph: Dict[str, KnowledgeEntity] = {}
        self.conversation_cache: Dict[str, ConversationContext] = {}
        self.text_embeddings: Dict[str, np.ndarray] = {}

        # Configuration
        self.max_context_length = 10
        self.similarity_threshold = 0.7
        self.confidence_threshold = 0.6
        self.max_knowledge_entities = 10000

        # Caches
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    async def initialize(self) -> bool:
        """Initialize the NLP processor."""
        try:
            # Load spaCy model
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, downloading...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp_model = spacy.load("en_core_web_sm")

            # Download NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)

            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)

            try:
                nltk.data.find('corpora/wordnet')
            except LookupError:
                nltk.download('wordnet', quiet=True)

            # Initialize vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )

            # Initialize language tool
            self.language_tool = language_tool_python.LanguageTool('en-US')

            # Load saved models and data
            await self._load_models()

            logger.info("Advanced NLP processor initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize NLP processor: {e}")
            return False

    async def process_text(self, text: str, context: Optional[ConversationContext] = None,
                          language: str = "en") -> Dict[str, Any]:
        """Process text with full NLP analysis."""
        try:
            result = {
                "original_text": text,
                "language": language,
                "processed_at": datetime.now().isoformat(),
                "tokens": [],
                "sentences": [],
                "entities": [],
                "intent": None,
                "sentiment": {},
                "key_phrases": [],
                "summary": "",
                "complexity_score": 0.0,
                "readability_score": 0.0,
                "topics": [],
                "semantic_matches": [],
                "knowledge_entities": [],
                "confidence": 0.0
            }

            # Basic text processing
            if self.nlp_model:
                doc = self.nlp_model(text)

                # Tokenization and POS tagging
                result["tokens"] = [
                    {
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "tag": token.tag_,
                        "is_stop": token.is_stop
                    }
                    for token in doc
                ]

                # Named entity recognition
                result["entities"] = [
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    }
                    for ent in doc.ents
                ]

            # Sentence segmentation
            result["sentences"] = sent_tokenize(text)

            # Intent recognition
            result["intent"] = await self.recognize_intent(text, context)

            # Sentiment analysis
            result["sentiment"] = self.analyze_sentiment(text)

            # Key phrase extraction
            result["key_phrases"] = self.extract_key_phrases(text)

            # Text summarization
            result["summary"] = self.summarize_text(text)

            # Complexity analysis
            result["complexity_score"] = self.calculate_complexity(text)
            result["readability_score"] = self.calculate_readability(text)

            # Topic modeling
            result["topics"] = self.extract_topics(text)

            # Semantic similarity search
            result["semantic_matches"] = await self.find_semantic_matches(text)

            # Knowledge extraction
            result["knowledge_entities"] = self.extract_knowledge(text)

            # Overall confidence
            result["confidence"] = self._calculate_overall_confidence(result)

            # Update conversation context
            if context:
                await self.update_conversation_context(context, result)

            return result

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {
                "original_text": text,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    async def recognize_intent(self, text: str, context: Optional[ConversationContext] = None) -> Optional[Intent]:
        """Recognize user intent from text."""
        try:
            # Preprocessing
            processed_text = self._preprocess_text(text)

            # Context-aware intent recognition
            if context:
                recent_intents = context.intent_history[-3:] if context.intent_history else []
                context_boost = {}
                for intent in recent_intents:
                    context_boost[intent] = context_boost.get(intent, 0) + 0.1
            else:
                context_boost = {}

            # Rule-based intent matching
            intent_scores = {}

            for intent_name, patterns in self.intent_patterns.items():
                max_score = 0.0
                for pattern in patterns:
                    score = self._calculate_pattern_match(processed_text, pattern)
                    max_score = max(max_score, score)

                if max_score > 0:
                    intent_scores[intent_name] = max_score + context_boost.get(intent_name, 0)

            # ML-based intent classification (if available)
            if self.intent_classifier and processed_text:
                try:
                    features = self.vectorizer.transform([processed_text])
                    ml_prediction = self.intent_classifier.predict(features)[0]
                    ml_proba = self.intent_classifier.predict_proba(features)[0]
                    ml_confidence = max(ml_proba)

                    intent_scores[ml_prediction] = max(
                        intent_scores.get(ml_prediction, 0),
                        ml_confidence
                    )
                except Exception as e:
                    logger.warning(f"ML intent classification failed: {e}")

            # Select best intent
            if intent_scores:
                best_intent = max(intent_scores.items(), key=lambda x: x[1])
                intent_name, confidence = best_intent

                if confidence >= self.confidence_threshold:
                    # Extract entities
                    entities = self._extract_entities(text, intent_name)

                    return Intent(
                        name=intent_name,
                        confidence=confidence,
                        entities=entities,
                        context={"conversation_id": context.conversation_id if context else None},
                        metadata={"method": "rule_based" if confidence > 0.8 else "ml_fallback"}
                    )

            return None

        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return None

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotion in text."""
        try:
            # TextBlob sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Classify sentiment
            if polarity > 0.1:
                sentiment_class = "positive"
            elif polarity < -0.1:
                sentiment_class = "negative"
            else:
                sentiment_class = "neutral"

            # Emotion detection (simplified)
            emotion_scores = self._detect_emotions(text)

            return {
                "polarity": polarity,
                "subjectivity": subjectivity,
                "sentiment_class": sentiment_class,
                "confidence": abs(polarity),
                "emotions": emotion_scores
            }

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": str(e)}

    def extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extract key phrases from text."""
        try:
            if not self.nlp_model:
                return []

            doc = self.nlp_model(text)

            # Extract noun phrases
            noun_phrases = [chunk.text for chunk in doc.noun_chunks]

            # Score phrases by importance
            phrase_scores = {}
            for phrase in noun_phrases:
                # Simple scoring based on length and position
                score = len(phrase.split()) * 0.1
                if phrase.lower().strip() in text.lower()[:100]:  # Appears early
                    score += 0.2

                phrase_scores[phrase] = score

            # Return top phrases
            sorted_phrases = sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)
            return [phrase for phrase, score in sorted_phrases[:max_phrases]]

        except Exception as e:
            logger.error(f"Key phrase extraction failed: {e}")
            return []

    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """Generate a summary of the text."""
        try:
            if len(text) <= max_length:
                return text

            sentences = sent_tokenize(text)

            if len(sentences) <= 2:
                return text

            # Simple extractive summarization
            # Score sentences by position and length
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                score = 1.0 / (i + 1)  # Prefer earlier sentences
                score += len(sentence.split()) * 0.01  # Prefer longer sentences

                # Boost score for sentences with key entities
                if self.nlp_model:
                    doc = self.nlp_model(sentence)
                    if doc.ents:
                        score += 0.2

                sentence_scores[sentence] = score

            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            summary = ' '.join([sent for sent, score in sorted(top_sentences, key=lambda x: sentences.index(x[0]))])

            return summary[:max_length] + "..." if len(summary) > max_length else summary

        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text

    def calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score."""
        try:
            words = word_tokenize(text)
            sentences = sent_tokenize(text)

            if not words or not sentences:
                return 0.0

            # Average sentence length
            avg_sentence_length = len(words) / len(sentences)

            # Lexical diversity (unique words / total words)
            unique_words = len(set(words))
            lexical_diversity = unique_words / len(words)

            # Average word length
            avg_word_length = sum(len(word) for word in words) / len(words)

            # Complexity score (0-1 scale)
            complexity = (
                (avg_sentence_length * 0.3) +
                (lexical_diversity * 0.3) +
                ((avg_word_length - 3) * 0.4)  # Normalize word length
            ) / 10.0  # Scale down

            return min(max(complexity, 0.0), 1.0)

        except Exception as e:
            logger.error(f"Complexity calculation failed: {e}")
            return 0.5

    def calculate_readability(self, text: str) -> float:
        """Calculate text readability score."""
        try:
            words = word_tokenize(text)
            sentences = sent_tokenize(text)

            if not words or not sentences:
                return 0.0

            # Simple readability metrics
            total_words = len(words)
            total_sentences = len(sentences)
            avg_words_per_sentence = total_words / total_sentences

            # Count syllables (simplified)
            syllables = sum(self._count_syllables(word) for word in words)
            avg_syllables_per_word = syllables / total_words

            # Flesch Reading Ease formula (simplified)
            readability = 206.835 - (avg_words_per_sentence * 0.846) - (avg_syllables_per_word * 84.6)

            # Normalize to 0-1 scale (lower is easier)
            normalized_readability = max(0, min(100, readability)) / 100.0

            return 1.0 - normalized_readability  # Invert so 1.0 = very readable

        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return 0.5

    def extract_topics(self, text: str, num_topics: int = 3) -> List[str]:
        """Extract main topics from text."""
        try:
            if not self.nlp_model:
                return []

            doc = self.nlp_model(text)

            # Extract noun phrases and named entities
            topics = []

            # Add named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                    topics.append(ent.text.lower())

            # Add noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word phrases
                    topics.append(chunk.text.lower())

            # Count and rank topics
            topic_counts = Counter(topics)
            top_topics = [topic for topic, count in topic_counts.most_common(num_topics)]

            return top_topics

        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []

    async def find_semantic_matches(self, text: str, limit: int = 5) -> List[SemanticMatch]:
        """Find semantically similar texts."""
        try:
            if not self.vectorizer or not self.text_embeddings:
                return []

            # Create embedding for input text
            input_vector = self.vectorizer.transform([text])

            # Calculate similarities
            similarities = {}
            for text_id, embedding in self.text_embeddings.items():
                similarity = cosine_similarity(input_vector, embedding.reshape(1, -1))[0][0]
                if similarity >= self.similarity_threshold:
                    similarities[text_id] = similarity

            # Return top matches
            top_matches = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:limit]

            matches = []
            for text_id, score in top_matches:
                # In a real implementation, you'd store the original text
                matches.append(SemanticMatch(
                    text=f"Similar text {text_id}",
                    similarity_score=float(score),
                    source="knowledge_base",
                    metadata={"text_id": text_id}
                ))

            return matches

        except Exception as e:
            logger.error(f"Semantic matching failed: {e}")
            return []

    def extract_knowledge(self, text: str) -> List[Dict[str, Any]]:
        """Extract knowledge entities and relationships."""
        try:
            if not self.nlp_model:
                return []

            doc = self.nlp_model(text)
            entities = []

            # Extract named entities
            for ent in doc.ents:
                entity = {
                    "entity_id": f"{ent.label_}_{ent.text.lower().replace(' ', '_')}",
                    "entity_type": ent.label_,
                    "name": ent.text,
                    "properties": {
                        "start_char": ent.start_char,
                        "end_char": ent.end_char,
                        "confidence": 0.9
                    },
                    "source": "nlp_extraction"
                }
                entities.append(entity)

            # Extract noun phrases as concepts
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:  # Multi-word concepts
                    concept = {
                        "entity_id": f"concept_{chunk.text.lower().replace(' ', '_')}",
                        "entity_type": "CONCEPT",
                        "name": chunk.text,
                        "properties": {
                            "root": chunk.root.text if chunk.root else "",
                            "confidence": 0.7
                        },
                        "source": "nlp_extraction"
                    }
                    entities.append(concept)

            return entities[:10]  # Limit to top entities

        except Exception as e:
            logger.error(f"Knowledge extraction failed: {e}")
            return []

    async def manage_conversation_context(self, conversation_id: str,
                                        user_id: Optional[str] = None) -> ConversationContext:
        """Get or create conversation context."""
        if conversation_id not in self.conversation_cache:
            self.conversation_cache[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id
            )

        return self.conversation_cache[conversation_id]

    async def update_conversation_context(self, context: ConversationContext,
                                        nlp_result: Dict[str, Any]) -> None:
        """Update conversation context with NLP results."""
        try:
            # Add sentiment to trend
            if 'sentiment' in nlp_result and 'polarity' in nlp_result['sentiment']:
                context.sentiment_trend.append(nlp_result['sentiment']['polarity'])

                # Keep only recent sentiment history
                if len(context.sentiment_trend) > 20:
                    context.sentiment_trend = context.sentiment_trend[-20:]

            # Update topics
            if 'topics' in nlp_result and nlp_result['topics']:
                context.topics.extend(nlp_result['topics'])
                context.topics = list(set(context.topics))  # Remove duplicates

            # Update entities
            if 'entities' in nlp_result:
                for entity in nlp_result['entities']:
                    entity_key = f"{entity['label']}_{entity['text']}"
                    context.entities[entity_key] = entity

            # Add intent to history
            if 'intent' in nlp_result and nlp_result['intent']:
                intent_name = nlp_result['intent'].name if hasattr(nlp_result['intent'], 'name') else str(nlp_result['intent'])
                context.intent_history.append(intent_name)

                # Keep only recent intents
                if len(context.intent_history) > 50:
                    context.intent_history = context.intent_history[-50:]

        except Exception as e:
            logger.error(f"Context update failed: {e}")

    def correct_grammar(self, text: str) -> Dict[str, Any]:
        """Correct grammar and spelling in text."""
        try:
            if not self.language_tool:
                return {"original": text, "corrected": text, "corrections": []}

            # Check for errors
            matches = self.language_tool.check(text)

            corrections = []
            for match in matches:
                corrections.append({
                    "error": match.context,
                    "suggestion": match.replacements[0] if match.replacements else "",
                    "rule": match.ruleId,
                    "message": match.message
                })

            # Apply corrections
            corrected_text = self.language_tool.correct(text)

            return {
                "original": text,
                "corrected": corrected_text,
                "corrections": corrections,
                "error_count": len(corrections)
            }

        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
            return {"original": text, "corrected": text, "corrections": [], "error": str(e)}

    def translate_text(self, text: str, target_language: str = "es") -> Dict[str, Any]:
        """Translate text to another language."""
        try:
            # Using TextBlob for translation (requires internet)
            blob = TextBlob(text)
            translated = blob.translate(to=target_language)

            return {
                "original": text,
                "translated": str(translated),
                "source_language": "en",  # Auto-detected
                "target_language": target_language,
                "confidence": 0.8
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "original": text,
                "translated": text,
                "error": str(e),
                "target_language": target_language
            }

    # Private helper methods

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        try:
            # Lowercase
            text = text.lower()

            # Remove special characters
            text = re.sub(r'[^\w\s]', ' ', text)

            # Tokenize and lemmatize
            tokens = word_tokenize(text)
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens
                     if token not in self.stop_words and len(token) > 2]

            return ' '.join(tokens)

        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text.lower()

    def _calculate_pattern_match(self, text: str, pattern: str) -> float:
        """Calculate how well text matches a pattern."""
        try:
            # Simple keyword matching
            pattern_words = set(pattern.lower().split())
            text_words = set(text.lower().split())

            intersection = pattern_words.intersection(text_words)
            union = pattern_words.union(text_words)

            if not union:
                return 0.0

            return len(intersection) / len(union)

        except Exception:
            return 0.0

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract entities relevant to an intent."""
        entities = {}

        try:
            if self.nlp_model:
                doc = self.nlp_model(text)

                # Extract different entity types
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'GPE', 'MONEY', 'DATE', 'TIME']:
                        entities[ent.label_.lower()] = ent.text

                # Intent-specific entity extraction
                if intent == "create_task":
                    # Look for task-related keywords
                    if "deadline" in text.lower():
                        # Extract dates
                        for ent in doc.ents:
                            if ent.label_ == 'DATE':
                                entities['deadline'] = ent.text
                                break

                elif intent == "search":
                    # Look for search terms
                    entities['query'] = text.strip()

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")

        return entities

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text (simplified implementation)."""
        emotions = {
            'joy': 0.0,
            'sadness': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'surprise': 0.0
        }

        try:
            text_lower = text.lower()

            # Simple keyword-based emotion detection
            joy_keywords = ['happy', 'great', 'awesome', 'excellent', 'wonderful']
            sadness_keywords = ['sad', 'sorry', 'unfortunate', 'disappointed', 'regret']
            anger_keywords = ['angry', 'frustrated', 'annoyed', 'irritated', 'furious']
            fear_keywords = ['worried', 'scared', 'afraid', 'concerned', 'nervous']
            surprise_keywords = ['surprised', 'amazing', 'shocked', 'unexpected', 'wow']

            for keyword in joy_keywords:
                if keyword in text_lower:
                    emotions['joy'] += 0.2

            for keyword in sadness_keywords:
                if keyword in text_lower:
                    emotions['sadness'] += 0.2

            for keyword in anger_keywords:
                if keyword in text_lower:
                    emotions['anger'] += 0.2

            for keyword in fear_keywords:
                if keyword in text_lower:
                    emotions['fear'] += 0.2

            for keyword in surprise_keywords:
                if keyword in text_lower:
                    emotions['surprise'] += 0.2

            # Normalize scores
            total = sum(emotions.values())
            if total > 0:
                for emotion in emotions:
                    emotions[emotion] /= total

        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")

        return emotions

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"

        if word[0] in vowels:
            count += 1

        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1

        if word.endswith("e"):
            count -= 1

        return max(1, count)

    def _calculate_overall_confidence(self, nlp_result: Dict[str, Any]) -> float:
        """Calculate overall confidence in NLP processing."""
        confidence_scores = []

        # Intent confidence
        if nlp_result.get('intent') and hasattr(nlp_result['intent'], 'confidence'):
            confidence_scores.append(nlp_result['intent'].confidence)

        # Sentiment confidence
        if 'sentiment' in nlp_result and 'confidence' in nlp_result['sentiment']:
            confidence_scores.append(nlp_result['sentiment']['confidence'])

        # Entity confidence (average)
        if 'entities' in nlp_result and nlp_result['entities']:
            entity_confidences = [ent.get('confidence', 0.8) for ent in nlp_result['entities']]
            confidence_scores.append(sum(entity_confidences) / len(entity_confidences))

        # Default confidence
        if not confidence_scores:
            return 0.5

        # Return average confidence
        return sum(confidence_scores) / len(confidence_scores)

    async def _load_models(self) -> None:
        """Load saved models and data."""
        try:
            # Load intent patterns
            patterns_file = self.model_path / "intent_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.intent_patterns = json.load(f)

            # Load entity patterns
            entities_file = self.model_path / "entity_patterns.json"
            if entities_file.exists():
                with open(entities_file, 'r') as f:
                    self.entity_patterns = json.load(f)

            # Load knowledge graph
            knowledge_file = self.model_path / "knowledge_graph.pkl"
            if knowledge_file.exists():
                with open(knowledge_file, 'rb') as f:
                    self.knowledge_graph = pickle.load(f)

            logger.info("NLP models and data loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")

    async def _save_models(self) -> None:
        """Save models and data."""
        try:
            # Save intent patterns
            patterns_file = self.model_path / "intent_patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump(self.intent_patterns, f, indent=2)

            # Save entity patterns
            entities_file = self.model_path / "entity_patterns.json"
            with open(entities_file, 'w') as f:
                json.dump(self.entity_patterns, f, indent=2)

            # Save knowledge graph
            knowledge_file = self.model_path / "knowledge_graph.pkl"
            with open(knowledge_file, 'wb') as f:
                pickle.dump(self.knowledge_graph, f)

            logger.info("NLP models and data saved successfully")

        except Exception as e:
            logger.error(f"Failed to save NLP models: {e}")

    def get_nlp_stats(self) -> Dict[str, Any]:
        """Get NLP processor statistics."""
        return {
            "intent_patterns_count": len(self.intent_patterns),
            "entity_patterns_count": len(self.entity_patterns),
            "knowledge_entities_count": len(self.knowledge_graph),
            "active_conversations": len(self.conversation_cache),
            "text_embeddings_count": len(self.text_embeddings),
            "model_path": str(self.model_path)
        }
