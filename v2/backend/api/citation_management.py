"""
Citation management API routes.
Handles citation generation, bibliography creation, and citation validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..api.auth import get_current_user
from ..models.user import User
from ..services.citation.citation_manager import CitationManager

router = APIRouter()


# Request/Response Models

class SourceData(BaseModel):
    """Source data for citation generation."""
    authors: Optional[List[str]] = Field(default_factory=list, description="List of authors")
    title: str = Field(..., description="Source title")
    year: Optional[str] = Field("", description="Publication year")
    publisher: Optional[str] = Field("", description="Publisher")
    journal: Optional[str] = Field("", description="Journal name")
    volume: Optional[str] = Field("", description="Volume number")
    issue: Optional[str] = Field("", description="Issue number")
    pages: Optional[str] = Field("", description="Page numbers")
    doi: Optional[str] = Field("", description="DOI")
    url: Optional[str] = Field("", description="URL")
    access_date: Optional[str] = Field("", description="Access date")
    edition: Optional[str] = Field("", description="Edition")
    editors: Optional[List[str]] = Field(default_factory=list, description="Editors")
    conference: Optional[str] = Field("", description="Conference name")
    location: Optional[str] = Field("", description="Location")
    isbn: Optional[str] = Field("", description="ISBN")
    issn: Optional[str] = Field("", description="ISSN")


class CitationRequest(BaseModel):
    """Request model for citation generation."""
    source_data: SourceData
    style: str = Field("apa", description="Citation style")
    citation_type: Optional[str] = Field("reference", description="Citation type: reference, in_text, footnote")


class CitationResponse(BaseModel):
    """Response model for citation generation."""
    success: bool
    citation: Optional[str] = None
    style: Optional[str] = None
    citation_type: Optional[str] = None
    source_type: Optional[str] = None
    normalized_source: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BibliographyRequest(BaseModel):
    """Request model for bibliography generation."""
    sources: List[SourceData] = Field(..., description="List of sources")
    style: str = Field("apa", description="Citation style")
    sort_by: Optional[str] = Field("author", description="Sort method: author, title, date, source_type")


class BibliographyResponse(BaseModel):
    """Response model for bibliography generation."""
    success: bool
    bibliography: Optional[Dict[str, Any]] = None
    total_sources: int = 0
    successful_citations: int = 0
    errors: Optional[List[str]] = None
    style: Optional[str] = None
    sort_method: Optional[str] = None
    error: Optional[str] = None


class ValidationRequest(BaseModel):
    """Request model for citation validation."""
    citation_text: str = Field(..., description="Citation text to validate")
    style: str = Field(..., description="Citation style")


class ValidationResponse(BaseModel):
    """Response model for citation validation."""
    valid: bool
    checks: Optional[List[Dict[str, Any]]] = None
    warnings: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    error: Optional[str] = None


class MetadataExtractionRequest(BaseModel):
    """Request model for metadata extraction."""
    citation_text: str = Field(..., description="Citation text to analyze")
    style: str = Field(..., description="Citation style")


class MetadataExtractionResponse(BaseModel):
    """Response model for metadata extraction."""
    success: bool
    metadata: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    error: Optional[str] = None


class BatchCitationRequest(BaseModel):
    """Request model for batch citation generation."""
    sources: List[Dict[str, Any]] = Field(..., description="List of source data dictionaries")
    style: str = Field("apa", description="Citation style")
    citation_type: Optional[str] = Field("reference", description="Citation type")


class BatchCitationResponse(BaseModel):
    """Response model for batch citation generation."""
    success: bool
    citations: List[Dict[str, Any]]
    total_sources: int
    successful_citations: int
    error: Optional[str] = None


class SupportedStylesResponse(BaseModel):
    """Response model for supported citation styles."""
    success: bool
    styles: Optional[Dict[str, Any]] = None
    total_styles: int = 0
    features: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StyleGuideResponse(BaseModel):
    """Response model for style guide information."""
    success: bool
    style_guide: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.post("/generate", response_model=CitationResponse)
async def generate_citation(request: CitationRequest):
    """
    Generate a citation for a source.

    Creates properly formatted citations in various academic styles.
    """
    try:
        citation_manager = CitationManager()

        result = await citation_manager.generate_citation(
            request.source_data.dict(),
            request.style,
            request.citation_type
        )

        return CitationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Citation generation failed: {str(e)}"
        )


@router.post("/bibliography", response_model=BibliographyResponse)
async def generate_bibliography(request: BibliographyRequest):
    """
    Generate a bibliography from multiple sources.

    Creates a properly formatted bibliography with citations sorted according to the specified method.
    """
    try:
        citation_manager = CitationManager()

        # Convert Pydantic models to dictionaries
        sources_data = [source.dict() for source in request.sources]

        result = await citation_manager.generate_bibliography(
            sources_data,
            request.style,
            request.sort_by
        )

        return BibliographyResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bibliography generation failed: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_citation(request: ValidationRequest):
    """
    Validate a citation for correctness.

    Checks citation format and completeness according to the specified style guidelines.
    """
    try:
        citation_manager = CitationManager()

        result = await citation_manager.validate_citation(
            request.citation_text,
            request.style
        )

        return ValidationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Citation validation failed: {str(e)}"
        )


@router.post("/extract-metadata", response_model=MetadataExtractionResponse)
async def extract_citation_metadata(request: MetadataExtractionRequest):
    """
    Extract metadata from a formatted citation.

    Analyzes citation text to extract author, title, year, and other metadata.
    """
    try:
        citation_manager = CitationManager()

        result = await citation_manager.extract_citation_metadata(
            request.citation_text,
            request.style
        )

        return MetadataExtractionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata extraction failed: {str(e)}"
        )


@router.post("/batch", response_model=BatchCitationResponse)
async def generate_batch_citations(request: BatchCitationRequest):
    """
    Generate citations for multiple sources in batch.

    Efficiently process multiple sources to generate citations.
    """
    try:
        if len(request.sources) > 50:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 sources per batch"
            )

        citation_manager = CitationManager()
        citations = []
        successful_count = 0

        for i, source_data in enumerate(request.sources):
            try:
                result = await citation_manager.generate_citation(
                    source_data,
                    request.style,
                    request.citation_type
                )

                citation_data = {
                    "index": i,
                    "success": result["success"],
                    "citation": result.get("citation"),
                    "source_type": result.get("source_type"),
                    "error": result.get("error") if not result["success"] else None
                }

                if result["success"]:
                    successful_count += 1

                citations.append(citation_data)

            except Exception as e:
                citations.append({
                    "index": i,
                    "success": False,
                    "citation": None,
                    "source_type": None,
                    "error": str(e)
                })

        return BatchCitationResponse(
            success=True,
            citations=citations,
            total_sources=len(request.sources),
            successful_citations=successful_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch citation generation failed: {str(e)}"
        )


@router.get("/styles", response_model=SupportedStylesResponse)
async def get_supported_styles():
    """
    Get information about supported citation styles.

    Returns details about all available citation styles and their features.
    """
    try:
        citation_manager = CitationManager()
        styles_info = citation_manager.get_supported_styles()

        return SupportedStylesResponse(
            success=True,
            **styles_info
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported styles: {str(e)}"
        )


@router.get("/styles/{style}", response_model=StyleGuideResponse)
async def get_style_guide(style: str):
    """
    Get detailed style guide for a citation style.

    Provides comprehensive information about formatting rules, examples, and guidelines.
    """
    try:
        citation_manager = CitationManager()
        style_guide = citation_manager.get_style_guide(style)

        if "error" in style_guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=style_guide["error"]
            )

        return StyleGuideResponse(
            success=True,
            style_guide=style_guide
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get style guide: {str(e)}"
        )


@router.get("/examples/{style}")
async def get_citation_examples(
    style: str,
    citation_type: Optional[str] = Query("reference", description="Citation type: reference, in_text")
):
    """
    Get citation examples for a style.

    Provides sample citations to help users understand formatting.
    """
    try:
        citation_manager = CitationManager()

        if style not in citation_manager.citation_styles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Style '{style}' not found"
            )

        examples = citation_manager._get_style_examples(style, citation_type)

        # Generate comprehensive examples
        sample_sources = [
            {
                "authors": ["Smith, John"],
                "title": "The Art of Research",
                "year": "2020",
                "publisher": "Academic Press"
            },
            {
                "authors": ["Johnson, Alice", "Brown, Bob"],
                "title": "Modern Methodologies in Science",
                "year": "2019",
                "journal": "Journal of Research",
                "volume": "45",
                "issue": "2",
                "pages": "123-145",
                "doi": "10.1234/jor.2019.45.2.123"
            },
            {
                "authors": ["Taylor, Robert", "Wilson, Mary", "Davis, Kevin"],
                "title": "Future Trends in Technology",
                "year": "2021",
                "conference": "International Conference on Technology",
                "location": "San Francisco, CA",
                "pages": "78-92"
            }
        ]

        detailed_examples = []
        for i, source in enumerate(sample_sources):
            try:
                result = await citation_manager.generate_citation(source, style, citation_type)
                if result["success"]:
                    detailed_examples.append({
                        "example_number": i + 1,
                        "source_data": source,
                        "citation": result["citation"],
                        "citation_type": citation_type
                    })
            except Exception as e:
                continue

        return {
            "success": True,
            "style": style,
            "citation_type": citation_type,
            "examples": examples,
            "detailed_examples": detailed_examples,
            "total_examples": len(detailed_examples)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get citation examples: {str(e)}"
        )


@router.post("/convert")
async def convert_citation_style(
    citation_text: str = Query(..., description="Citation text to convert"),
    from_style: str = Query(..., description="Source citation style"),
    to_style: str = Query(..., description="Target citation style")
):
    """
    Convert a citation from one style to another.

    Attempts to convert citation formatting between different styles.
    """
    try:
        citation_manager = CitationManager()

        # First, extract metadata from the source citation
        metadata_result = await citation_manager.extract_citation_metadata(
            citation_text,
            from_style
        )

        if not metadata_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not parse source citation"
            )

        # Convert metadata back to source data format
        source_data = {
            "authors": metadata_result["metadata"]["authors"],
            "title": metadata_result["metadata"]["title"],
            "year": metadata_result["metadata"]["year"],
            "doi": metadata_result["metadata"]["doi"],
            "url": metadata_result["metadata"]["url"]
        }

        # Generate citation in target style
        result = await citation_manager.generate_citation(
            source_data,
            to_style,
            "reference"
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Citation conversion failed"
            )

        return {
            "success": True,
            "original_citation": citation_text,
            "original_style": from_style,
            "converted_citation": result["citation"],
            "converted_style": to_style,
            "confidence": metadata_result["confidence"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Citation conversion failed: {str(e)}"
        )


@router.get("/stats")
async def get_citation_stats():
    """
    Get citation generation statistics.

    Returns usage metrics and popular citation styles.
    """
    try:
        # This would integrate with real analytics
        # For now, return mock data
        stats = {
            "total_citations_generated": 5420,
            "total_bibliographies_created": 345,
            "popular_styles": {
                "apa": 2840,
                "mla": 1560,
                "chicago": 680,
                "ieee": 340
            },
            "citation_types": {
                "reference": 4850,
                "in_text": 420,
                "footnote": 150
            },
            "source_types": {
                "journal_article": 2100,
                "book": 1800,
                "website": 1200,
                "conference_paper": 320
            },
            "validation_requests": 890,
            "cache_hit_rate": 0.73,
            "generated_at": "2024-01-01T12:00:00Z"
        }

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get citation stats: {str(e)}"
        )


@router.post("/format-check")
async def check_citation_format(
    citations: List[str] = Query(..., description="List of citations to check"),
    expected_style: str = Query(..., description="Expected citation style")
):
    """
    Check multiple citations for format consistency.

    Validates that citations follow the expected style guidelines.
    """
    try:
        if len(citations) > 20:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 citations per format check"
            )

        citation_manager = CitationManager()
        results = []

        for i, citation_text in enumerate(citations):
            try:
                validation = await citation_manager.validate_citation(
                    citation_text,
                    expected_style
                )

                results.append({
                    "index": i,
                    "citation": citation_text,
                    "valid": validation["valid"],
                    "errors": validation.get("errors", []),
                    "warnings": validation.get("warnings", []),
                    "checks_passed": sum(1 for check in validation.get("checks", []) if check.get("passed", False)),
                    "total_checks": len(validation.get("checks", []))
                })

            except Exception as e:
                results.append({
                    "index": i,
                    "citation": citation_text,
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                    "checks_passed": 0,
                    "total_checks": 0
                })

        # Summary statistics
        valid_count = sum(1 for r in results if r["valid"])
        total_errors = sum(len(r["errors"]) for r in results)
        total_warnings = sum(len(r["warnings"]) for r in results)

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_citations": len(citations),
                "valid_citations": valid_count,
                "invalid_citations": len(citations) - valid_count,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "expected_style": expected_style
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Format check failed: {str(e)}"
        )
