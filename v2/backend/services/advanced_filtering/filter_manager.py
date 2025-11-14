"""
Advanced filtering system for Deep Search results.
Provides sophisticated filtering capabilities for research results.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class FilterType(Enum):
    """Types of filters available."""
    DATE_RANGE = "date_range"
    SOURCE_TYPE = "source_type"
    CREDIBILITY_SCORE = "credibility_score"
    CONTENT_TYPE = "content_type"
    LANGUAGE = "language"
    DOMAIN = "domain"
    TAG = "tag"
    AUTHOR = "author"
    PUBLICATION_DATE = "publication_date"
    ACCESS_LEVEL = "access_level"
    GEOGRAPHIC_REGION = "geographic_region"


class SourceType(Enum):
    """Types of sources that can be filtered."""
    ACADEMIC_PAPER = "academic_paper"
    NEWS_ARTICLE = "news_article"
    BLOG_POST = "blog_post"
    BOOK = "book"
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    VIDEO = "video"
    PODCAST = "podcast"
    GOVERNMENT_DOCUMENT = "government_document"
    RESEARCH_REPORT = "research_report"
    PATENT = "patent"
    CONFERENCE_PROCEEDING = "conference_proceeding"


class ContentType(Enum):
    """Types of content that can be filtered."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DATASET = "dataset"
    CODE = "code"
    PRESENTATION = "presentation"
    INTERACTIVE = "interactive"


class CredibilityLevel(Enum):
    """Credibility levels for sources."""
    VERY_HIGH = "very_high"      # Peer-reviewed academic sources
    HIGH = "high"               # Established news outlets, government sites
    MEDIUM = "medium"           # Blogs, social media from experts
    LOW = "low"                 # Unverified social media, user-generated content
    VERY_LOW = "very_low"       # Potentially unreliable sources


