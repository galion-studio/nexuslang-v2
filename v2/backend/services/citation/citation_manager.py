"""
Citation management system for Deep Search.
Provides academic-style citation generation and bibliography management.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)


class CitationManager:
    """
    Comprehensive citation management system.

    Supports multiple citation styles (APA, MLA, Chicago, IEEE, etc.)
    with automatic citation generation and bibliography management.
    """

    def __init__(self):
        # Supported citation styles
        self.citation_styles = {
            'apa': {
                'name': 'APA 7th Edition',
                'description': 'American Psychological Association',
                'in_text_template': '({author}, {year})',
                'reference_template': '{author}. ({year}). {title}. {source}',
                'features': ['parenthetical', 'narrative', 'page_numbers']
            },
            'mla': {
                'name': 'MLA 9th Edition',
                'description': 'Modern Language Association',
                'in_text_template': '({author} {page})',
                'reference_template': '{author}. "{title}." {container}, {publisher}, {year}, {pages}.',
                'features': ['author_page', 'works_cited']
            },
            'chicago': {
                'name': 'Chicago 17th Edition',
                'description': 'Chicago Manual of Style',
                'in_text_template': '({author} {year}, {page})',
                'reference_template': '{author}. "{title}." {source} {year}.',
                'features': ['notes_bibliography', 'author_date']
            },
            'ieee': {
                'name': 'IEEE',
                'description': 'Institute of Electrical and Electronics Engineers',
                'in_text_template': '[{number}]',
                'reference_template': '[{number}] {author}, "{title}," {source}, {year}.',
                'features': ['numbered', 'technical']
            },
            'harvard': {
                'name': 'Harvard',
                'description': 'Harvard referencing style',
                'in_text_template': '({author} {year})',
                'reference_template': '{author} ({year}) {title}. {source}.',
                'features': ['parenthetical', 'alphabetical']
            },
            'vancouver': {
                'name': 'Vancouver',
                'description': 'Vancouver referencing style',
                'in_text_template': '({number})',
                'reference_template': '{number}. {author}. {title}. {source}. {year}.',
                'features': ['numbered', 'medical']
            }
        }

        # Source type mappings for different citation styles
        self.source_type_mappings = {
            'book': {
                'apa': '{author}. ({year}). {title}. {publisher}.',
                'mla': '{author}. {title}. {publisher}, {year}.',
                'chicago': '{author}. {title}. {publisher}, {year}.',
                'ieee': '{author}, "{title}," {publisher}, {year}.',
                'harvard': '{author} ({year}) {title}. {publisher}.',
                'vancouver': '{author}. {title}. {publisher}; {year}.'
            },
            'journal_article': {
                'apa': '{author}. ({year}). {title}. {journal}, {volume}({issue}), {pages}. {doi}',
                'mla': '{author}. "{title}." {journal}, vol. {volume}, no. {issue}, {year}, pp. {pages}.',
                'chicago': '{author}. "{title}." {journal} {volume}, no. {issue} ({year}): {pages}.',
                'ieee': '{author}, "{title}," {journal}, vol. {volume}, no. {issue}, pp. {pages}, {year}.',
                'harvard': '{author} ({year}) \'{title}\'. {journal}, {volume}({issue}), pp.{pages}.',
                'vancouver': '{author}. {title}. {journal}. {year};{volume}({issue}):{pages}.'
            },
            'website': {
                'apa': '{author}. ({year}). {title}. {website}. {url}',
                'mla': '{author}. "{title}." {website}, {publisher}, {year}, {url}.',
                'chicago': '{author}. "{title}." {website}. {publisher}. {year}. {url}.',
                'ieee': '{author}, "{title}," {website}, {year}. [Online]. Available: {url}',
                'harvard': '{author} ({year}) {title}. Available at: {url} (Accessed: {access_date}).',
                'vancouver': '{author}. {title} [Internet]. {publisher}; {year} [cited {access_date}]. Available from: {url}'
            },
            'conference_paper': {
                'apa': '{author}. ({year}). {title}. In {editors} (Eds.), {conference} (pp. {pages}). {publisher}.',
                'mla': '{author}. "{title}." {conference}, {location}, {year}, pp. {pages}.',
                'chicago': '{author}. "{title}." Paper presented at {conference}, {location}, {year}.',
                'ieee': '{author}, "{title}," in {conference}, {year}, pp. {pages}.',
                'harvard': '{author} ({year}) \'{title}\'. Paper presented at: {conference}, {location}.',
                'vancouver': '{author}. {title}. {conference}; {year} {location}.'
            }
        }

        # Citation cache for performance
        self.citation_cache = {}
        self.cache_ttl = 3600  # 1 hour

    async def generate_citation(self, source_data: Dict[str, Any],
                               style: str = 'apa',
                               citation_type: str = 'reference') -> Dict[str, Any]:
        """
        Generate a citation for a source.

        Args:
            source_data: Source information
            style: Citation style (apa, mla, chicago, etc.)
            citation_type: Type of citation (reference, in_text, footnote)

        Returns:
            Generated citation
        """
        try:
            # Validate inputs
            if style not in self.citation_styles:
                return {
                    "success": False,
                    "error": f"Unsupported citation style: {style}"
                }

            # Check cache
            cache_key = self._generate_cache_key(source_data, style, citation_type)
            if cache_key in self.citation_cache:
                cached_result = self.citation_cache[cache_key]
                if (datetime.utcnow().timestamp() - cached_result["timestamp"]) < self.cache_ttl:
                    return cached_result["result"]

            # Normalize source data
            normalized_source = self._normalize_source_data(source_data)

            # Determine source type
            source_type = self._classify_source_type(normalized_source)

            # Generate citation based on type and style
            if citation_type == 'reference':
                citation_text = self._generate_reference_citation(normalized_source, style, source_type)
            elif citation_type == 'in_text':
                citation_text = self._generate_in_text_citation(normalized_source, style)
            elif citation_type == 'footnote':
                citation_text = self._generate_footnote_citation(normalized_source, style)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported citation type: {citation_type}"
                }

            result = {
                "success": True,
                "citation": citation_text,
                "style": style,
                "citation_type": citation_type,
                "source_type": source_type,
                "normalized_source": normalized_source
            }

            # Cache result
            self.citation_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.utcnow().timestamp()
            }

            return result

        except Exception as e:
            logger.error(f"Citation generation failed: {e}")
            return {
                "success": False,
                "error": f"Citation generation error: {str(e)}"
            }

    async def generate_bibliography(self, sources: List[Dict[str, Any]],
                                   style: str = 'apa',
                                   sort_by: str = 'author') -> Dict[str, Any]:
        """
        Generate a bibliography from multiple sources.

        Args:
            sources: List of source data
            style: Citation style
            sort_by: Sort method (author, title, date, source_type)

        Returns:
            Formatted bibliography
        """
        try:
            if style not in self.citation_styles:
                return {
                    "success": False,
                    "error": f"Unsupported citation style: {style}"
                }

            citations = []
            errors = []

            # Generate citations for each source
            for i, source in enumerate(sources):
                try:
                    citation_result = await self.generate_citation(source, style, 'reference')
                    if citation_result["success"]:
                        citations.append({
                            "index": i,
                            "citation": citation_result["citation"],
                            "source_data": citation_result["normalized_source"]
                        })
                    else:
                        errors.append(f"Source {i}: {citation_result.get('error', 'Unknown error')}")
                except Exception as e:
                    errors.append(f"Source {i}: {str(e)}")

            # Sort citations
            sorted_citations = self._sort_citations(citations, sort_by)

            # Format bibliography
            bibliography = self._format_bibliography(sorted_citations, style)

            return {
                "success": True,
                "bibliography": bibliography,
                "total_sources": len(sources),
                "successful_citations": len(citations),
                "errors": errors,
                "style": style,
                "sort_method": sort_by
            }

        except Exception as e:
            logger.error(f"Bibliography generation failed: {e}")
            return {
                "success": False,
                "error": f"Bibliography generation error: {str(e)}"
            }

    async def validate_citation(self, citation_text: str, style: str) -> Dict[str, Any]:
        """
        Validate a citation for correctness.

        Args:
            citation_text: Citation to validate
            style: Citation style

        Returns:
            Validation results
        """
        try:
            if style not in self.citation_styles:
                return {
                    "valid": False,
                    "error": f"Unsupported citation style: {style}"
                }

            # Basic validation checks
            validation_results = {
                "valid": True,
                "checks": [],
                "warnings": [],
                "errors": []
            }

            # Check for required elements based on style
            style_rules = self.citation_styles[style]

            # Basic format checks
            if style in ['apa', 'harvard']:
                # Check for parentheses with year
                if not re.search(r'\(\d{4}\)', citation_text):
                    validation_results["warnings"].append("Citation may be missing publication year")
                    validation_results["checks"].append({"check": "year_format", "passed": False})

            if style == 'mla':
                # Check for page numbers
                if not re.search(r'\d+', citation_text):
                    validation_results["warnings"].append("MLA citations typically include page numbers")
                    validation_results["checks"].append({"check": "page_numbers", "passed": False})

            if style == 'ieee':
                # Check for bracketed numbers
                if not re.search(r'\[\d+\]', citation_text):
                    validation_results["errors"].append("IEEE citations require bracketed reference numbers")
                    validation_results["valid"] = False
                    validation_results["checks"].append({"check": "bracketed_numbers", "passed": False})

            # Check for complete sentences
            if not citation_text.endswith('.'):
                validation_results["warnings"].append("Citation should end with a period")

            # Check for proper capitalization
            if citation_text.isupper() or citation_text.islower():
                validation_results["warnings"].append("Citation may have incorrect capitalization")

            validation_results["checks"].append({
                "check": "basic_format",
                "passed": len(validation_results["errors"]) == 0
            })

            return validation_results

        except Exception as e:
            logger.error(f"Citation validation failed: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    async def extract_citation_metadata(self, citation_text: str,
                                       style: str) -> Dict[str, Any]:
        """
        Extract metadata from a formatted citation.

        Args:
            citation_text: Formatted citation
            style: Citation style

        Returns:
            Extracted metadata
        """
        try:
            metadata = {
                "authors": [],
                "title": "",
                "year": "",
                "source": "",
                "pages": "",
                "doi": "",
                "url": ""
            }

            # Style-specific extraction patterns
            if style == 'apa':
                # Extract year from parentheses
                year_match = re.search(r'\((\d{4})\)', citation_text)
                if year_match:
                    metadata["year"] = year_match.group(1)

                # Extract DOI
                doi_match = re.search(r'https?://doi\.org/([^\s]+)', citation_text)
                if doi_match:
                    metadata["doi"] = doi_match.group(1)

            elif style == 'mla':
                # Extract page numbers
                page_match = re.search(r'(\d+(?:-\d+)?)', citation_text)
                if page_match:
                    metadata["pages"] = page_match.group(1)

            elif style == 'ieee':
                # Extract reference number
                ref_match = re.search(r'\[(\d+)\]', citation_text)
                if ref_match:
                    metadata["reference_number"] = ref_match.group(1)

            # Common extractions
            # Extract URLs
            url_match = re.search(r'https?://[^\s]+', citation_text)
            if url_match:
                metadata["url"] = url_match.group(0)

            # Try to extract title (usually in quotes)
            title_match = re.search(r'"([^"]*)"', citation_text)
            if title_match:
                metadata["title"] = title_match.group(1)

            return {
                "success": True,
                "metadata": metadata,
                "confidence": 0.7  # Placeholder confidence score
            }

        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {
                "success": False,
                "error": f"Metadata extraction error: {str(e)}"
            }

    def get_supported_styles(self) -> Dict[str, Any]:
        """
        Get information about supported citation styles.

        Returns:
            Supported citation styles with metadata
        """
        return {
            "styles": self.citation_styles,
            "total_styles": len(self.citation_styles),
            "features": {
                "in_text_citations": True,
                "reference_lists": True,
                "footnotes": True,
                "endnotes": True,
                "bibliographies": True,
                "validation": True,
                "metadata_extraction": True
            }
        }

    def get_style_guide(self, style: str) -> Dict[str, Any]:
        """
        Get detailed style guide for a citation style.

        Args:
            style: Citation style

        Returns:
            Style guide information
        """
        if style not in self.citation_styles:
            return {"error": f"Style '{style}' not supported"}

        style_info = self.citation_styles[style]

        # Create comprehensive style guide
        guide = {
            "style": style,
            "name": style_info["name"],
            "description": style_info["description"],
            "in_text_examples": self._get_style_examples(style, "in_text"),
            "reference_examples": self._get_style_examples(style, "reference"),
            "rules": self._get_style_rules(style),
            "source_types": list(self.source_type_mappings.keys()),
            "features": style_info["features"]
        }

        return guide

    # Helper methods

    def _normalize_source_data(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize source data to standard format."""
        normalized = {
            "authors": source_data.get("authors", []),
            "title": source_data.get("title", ""),
            "year": source_data.get("year", source_data.get("publication_year", "")),
            "publisher": source_data.get("publisher", ""),
            "journal": source_data.get("journal", ""),
            "volume": source_data.get("volume", ""),
            "issue": source_data.get("issue", ""),
            "pages": source_data.get("pages", ""),
            "doi": source_data.get("doi", ""),
            "url": source_data.get("url", ""),
            "access_date": source_data.get("access_date", ""),
            "edition": source_data.get("edition", ""),
            "editors": source_data.get("editors", []),
            "conference": source_data.get("conference", ""),
            "location": source_data.get("location", ""),
            "isbn": source_data.get("isbn", ""),
            "issn": source_data.get("issn", "")
        }

        # Ensure authors is a list
        if isinstance(normalized["authors"], str):
            normalized["authors"] = [normalized["authors"]]

        # Normalize author names
        normalized["authors"] = [self._normalize_author_name(author) for author in normalized["authors"]]

        return normalized

    def _normalize_author_name(self, author: str) -> str:
        """Normalize author name to standard format."""
        # Handle "Last, First" format
        if ',' in author:
            parts = author.split(',', 1)
            return f"{parts[0].strip()}, {parts[1].strip()}"

        # Handle "First Last" format
        parts = author.strip().split()
        if len(parts) >= 2:
            return f"{parts[-1]}, {' '.join(parts[:-1])}"

        return author.strip()

    def _classify_source_type(self, source: Dict[str, Any]) -> str:
        """Classify the type of source."""
        if source.get("journal"):
            return "journal_article"
        elif source.get("conference"):
            return "conference_paper"
        elif source.get("url") and not source.get("publisher"):
            return "website"
        else:
            return "book"

    def _generate_reference_citation(self, source: Dict[str, Any],
                                    style: str, source_type: str) -> str:
        """Generate a reference citation."""
        # Get template for source type and style
        template = self.source_type_mappings.get(source_type, {}).get(style)

        if not template:
            # Fallback to generic template
            template = "{author}. ({year}). {title}. {source}."

        # Format author list
        author_str = self._format_author_list(source["authors"], style)

        # Replace template variables
        citation = template
        citation = citation.replace("{author}", author_str)
        citation = citation.replace("{title}", source["title"])
        citation = citation.replace("{year}", str(source["year"]))
        citation = citation.replace("{publisher}", source["publisher"])
        citation = citation.replace("{journal}", source["journal"])
        citation = citation.replace("{volume}", str(source["volume"]))
        citation = citation.replace("{issue}", str(source["issue"]))
        citation = citation.replace("{pages}", source["pages"])
        citation = citation.replace("{doi}", source["doi"])
        citation = citation.replace("{url}", source["url"])
        citation = citation.replace("{editors}", self._format_author_list(source["editors"], style))
        citation = citation.replace("{conference}", source["conference"])
        citation = citation.replace("{location}", source["location"])
        citation = citation.replace("{access_date}", source["access_date"])
        citation = citation.replace("{source}", self._determine_source_string(source))

        return citation

    def _generate_in_text_citation(self, source: Dict[str, Any], style: str) -> str:
        """Generate an in-text citation."""
        style_info = self.citation_styles[style]

        if style == 'apa':
            author = self._get_primary_author(source["authors"])
            return f"({author}, {source['year']})"
        elif style == 'mla':
            author = self._get_primary_author(source["authors"])
            return f"({author} {source['pages']})"
        elif style == 'chicago':
            author = self._get_primary_author(source["authors"])
            return f"({author} {source['year']}, {source['pages']})"
        elif style == 'ieee':
            # IEEE uses numbered references, would need reference number
            return "[1]"  # Placeholder
        else:
            author = self._get_primary_author(source["authors"])
            return f"({author} {source['year']})"

    def _generate_footnote_citation(self, source: Dict[str, Any], style: str) -> str:
        """Generate a footnote citation."""
        # Simplified footnote generation
        author = self._get_primary_author(source["authors"])
        title = source["title"][:50] + "..." if len(source["title"]) > 50 else source["title"]

        if style in ['chicago', 'mla']:
            return f"{author}, {title}, {source['publisher']}, {source['year']}."
        else:
            return f"{author}, '{title}', {source['year']}."

    def _format_author_list(self, authors: List[str], style: str) -> str:
        """Format a list of authors according to style."""
        if not authors:
            return "Anonymous"

        if len(authors) == 1:
            return self._format_single_author(authors[0], style)
        elif len(authors) == 2:
            author1 = self._format_single_author(authors[0], style)
            author2 = self._format_single_author(authors[1], style)
            if style == 'apa':
                return f"{author1} & {author2}"
            else:
                return f"{author1} and {author2}"
        else:
            # Three or more authors
            if style == 'apa':
                author1 = self._format_single_author(authors[0], style)
                return f"{author1} et al."
            elif style == 'mla':
                author1 = self._format_single_author(authors[0], style)
                return f"{author1} et al."
            else:
                # List all authors
                formatted_authors = [self._format_single_author(author, style) for author in authors]
                return ", ".join(formatted_authors[:-1]) + f", and {formatted_authors[-1]}"

    def _format_single_author(self, author: str, style: str) -> str:
        """Format a single author name."""
        if ',' in author:
            # Already in "Last, First" format
            return author

        # Convert "First Last" to appropriate format
        if style == 'apa':
            return author  # APA uses "Last, First" but we keep as-is for simplicity
        elif style == 'mla':
            return author  # MLA uses "Last, First" but we keep as-is
        else:
            return author

    def _get_primary_author(self, authors: List[str]) -> str:
        """Get the primary author for in-text citations."""
        if not authors:
            return "Anonymous"

        author = authors[0]
        if ',' in author:
            # Take last name only
            return author.split(',')[0].strip()
        else:
            # Take last word as last name
            return author.split()[-1]

    def _determine_source_string(self, source: Dict[str, Any]) -> str:
        """Determine the source string for citations."""
        if source.get("journal"):
            return source["journal"]
        elif source.get("publisher"):
            return source["publisher"]
        elif source.get("url"):
            return source["url"]
        else:
            return "Unknown source"

    def _sort_citations(self, citations: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort citations according to specified method."""
        if sort_by == 'author':
            return sorted(citations, key=lambda x: self._get_sort_key_author(x))
        elif sort_by == 'title':
            return sorted(citations, key=lambda x: x["source_data"]["title"].lower())
        elif sort_by == 'date':
            return sorted(citations, key=lambda x: x["source_data"]["year"], reverse=True)
        elif sort_by == 'source_type':
            return sorted(citations, key=lambda x: x["source_data"].get("journal", x["source_data"].get("publisher", "")))
        else:
            return citations  # No sorting

    def _get_sort_key_author(self, citation: Dict[str, Any]) -> str:
        """Get sort key for author-based sorting."""
        authors = citation["source_data"]["authors"]
        if authors:
            author = authors[0]
            if ',' in author:
                return author.lower()
            else:
                return author.split()[-1].lower()
        return "zzzz"  # Sort anonymous authors last

    def _format_bibliography(self, citations: List[Dict[str, Any]], style: str) -> Dict[str, Any]:
        """Format citations into a bibliography."""
        formatted_entries = []

        for i, citation in enumerate(citations, 1):
            entry = {
                "number": i,
                "citation": citation["citation"],
                "source_data": citation["source_data"]
            }
            formatted_entries.append(entry)

        return {
            "title": self._get_bibliography_title(style),
            "entries": formatted_entries,
            "total_entries": len(formatted_entries),
            "style": style
        }

    def _get_bibliography_title(self, style: str) -> str:
        """Get the appropriate title for bibliography."""
        if style == 'mla':
            return "Works Cited"
        elif style == 'apa':
            return "References"
        elif style == 'chicago':
            return "Bibliography"
        elif style == 'ieee':
            return "References"
        else:
            return "Bibliography"

    def _generate_cache_key(self, source_data: Dict[str, Any],
                           style: str, citation_type: str) -> str:
        """Generate cache key for citation caching."""
        # Create a deterministic key from source data
        key_data = {
            "authors": source_data.get("authors", []),
            "title": source_data.get("title", ""),
            "year": source_data.get("year", ""),
            "style": style,
            "citation_type": citation_type
        }
        return str(hash(json.dumps(key_data, sort_keys=True)))

    def _get_style_examples(self, style: str, citation_type: str) -> List[str]:
        """Get example citations for a style."""
        examples = {
            'apa': {
                'in_text': ['(Smith, 2020)', '(Johnson & Brown, 2019)', '(Taylor et al., 2021)'],
                'reference': [
                    'Smith, J. (2020). The art of research. Academic Press.',
                    'Johnson, A., & Brown, B. (2019). Modern methodologies. Journal of Research, 45(2), 123-145.',
                    'Taylor, R., Wilson, M., & Davis, K. (2021). Future trends. Conference Proceedings, 78-92.'
                ]
            },
            'mla': {
                'in_text': ['(Smith 45)', '(Johnson and Brown 23)', '(Taylor et al. 78)'],
                'reference': [
                    'Smith, John. The Art of Research. Academic Press, 2020.',
                    'Johnson, Alice, and Bob Brown. "Modern Methodologies." Journal of Research, vol. 45, no. 2, 2019, pp. 123-145.',
                    'Taylor, Robert, et al. "Future Trends." Conference Proceedings, 2021, pp. 78-92.'
                ]
            }
        }

        return examples.get(style, {}).get(citation_type, [])

    def _get_style_rules(self, style: str) -> Dict[str, Any]:
        """Get formatting rules for a citation style."""
        rules = {
            'apa': {
                'author_format': 'Last, First Initial.',
                'date_format': 'Year in parentheses',
                'title_case': 'Sentence case',
                'italics': 'Book titles, journal names',
                'doi': 'Include DOI when available'
            },
            'mla': {
                'author_format': 'Last, First',
                'date_format': 'Year at end',
                'title_case': 'Title case for articles',
                'italics': 'Book titles, journal names',
                'pages': 'Include page numbers'
            },
            'chicago': {
                'author_format': 'First Last',
                'date_format': 'Year after author',
                'title_case': 'Title case',
                'italics': 'Book titles',
                'notes': 'Optional notes and bibliography'
            }
        }

        return rules.get(style, {})
