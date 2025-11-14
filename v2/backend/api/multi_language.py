"""
Multi-language support API routes.
Handles language detection, translation, and cross-language research.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json

from ..api.auth import get_current_user
from ..models.user import User
from ..services.multi_language.language_support import MultiLanguageSupport

router = APIRouter()


# Request/Response Models

class LanguageDetectionRequest(BaseModel):
    """Request model for language detection."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to detect language for")


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection."""
    success: bool
    detected_language: Optional[str] = None
    confidence: float = 0.0
    language_info: Optional[Dict[str, Any]] = None
    detection_methods: Optional[int] = None
    error: Optional[str] = None


class TranslationRequest(BaseModel):
    """Request model for text translation."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'es', 'fr', 'de')")
    source_language: Optional[str] = Field(None, description="Source language code (auto-detected if not provided)")


class TranslationResponse(BaseModel):
    """Response model for text translation."""
    success: bool
    translated_text: str = ""
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    confidence: float = 0.0
    method: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class CrossLanguageResearchRequest(BaseModel):
    """Request model for cross-language research."""
    query: str = Field(..., min_length=1, max_length=1000, description="Research query")
    query_language: str = Field("en", description="Language of the query")
    response_language: str = Field("en", description="Desired response language")
    context: Optional[Dict[str, Any]] = Field(None, description="User context and preferences")


class CrossLanguageResearchResponse(BaseModel):
    """Response model for cross-language research."""
    success: bool
    research_result: Optional[Dict[str, Any]] = None
    language_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    stage: Optional[str] = None


class LanguageValidationResponse(BaseModel):
    """Response model for language validation."""
    supported: bool
    language_code: Optional[str] = None
    language_info: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


class LanguageCapabilitiesResponse(BaseModel):
    """Response model for language capabilities."""
    success: bool
    supported_languages: Optional[Dict[str, Any]] = None
    detection_available: bool = False
    translation_engines: Optional[List[str]] = None
    features: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BatchTranslationRequest(BaseModel):
    """Request model for batch translation."""
    texts: List[str] = Field(..., min_length=1, max_length=50, description="List of texts to translate")
    target_language: str = Field(..., description="Target language code")
    source_language: Optional[str] = Field(None, description="Source language code")


class BatchTranslationResponse(BaseModel):
    """Response model for batch translation."""
    success: bool
    translations: List[Dict[str, Any]]
    total_texts: int
    successful_translations: int
    error: Optional[str] = None


# API Endpoints

@router.post("/detect", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """
    Detect the language of input text.

    Uses multiple detection methods for improved accuracy across supported languages.
    """
    try:
        language_service = MultiLanguageSupport()
        result = await language_service.detect_language(request.text)

        return LanguageDetectionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}"
        )


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text to a target language.

    Supports multiple translation engines and provides alternatives when available.
    """
    try:
        # Validate languages
        language_service = MultiLanguageSupport()

        # Check if target language is supported
        target_validation = await language_service.validate_language_support(request.target_language)
        if not target_validation["supported"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{request.target_language}' is not supported"
            )

        # Check source language if provided
        if request.source_language:
            source_validation = await language_service.validate_language_support(request.source_language)
            if not source_validation["supported"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Source language '{request.source_language}' is not supported"
                )

        result = await language_service.translate_text(
            request.text,
            request.target_language,
            request.source_language
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Translation failed")
            )

        return TranslationResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/research", response_model=CrossLanguageResearchResponse)
async def perform_cross_language_research(
    request: CrossLanguageResearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform research with cross-language capabilities.

    Research in multiple languages and provide results in the user's preferred language.
    """
    try:
        # Validate languages
        language_service = MultiLanguageSupport()

        languages_to_check = [request.query_language, request.response_language]
        for lang_code in languages_to_check:
            validation = await language_service.validate_language_support(lang_code)
            if not validation["supported"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Language '{lang_code}' is not supported"
                )

        # Prepare user context
        user_context = request.context or {}
        user_context.update({
            "user_id": current_user.id,
            "query_language": request.query_language,
            "response_language": request.response_language
        })

        result = await language_service.perform_cross_language_research(
            request.query,
            request.query_language,
            request.response_language,
            user_context
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Cross-language research failed")
            )

        return CrossLanguageResearchResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cross-language research failed: {str(e)}"
        )


@router.get("/validate/{language_code}", response_model=LanguageValidationResponse)
async def validate_language_support(language_code: str):
    """
    Validate if a language is fully supported by the system.

    Checks detection, translation, and research capabilities for the language.
    """
    try:
        language_service = MultiLanguageSupport()
        result = await language_service.validate_language_support(language_code)

        return LanguageValidationResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language validation failed: {str(e)}"
        )


@router.get("/capabilities", response_model=LanguageCapabilitiesResponse)
async def get_language_capabilities():
    """
    Get information about supported languages and system capabilities.

    Provides comprehensive information about language support across the platform.
    """
    try:
        language_service = MultiLanguageSupport()
        capabilities = await language_service.get_language_capabilities()

        return LanguageCapabilitiesResponse(
            success=True,
            **capabilities
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get language capabilities: {str(e)}"
        )


