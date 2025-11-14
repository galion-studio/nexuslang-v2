"""
Custom persona management API routes.
Allows users to create, manage, and use custom writing personas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..services.personas.custom_persona_manager import CustomPersonaManager

router = APIRouter()


# Request/Response Models

class CreatePersonaRequest(BaseModel):
    """Request model for creating a custom persona."""
    name: str = Field(..., min_length=2, max_length=50, description="Persona name")
    description: str = Field("", max_length=500, description="Persona description")
    base_persona: Optional[str] = Field(None, description="Base persona to inherit from")

    # Personality configuration
    personality_traits: Optional[Dict[str, str]] = Field(default_factory=dict, description="Personality traits")
    writing_style: Optional[Dict[str, str]] = Field(default_factory=dict, description="Writing style preferences")
    content_focus: Optional[List[str]] = Field(default_factory=list, description="Content focus areas")
    tone_preferences: Optional[List[str]] = Field(default_factory=list, description="Tone preferences")
    structural_patterns: Optional[List[str]] = Field(default_factory=list, description="Structural patterns")
    domain_expertise: Optional[List[str]] = Field(default_factory=list, description="Domain expertise areas")

    # Technical preferences
    language_complexity: Optional[str] = Field("balanced", description="Language complexity level")
    citation_style: Optional[str] = Field("inline", description="Citation style preference")

    # Meta information
    is_public: Optional[bool] = Field(False, description="Whether persona is publicly available")
    tags: Optional[List[str]] = Field(default_factory=list, description="Persona tags")


class CreatePersonaResponse(BaseModel):
    """Response model for persona creation."""
    success: bool
    persona_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class PersonaInfo(BaseModel):
    """Information about a persona."""
    id: str
    name: str
    description: str
    is_custom: bool
    is_builtin: Optional[bool] = False
    usage_count: Optional[int] = None
    created_at: Optional[str] = None
    creator: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ListPersonasResponse(BaseModel):
    """Response model for listing personas."""
    success: bool
    personas: Dict[str, List[PersonaInfo]]
    total: int
    error: Optional[str] = None


class UpdatePersonaRequest(BaseModel):
    """Request model for updating a persona."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    personality_traits: Optional[Dict[str, str]] = None
    writing_style: Optional[Dict[str, str]] = None
    content_focus: Optional[List[str]] = None
    tone_preferences: Optional[List[str]] = None
    structural_patterns: Optional[List[str]] = None
    domain_expertise: Optional[List[str]] = None
    language_complexity: Optional[str] = None
    citation_style: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class UpdatePersonaResponse(BaseModel):
    """Response model for persona updates."""
    success: bool
    persona_id: Optional[str] = None
    updated_at: Optional[str] = None
    error: Optional[str] = None


class PersonaTemplateResponse(BaseModel):
    """Response model for persona templates."""
    success: bool
    template: Optional[Dict[str, Any]] = None
    available_templates: Optional[List[str]] = None
    error: Optional[str] = None


class PersonaStatsResponse(BaseModel):
    """Response model for persona usage statistics."""
    success: bool
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.post("/create", response_model=CreatePersonaResponse)
async def create_custom_persona(
    request: CreatePersonaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new custom persona.

    Allows users to define their own writing personas with custom characteristics,
    styles, and preferences that can be used in deep research.
    """
    try:
        persona_manager = CustomPersonaManager()

        persona_data = request.dict()
        # Remove None values
        persona_data = {k: v for k, v in persona_data.items() if v is not None}

        result = await persona_manager.create_custom_persona(db, current_user.id, persona_data)

        return CreatePersonaResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom persona: {str(e)}"
        )


@router.get("/list", response_model=ListPersonasResponse)
async def list_personas(
    include_public: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all available personas for the user.

    Returns custom personas created by the user, public personas created by others,
    and built-in personas that come with the system.
    """
    try:
        persona_manager = CustomPersonaManager()

        result = await persona_manager.get_user_personas(db, current_user.id, include_public)

        return ListPersonasResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list personas: {str(e)}"
        )