class FilterManager:
    """
    Advanced filtering system for research results.

    Provides sophisticated filtering capabilities including:
    - Date range filtering
    - Source type filtering
    - Credibility score filtering
    - Geographic and domain filtering
    - Multi-criteria filtering with logical operators
    """

    def __init__(self):
        # Default filter configurations
        self.credibility_thresholds = {
            CredibilityLevel.VERY_HIGH: (0.95, 1.0),
            CredibilityLevel.HIGH: (0.80, 0.94),
            CredibilityLevel.MEDIUM: (0.60, 0.79),
            CredibilityLevel.LOW: (0.30, 0.59),
            CredibilityLevel.VERY_LOW: (0.0, 0.29)
        }

        # Trusted domains for automatic credibility scoring
        self.trusted_domains = {
            "nature.com", "science.org", "nejm.org", "thelancet.com",
            "ieee.org", "acm.org", "arxiv.org", "ssrn.com",
            "nytimes.com", "washingtonpost.com", "bbc.com", "reuters.com",
            "gov.uk", "nih.gov", "cdc.gov", "who.int",
            "harvard.edu", "stanford.edu", "mit.edu", "ox.ac.uk"
        }

        # Domain credibility scores
        self.domain_scores = {
            # Academic (.edu, research institutions)
            "edu": 0.90, ".ac.uk": 0.90, ".edu.au": 0.90,
            # Government
            "gov": 0.85, ".gov.uk": 0.85, ".gov.au": 0.85,
            # International organizations
            "org": 0.75, "who.int": 0.90, "un.org": 0.85,
            # News outlets
            "com": 0.60, "co.uk": 0.65,
            # Blogs and social
            "blogspot.com": 0.40, "wordpress.com": 0.45,
            "medium.com": 0.55, "substack.com": 0.50
        }

    def apply_filters(self, sources: List[Dict[str, Any]],
                     filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply advanced filters to a list of sources.

        Args:
            sources: List of source dictionaries
            filters: Dictionary of filter criteria

        Returns:
            Tuple of (filtered_sources, filter_metadata)
        """
        if not sources:
            return [], {"total_sources": 0, "filtered_sources": 0, "filters_applied": []}

        filtered_sources = sources.copy()
        applied_filters = []
        filter_stats = {
            "total_sources": len(sources),
            "filtered_sources": len(sources),
            "filters_applied": []
        }

        # Apply each filter type
        for filter_type, filter_value in filters.items():
            if not filter_value:
                continue

            try:
                if filter_type == FilterType.DATE_RANGE.value:
                    filtered_sources, stats = self._apply_date_range_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.SOURCE_TYPE.value:
                    filtered_sources, stats = self._apply_source_type_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.CREDIBILITY_SCORE.value:
                    filtered_sources, stats = self._apply_credibility_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.CONTENT_TYPE.value:
                    filtered_sources, stats = self._apply_content_type_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.DOMAIN.value:
                    filtered_sources, stats = self._apply_domain_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.TAG.value:
                    filtered_sources, stats = self._apply_tag_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.LANGUAGE.value:
                    filtered_sources, stats = self._apply_language_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.AUTHOR.value:
                    filtered_sources, stats = self._apply_author_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.ACCESS_LEVEL.value:
                    filtered_sources, stats = self._apply_access_level_filter(filtered_sources, filter_value)
                elif filter_type == FilterType.GEOGRAPHIC_REGION.value:
                    filtered_sources, stats = self._apply_geographic_filter(filtered_sources, filter_value)
                else:
                    continue

                applied_filters.append(filter_type)
                filter_stats["filtered_sources"] = len(filtered_sources)

            except Exception as e:
                logger.warning(f"Error applying filter {filter_type}: {e}")
                continue

        filter_stats["filters_applied"] = applied_filters
        filter_stats["reduction_percentage"] = (
            (filter_stats["total_sources"] - filter_stats["filtered_sources"]) /
            max(filter_stats["total_sources"], 1) * 100
        )

        return filtered_sources, filter_stats

    def _apply_date_range_filter(self, sources: List[Dict[str, Any]],
                                date_range: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply date range filtering."""
        date_from = date_range.get("from")
        date_to = date_range.get("to")

        if not date_from and not date_to:
            return sources, {}

        filtered = []
        stats = {"date_filtered": 0, "out_of_range": 0}

        for source in sources:
            source_date = self._extract_source_date(source)

            if source_date:
                if date_from and source_date < date_from:
                    stats["out_of_range"] += 1
                    continue
                if date_to and source_date > date_to:
                    stats["out_of_range"] += 1
                    continue

            filtered.append(source)
            stats["date_filtered"] += 1

        return filtered, stats

    def _apply_source_type_filter(self, sources: List[Dict[str, Any]],
                                 allowed_types: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply source type filtering."""
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]

        filtered = []
        stats = {"type_filtered": 0, "type_rejected": 0}

        for source in sources:
            source_type = self._classify_source_type(source)
            if source_type and source_type.value in allowed_types:
                filtered.append(source)
                stats["type_filtered"] += 1
            else:
                stats["type_rejected"] += 1

        return filtered, stats

    def _apply_credibility_filter(self, sources: List[Dict[str, Any]],
                                 credibility_criteria: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply credibility score filtering."""
        min_score = credibility_criteria.get("min_score", 0.0)
        max_score = credibility_criteria.get("max_score", 1.0)
        levels = credibility_criteria.get("levels", [])

        filtered = []
        stats = {"credibility_filtered": 0, "credibility_rejected": 0}

        for source in sources:
            score = self._calculate_credibility_score(source)

            # Check direct score range
            if not (min_score <= score <= max_score):
                stats["credibility_rejected"] += 1
                continue

            # Check credibility levels
            if levels:
                level = self._get_credibility_level(score)
                if level.value not in levels:
                    stats["credibility_rejected"] += 1
                    continue

            # Add credibility score to source for reference
            source["credibility_score"] = score
            source["credibility_level"] = self._get_credibility_level(score).value

            filtered.append(source)
            stats["credibility_filtered"] += 1

        return filtered, stats

    def _apply_content_type_filter(self, sources: List[Dict[str, Any]],
                                  allowed_types: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply content type filtering."""
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]

        filtered = []
        stats = {"content_filtered": 0, "content_rejected": 0}

        for source in sources:
            content_type = self._classify_content_type(source)
            if content_type and content_type.value in allowed_types:
                filtered.append(source)
                stats["content_filtered"] += 1
            else:
                stats["content_rejected"] += 1

        return filtered, stats

    def _apply_domain_filter(self, sources: List[Dict[str, Any]],
                            domain_criteria: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply domain-based filtering."""
        allowed_domains = domain_criteria.get("allowed", [])
        blocked_domains = domain_criteria.get("blocked", [])

        if not isinstance(allowed_domains, list):
            allowed_domains = [allowed_domains] if allowed_domains else []
        if not isinstance(blocked_domains, list):
            blocked_domains = [blocked_domains] if blocked_domains else []

        filtered = []
        stats = {"domain_filtered": 0, "domain_blocked": 0}

        for source in sources:
            domain = self._extract_domain(source)

            if domain:
                # Check blocked domains first
                if any(blocked in domain for blocked in blocked_domains):
                    stats["domain_blocked"] += 1
                    continue

                # Check allowed domains
                if allowed_domains and not any(allowed in domain for allowed in allowed_domains):
                    stats["domain_blocked"] += 1
                    continue

            filtered.append(source)
            stats["domain_filtered"] += 1

        return filtered, stats

    def _apply_tag_filter(self, sources: List[Dict[str, Any]],
                         tag_criteria: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply tag-based filtering."""
        required_tags = tag_criteria.get("required", [])
        any_tags = tag_criteria.get("any", [])
        excluded_tags = tag_criteria.get("excluded", [])

        if not isinstance(required_tags, list):
            required_tags = [required_tags] if required_tags else []
        if not isinstance(any_tags, list):
            any_tags = [any_tags] if any_tags else []
        if not isinstance(excluded_tags, list):
            excluded_tags = [excluded_tags] if excluded_tags else []

        filtered = []
        stats = {"tag_filtered": 0, "tag_rejected": 0}

        for source in sources:
            source_tags = set(source.get("tags", []))

            # Check excluded tags
            if excluded_tags and source_tags.intersection(set(excluded_tags)):
                stats["tag_rejected"] += 1
                continue

            # Check required tags (all must be present)
            if required_tags and not set(required_tags).issubset(source_tags):
                stats["tag_rejected"] += 1
                continue

            # Check any tags (at least one must be present)
            if any_tags and not source_tags.intersection(set(any_tags)):
                stats["tag_rejected"] += 1
                continue

            filtered.append(source)
            stats["tag_filtered"] += 1

        return filtered, stats

    def _apply_language_filter(self, sources: List[Dict[str, Any]],
                              allowed_languages: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply language-based filtering."""
        if not isinstance(allowed_languages, list):
            allowed_languages = [allowed_languages]

        filtered = []
        stats = {"language_filtered": 0, "language_rejected": 0}

        for source in sources:
            language = source.get("language", "en")  # Default to English

            if language in allowed_languages:
                filtered.append(source)
                stats["language_filtered"] += 1
            else:
                stats["language_rejected"] += 1

        return filtered, stats

    def _apply_author_filter(self, sources: List[Dict[str, Any]],
                            author_criteria: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply author-based filtering."""
        allowed_authors = author_criteria.get("allowed", [])
        blocked_authors = author_criteria.get("blocked", [])

        if not isinstance(allowed_authors, list):
            allowed_authors = [allowed_authors] if allowed_authors else []
        if not isinstance(blocked_authors, list):
            blocked_authors = [blocked_authors] if blocked_authors else []

        filtered = []
        stats = {"author_filtered": 0, "author_blocked": 0}

        for source in sources:
            authors = source.get("authors", [])
            if isinstance(authors, str):
                authors = [authors]

            author_names = [author.lower() for author in authors]

            # Check blocked authors
            if any(any(blocked.lower() in name for name in author_names) for blocked in blocked_authors):
                stats["author_blocked"] += 1
                continue

            # Check allowed authors
            if allowed_authors and not any(any(allowed.lower() in name for name in author_names) for allowed in allowed_authors):
                stats["author_blocked"] += 1
                continue

            filtered.append(source)
            stats["author_filtered"] += 1

        return filtered, stats

    def _apply_access_level_filter(self, sources: List[Dict[str, Any]],
                                  access_levels: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply access level filtering (free, premium, subscription, etc.)."""
        if not isinstance(access_levels, list):
            access_levels = [access_levels]

        filtered = []
        stats = {"access_filtered": 0, "access_restricted": 0}

        for source in sources:
            access_level = source.get("access_level", "free")

            if access_level in access_levels:
                filtered.append(source)
                stats["access_filtered"] += 1
            else:
                stats["access_restricted"] += 1

        return filtered, stats

    def _apply_geographic_filter(self, sources: List[Dict[str, Any]],
                                regions: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply geographic region filtering."""
        if not isinstance(regions, list):
            regions = [regions]

        filtered = []
        stats = {"region_filtered": 0, "region_excluded": 0}

        for source in sources:
            region = source.get("region", source.get("country", "global"))

            if region in regions or "global" in regions:
                filtered.append(source)
                stats["region_filtered"] += 1
            else:
                stats["region_excluded"] += 1

        return filtered, stats

    # Helper methods for source analysis

    def _extract_source_date(self, source: Dict[str, Any]) -> Optional[datetime]:
        """Extract publication date from source."""
        date_fields = ["published_at", "publication_date", "created_at", "date"]

        for field in date_fields:
            date_value = source.get(field)
            if date_value:
                if isinstance(date_value, str):
                    try:
                        return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                elif isinstance(date_value, datetime):
                    return date_value

        return None

    def _classify_source_type(self, source: Dict[str, Any]) -> Optional[SourceType]:
        """Classify the type of source."""
        url = source.get("url", "").lower()
        title = source.get("title", "").lower()
        content_type = source.get("content_type", "")

        # Check URL patterns
        if ".pdf" in url and ("paper" in title or "journal" in title):
            return SourceType.ACADEMIC_PAPER
        elif any(domain in url for domain in ["arxiv.org", "ssrn.com", "researchgate.net"]):
            return SourceType.ACADEMIC_PAPER
        elif any(domain in url for domain in ["nytimes.com", "bbc.com", "reuters.com", "apnews.com"]):
            return SourceType.NEWS_ARTICLE
        elif any(domain in url for domain in ["medium.com", "substack.com", "blogspot.com"]):
            return SourceType.BLOG_POST
        elif any(domain in url for domain in ["youtube.com", "vimeo.com", "twitch.tv"]):
            return SourceType.VIDEO
        elif any(domain in url for domain in ["spotify.com", "soundcloud.com"]):
            return SourceType.PODCAST

        # Check content type
        if content_type:
            if "video" in content_type:
                return SourceType.VIDEO
            elif "audio" in content_type:
                return SourceType.PODCAST

        # Default to website
        return SourceType.WEBSITE

    def _classify_content_type(self, source: Dict[str, Any]) -> Optional[ContentType]:
        """Classify the type of content."""
        content = source.get("content", "")
        url = source.get("url", "").lower()
        content_type = source.get("content_type", "")

        if content_type:
            if "image" in content_type:
                return ContentType.IMAGE
            elif "video" in content_type:
                return ContentType.VIDEO
            elif "audio" in content_type:
                return ContentType.AUDIO

        if url.endswith(('.jpg', '.png', '.gif', '.svg')):
            return ContentType.IMAGE
        elif url.endswith(('.mp4', '.avi', '.mov')):
            return ContentType.VIDEO
        elif url.endswith(('.mp3', '.wav', '.aac')):
            return ContentType.AUDIO
        elif url.endswith(('.py', '.js', '.java', '.cpp')):
            return ContentType.CODE
        elif url.endswith(('.pdf', '.ppt', '.pptx')):
            return ContentType.PRESENTATION

        return ContentType.TEXT

    def _calculate_credibility_score(self, source: Dict[str, Any]) -> float:
        """Calculate credibility score for a source."""
        score = 0.5  # Base score

        # Domain credibility
        domain = self._extract_domain(source)
        if domain:
            # Check trusted domains
            if domain in self.trusted_domains:
                score += 0.3
            else:
                # Check domain suffixes
                for suffix, domain_score in self.domain_scores.items():
                    if domain.endswith(suffix):
                        score += domain_score * 0.5
                        break

        # Source type credibility
        source_type = self._classify_source_type(source)
        if source_type:
            type_scores = {
                SourceType.ACADEMIC_PAPER: 0.9,
                SourceType.GOVERNMENT_DOCUMENT: 0.85,
                SourceType.RESEARCH_REPORT: 0.8,
                SourceType.NEWS_ARTICLE: 0.7,
                SourceType.BOOK: 0.75,
                SourceType.CONFERENCE_PROCEEDING: 0.8,
                SourceType.PATENT: 0.7,
                SourceType.BLOG_POST: 0.5,
                SourceType.WEBSITE: 0.4,
                SourceType.SOCIAL_MEDIA: 0.2,
                SourceType.VIDEO: 0.3,
                SourceType.PODCAST: 0.4
            }
            score += type_scores.get(source_type, 0.0) * 0.3

        # Author credibility (simplified)
        authors = source.get("authors", [])
        if authors:
            score += 0.1  # Having authors is a positive signal

        # Recency bonus (newer sources tend to be more reliable)
        pub_date = self._extract_source_date(source)
        if pub_date:
            days_old = (datetime.utcnow() - pub_date).days
            if days_old < 30:
                score += 0.05
            elif days_old < 365:
                score += 0.02

        return min(max(score, 0.0), 1.0)

    def _get_credibility_level(self, score: float) -> CredibilityLevel:
        """Get credibility level from score."""
        for level, (min_score, max_score) in self.credibility_thresholds.items():
            if min_score <= score <= max_score:
                return level
        return CredibilityLevel.LOW

    def _extract_domain(self, source: Dict[str, Any]) -> Optional[str]:
        """Extract domain from source URL."""
        url = source.get("url", "")
        if not url:
            return None

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None

    def create_filter_preset(self, name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reusable filter preset."""
        return {
            "name": name,
            "filters": filters,
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0
        }

    def get_common_filters(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get commonly used filter combinations."""
        return {
            "academic_only": [
                {FilterType.SOURCE_TYPE.value: [SourceType.ACADEMIC_PAPER.value]},
                {FilterType.CREDIBILITY_SCORE.value: {"levels": [CredibilityLevel.VERY_HIGH.value, CredibilityLevel.HIGH.value]}}
            ],
            "recent_news": [
                {FilterType.SOURCE_TYPE.value: [SourceType.NEWS_ARTICLE.value]},
                {FilterType.DATE_RANGE.value: {"from": (datetime.utcnow() - timedelta(days=7)).isoformat()}},
                {FilterType.CREDIBILITY_SCORE.value: {"min_score": 0.6}}
            ],
            "technical_resources": [
                {FilterType.CONTENT_TYPE.value: [ContentType.CODE.value, ContentType.PRESENTATION.value]},
                {FilterType.CREDIBILITY_SCORE.value: {"min_score": 0.5}}
            ],
            "high_credibility": [
                {FilterType.CREDIBILITY_SCORE.value: {"levels": [CredibilityLevel.VERY_HIGH.value, CredibilityLevel.HIGH.value]}}
            ]
        }