@router.get("/info/{language_code}")
async def get_language_info(language_code: str):
    """
    Get detailed information about a specific language.

    Returns metadata including native name, region, script, and system capabilities.
    """
    try:
        language_service = MultiLanguageSupport()

        lang_info = language_service.get_language_info(language_code)
        if not lang_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language '{language_code}' not found"
            )

        # Get validation info
        validation = await language_service.validate_language_support(language_code)

        return {
            "success": True,
            "language_code": language_code,
            "language_info": lang_info,
            "capabilities": validation.get("capabilities", {}),
            "fully_supported": validation.get("supported", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get language info: {str(e)}"
        )


@router.get("/supported")
async def list_supported_languages(
    include_capabilities: bool = Query(False, description="Include detailed capabilities for each language")
):
    """
    List all supported languages.

    Returns basic information about each supported language, with optional capabilities.
    """
    try:
        language_service = MultiLanguageSupport()
        capabilities = await language_service.get_language_capabilities()

        supported_languages = capabilities.get("supported_languages", {})

        if include_capabilities:
            # Add validation info for each language
            detailed_languages = {}
            for lang_code, lang_info in supported_languages.items():
                validation = await language_service.validate_language_support(lang_code)
                detailed_languages[lang_code] = {
                    **lang_info,
                    "capabilities": validation.get("capabilities", {})
                }

            return {
                "success": True,
                "languages": detailed_languages,
                "total_languages": len(detailed_languages)
            }
        else:
            return {
                "success": True,
                "languages": supported_languages,
                "total_languages": len(supported_languages)
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list supported languages: {str(e)}"
        )


@router.post("/translate/batch", response_model=BatchTranslationResponse)
async def batch_translate_texts(request: BatchTranslationRequest):
    """
    Translate multiple texts in a single request.

    Efficiently process multiple translations with shared source/target languages.
    """
    try:
        if not request.texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No texts provided for translation"
            )

        language_service = MultiLanguageSupport()

        # Validate languages
        target_validation = await language_service.validate_language_support(request.target_language)
        if not target_validation["supported"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{request.target_language}' is not supported"
            )

        if request.source_language:
            source_validation = await language_service.validate_language_support(request.source_language)
            if not source_validation["supported"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Source language '{request.source_language}' is not supported"
                )

        translations = []
        successful_count = 0

        for i, text in enumerate(request.texts):
            try:
                result = await language_service.translate_text(
                    text,
                    request.target_language,
                    request.source_language
                )

                translation_data = {
                    "index": i,
                    "success": result["success"],
                    "text": result.get("translated_text", ""),
                    "confidence": result.get("confidence", 0.0),
                    "method": result.get("method"),
                    "source_language": result.get("source_language"),
                    "target_language": result.get("target_language")
                }

                if result["success"]:
                    successful_count += 1
                else:
                    translation_data["error"] = result.get("error")

                translations.append(translation_data)

            except Exception as e:
                translations.append({
                    "index": i,
                    "success": False,
                    "text": "",
                    "confidence": 0.0,
                    "error": str(e)
                })

        return BatchTranslationResponse(
            success=True,
            translations=translations,
            total_texts=len(request.texts),
            successful_translations=successful_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch translation failed: {str(e)}"
        )


@router.get("/stats")
async def get_language_stats():
    """
    Get usage statistics for multi-language features.

    Returns metrics on language detection, translation, and cross-language research usage.
    """
    try:
        language_service = MultiLanguageSupport()

        # Get translation stats
        translation_stats = await language_service.get_translation_stats()

        # Mock additional stats (would integrate with real analytics)
        detection_stats = {
            "total_detections": 2100,
            "accuracy_rate": 0.91,
            "popular_languages": {
                "en": 1200,
                "es": 340,
                "fr": 195,
                "de": 155,
                "zh": 85,
                "ja": 65
            },
            "cache_hit_rate": 0.68
        }

        research_stats = {
            "cross_language_researches": 450,
            "language_pairs": {
                "en-es": 120,
                "es-en": 95,
                "en-fr": 85,
                "fr-en": 70,
                "en-de": 45,
                "de-en": 35
            },
            "average_processing_time": 3.2
        }

        return {
            "success": True,
            "stats": {
                "detection": detection_stats,
                "translation": translation_stats,
                "research": research_stats,
                "generated_at": translation_stats.get("generated_at")
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get language stats: {str(e)}"
        )


@router.post("/detect/batch")
async def batch_detect_languages(texts: List[str]):
    """
    Detect languages for multiple texts in a single request.

    Efficiently process multiple language detections.
    """
    try:
        if not texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No texts provided for language detection"
            )

        if len(texts) > 100:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 texts per batch"
            )

        language_service = MultiLanguageSupport()

        detections = []
        successful_count = 0

        for i, text in enumerate(texts):
            try:
                result = await language_service.detect_language(text)

                detection_data = {
                    "index": i,
                    "success": result["success"],
                    "detected_language": result.get("detected_language"),
                    "confidence": result.get("confidence", 0.0)
                }

                if result["success"]:
                    successful_count += 1
                    detection_data["language_info"] = result.get("language_info")
                else:
                    detection_data["error"] = result.get("error")

                detections.append(detection_data)

            except Exception as e:
                detections.append({
                    "index": i,
                    "success": False,
                    "detected_language": None,
                    "confidence": 0.0,
                    "error": str(e)
                })

        return {
            "success": True,
            "detections": detections,
            "total_texts": len(texts),
            "successful_detections": successful_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch language detection failed: {str(e)}"
        )