@router.put("/{persona_id}", response_model=UpdatePersonaResponse)
async def update_custom_persona(
    persona_id: str,
    request: UpdatePersonaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing custom persona.

    Allows modification of persona characteristics, settings, and metadata.
    """
    try:
        persona_manager = CustomPersonaManager()

        update_data = request.dict(exclude_unset=True)

        result = await persona_manager.update_custom_persona(
            db, current_user.id, persona_id, update_data
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Persona not found")
            )

        return UpdatePersonaResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update persona: {str(e)}"
        )


@router.delete("/{persona_id}")
async def delete_custom_persona(
    persona_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a custom persona.

    Removes the persona and all its associated data.
    """
    try:
        persona_manager = CustomPersonaManager()

        result = await persona_manager.delete_custom_persona(
            db, current_user.id, persona_id
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Persona not found")
            )

        return {"success": True, "message": "Persona deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete persona: {str(e)}"
        )


@router.get("/templates", response_model=PersonaTemplateResponse)
async def get_persona_templates():
    """
    Get available persona creation templates.

    Provides pre-built templates for common persona types that users
    can customize to create their own personas.
    """
    try:
        persona_manager = CustomPersonaManager()

        # Get available template types
        available_templates = ["basic", "academic", "creative"]

        return PersonaTemplateResponse(
            success=True,
            available_templates=available_templates
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get persona templates: {str(e)}"
        )


@router.get("/templates/{template_type}", response_model=PersonaTemplateResponse)
async def get_persona_template(template_type: str):
    """
    Get a specific persona creation template.

    Returns a complete template configuration for the specified type
    that users can use as a starting point for their custom personas.
    """
    try:
        persona_manager = CustomPersonaManager()

        template = persona_manager.get_persona_template(template_type)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template type '{template_type}' not found"
            )

        return PersonaTemplateResponse(
            success=True,
            template=template
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get persona template: {str(e)}"
        )


@router.get("/stats/{persona_id}", response_model=PersonaStatsResponse)
async def get_persona_stats(
    persona_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get usage statistics for a persona.

    Provides insights into how often a persona is used and its performance.
    """
    try:
        persona_manager = CustomPersonaManager()

        stats = await persona_manager.get_persona_usage_stats(db, persona_id)

        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=stats["error"]
            )

        return PersonaStatsResponse(
            success=True,
            stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get persona statistics: {str(e)}"
        )


@router.post("/validate")
async def validate_persona_config(request: CreatePersonaRequest):
    """
    Validate a persona configuration without creating it.

    Allows users to check if their persona configuration is valid
    before attempting to create the persona.
    """
    try:
        persona_manager = CustomPersonaManager()

        persona_data = request.dict()
        validation_result = persona_manager._validate_persona_data(persona_data)

        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"],
            "warnings": []  # Could add warnings for best practices
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate persona configuration: {str(e)}"
        )


@router.get("/public/browse")
async def browse_public_personas(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Browse publicly available personas.

    Allows users to discover and use personas created by other users.
    Supports filtering by category and search functionality.
    """
    try:
        from sqlalchemy import or_, and_, func

        # Build query for public personas
        query = db.query(ResearchTemplate).filter(
            ResearchTemplate.category == "custom_persona",
            ResearchTemplate.is_public == True
        )

        # Apply filters
        if category:
            query = query.filter(ResearchTemplate.workflow_steps.contains(f'"category": "{category}"'))

        if search:
            search_filter = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(ResearchTemplate.name).like(search_filter),
                    func.lower(ResearchTemplate.description).like(search_filter)
                )
            )

        # Order by usage count and creation date
        query = query.order_by(
            ResearchTemplate.usage_count.desc(),
            ResearchTemplate.created_at.desc()
        )

        # Apply pagination
        total_query = query.with_entities(func.count(ResearchTemplate.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        personas = result.scalars().all()

        # Format response
        persona_list = []
        for persona in personas:
            config = json.loads(persona.workflow_steps) if persona.workflow_steps else {}

            persona_list.append({
                "id": str(persona.id),
                "name": persona.name,
                "description": persona.description,
                "usage_count": persona.usage_count,
                "created_at": persona.created_at.isoformat(),
                "creator": persona.created_by,
                "tags": config.get("tags", []),
                "base_persona": config.get("base_persona"),
                "category": config.get("category", "general")
            })

        return {
            "success": True,
            "personas": persona_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to browse public personas: {str(e)}"
        )
