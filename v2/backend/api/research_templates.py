"""
Research templates API routes.
Provides access to pre-built research workflows and template management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..api.auth import get_current_user
from ..models.user import User
from ..services.templates.research_templates import ResearchTemplateManager

router = APIRouter()


# Request/Response Models

class TemplateInfo(BaseModel):
    """Information about a research template."""
    id: str
    name: str
    description: str
    category: str
    is_builtin: bool
    usage_count: Optional[int] = None
    estimated_time: Optional[str] = None
    difficulty: Optional[str] = None
    suggested_tags: Optional[List[str]] = None


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    success: bool
    templates: Dict[str, List[TemplateInfo]]
    total: int
    categories: List[str]
    error: Optional[str] = None


class TemplateDetailsResponse(BaseModel):
    """Response model for template details."""
    success: bool
    template: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ApplyTemplateRequest(BaseModel):
    """Request model for applying a template."""
    research_query: str = Field(..., description="Research query to apply template to")


class ApplyTemplateResponse(BaseModel):
    """Response model for template application."""
    success: bool
    research_config: Optional[Dict[str, Any]] = None
    template_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CreateTemplateRequest(BaseModel):
    """Request model for creating custom templates."""
    name: str = Field(..., min_length=3, max_length=100, description="Template name")
    description: str = Field("", max_length=500, description="Template description")
    category: str = Field("custom", description="Template category")
    default_persona: Optional[str] = Field("default", description="Default persona")
    default_depth: Optional[str] = Field("comprehensive", description="Default research depth")

    # Template configuration
    workflow_steps: Dict[str, Any] = Field(..., description="Workflow steps and phases")
    suggested_tags: Optional[List[str]] = Field(default_factory=list, description="Suggested tags")
    estimated_time: Optional[str] = Field(None, description="Estimated completion time")
    difficulty: Optional[str] = Field("intermediate", description="Difficulty level")
    is_public: Optional[bool] = Field(False, description="Whether template is public")


class CreateTemplateResponse(BaseModel):
    """Response model for template creation."""
    success: bool
    template_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class TemplateUsageStats(BaseModel):
    """Usage statistics for templates."""
    total_usage: int
    popular_templates: List[Dict[str, Any]]
    category_breakdown: Dict[str, int]
    generated_at: str


class TemplateStatsResponse(BaseModel):
    """Response model for template statistics."""
    success: bool
    stats: Optional[TemplateUsageStats] = None
    error: Optional[str] = None


class ResearchPlanResponse(BaseModel):
    """Response model for generated research plans."""
    success: bool
    research_plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TemplateRecommendationsResponse(BaseModel):
    """Response model for template recommendations."""
    success: bool
    recommendations: List[Dict[str, Any]]
    error: Optional[str] = None


# API Endpoints

@router.get("/list", response_model=TemplateListResponse)
async def list_research_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    include_builtin: bool = Query(True, description="Include built-in templates"),
    include_custom: bool = Query(True, description="Include custom templates")
):
    """
    List all available research templates.

    Returns built-in templates and user-created templates with optional filtering.
    """
    try:
        template_manager = ResearchTemplateManager()

        result = await template_manager.get_available_templates(category)

        # Apply inclusion filters
        filtered_templates = {}
        for template_id, template_info in result["templates"].items():
            if template_info.get("is_builtin") and not include_builtin:
                continue
            if not template_info.get("is_builtin") and not include_custom:
                continue

            category_key = template_info.get("category", "other")
            if category_key not in filtered_templates:
                filtered_templates[category_key] = []
            filtered_templates[category_key].append(template_info)

        return TemplateListResponse(
            success=True,
            templates=filtered_templates,
            total=sum(len(templates) for templates in filtered_templates.values()),
            categories=list(filtered_templates.keys())
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list research templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=TemplateDetailsResponse)
async def get_template_details(template_id: str):
    """
    Get detailed information about a specific research template.

    Returns complete template configuration including workflow steps and guidelines.
    """
    try:
        template_manager = ResearchTemplateManager()

        result = await template_manager.get_template_details(template_id)

        return TemplateDetailsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template details: {str(e)}"
        )


@router.post("/{template_id}/apply", response_model=ApplyTemplateResponse)
async def apply_research_template(
    template_id: str,
    request: ApplyTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Apply a research template to a query.

    Returns enhanced research configuration with template-specific settings and workflow guidance.
    """
    try:
        template_manager = ResearchTemplateManager()

        result = await template_manager.apply_template_to_research(template_id, request.research_query)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Template not found")
            )

        return ApplyTemplateResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply research template: {str(e)}"
        )


@router.post("/create", response_model=CreateTemplateResponse)
async def create_custom_template(
    request: CreateTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a custom research template.

    Allows users to create their own research templates based on successful research workflows.
    """
    try:
        template_manager = ResearchTemplateManager()

        template_data = request.dict()
        # Remove None values
        template_data = {k: v for k, v in template_data.items() if v is not None}

        result = await template_manager.create_custom_template(current_user.id, template_data)

        return CreateTemplateResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom template: {str(e)}"
        )


@router.get("/stats", response_model=TemplateStatsResponse)
async def get_template_usage_stats():
    """
    Get usage statistics for research templates.

    Provides insights into template popularity and effectiveness.
    """
    try:
        template_manager = ResearchTemplateManager()

        stats = await template_manager.get_template_usage_stats()

        return TemplateStatsResponse(
            success=True,
            stats=TemplateUsageStats(**stats)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template statistics: {str(e)}"
        )


@router.post("/{template_id}/plan", response_model=ResearchPlanResponse)
async def generate_research_plan(
    template_id: str,
    request: ApplyTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a detailed research plan from a template.

    Creates a comprehensive research roadmap with phases, timelines, and deliverables.
    """
    try:
        template_manager = ResearchTemplateManager()

        research_plan = template_manager.generate_research_plan_from_template(
            template_id, request.research_query
        )

        if "error" in research_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=research_plan["error"]
            )

        return ResearchPlanResponse(
            success=True,
            research_plan=research_plan
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate research plan: {str(e)}"
        )


@router.post("/recommend", response_model=TemplateRecommendationsResponse)
async def get_template_recommendations(
    request: ApplyTemplateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get template recommendations based on research query analysis.

    Analyzes the query to suggest the most appropriate research templates.
    """
    try:
        template_manager = ResearchTemplateManager()

        recommendations = await template_manager.get_recommended_templates(request.research_query)

        return TemplateRecommendationsResponse(
            success=True,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template recommendations: {str(e)}"
        )


@router.get("/categories", response_model=Dict[str, Any])
async def get_template_categories():
    """
    Get available template categories and their descriptions.

    Provides information about different types of research templates available.
    """
    categories = {
        "academic": {
            "name": "Academic Research",
            "description": "Templates for academic papers, theses, and scholarly research",
            "difficulty_range": "intermediate to expert",
            "typical_duration": "1-4 weeks"
        },
        "technical": {
            "name": "Technical Documentation",
            "description": "Templates for API docs, implementation guides, and technical specifications",
            "difficulty_range": "beginner to advanced",
            "typical_duration": "3-10 days"
        },
        "analysis": {
            "name": "Comparative Analysis",
            "description": "Templates for comparing technologies, products, or approaches",
            "difficulty_range": "intermediate",
            "typical_duration": "3-7 days"
        },
        "verification": {
            "name": "Fact Checking",
            "description": "Templates for verifying claims, statistics, and information accuracy",
            "difficulty_range": "beginner to intermediate",
            "typical_duration": "1-4 hours"
        },
        "business": {
            "name": "Business Analysis",
            "description": "Templates for industry analysis, market research, and business intelligence",
            "difficulty_range": "intermediate to advanced",
            "typical_duration": "1-2 weeks"
        },
        "trends": {
            "name": "Trend Research",
            "description": "Templates for identifying and analyzing emerging trends",
            "difficulty_range": "intermediate",
            "typical_duration": "3-7 days"
        },
        "ux": {
            "name": "User Research",
            "description": "Templates for user interviews, usability testing, and UX research synthesis",
            "difficulty_range": "intermediate",
            "typical_duration": "3-5 days"
        },
        "custom": {
            "name": "Custom Templates",
            "description": "User-created templates tailored to specific research needs",
            "difficulty_range": "varies",
            "typical_duration": "varies"
        }
    }

    return {
        "success": True,
        "categories": categories,
        "total_categories": len(categories)
    }


@router.get("/difficulty/levels", response_model=Dict[str, Any])
async def get_difficulty_levels():
    """
    Get information about template difficulty levels.

    Helps users choose appropriate templates for their skill level and needs.
    """
    difficulty_levels = {
        "beginner": {
            "description": "Simple templates requiring basic research skills",
            "requirements": ["Internet search proficiency", "Basic writing skills"],
            "estimated_completion": "1-4 hours",
            "best_for": ["Quick fact checking", "Basic information gathering", "Simple comparisons"]
        },
        "intermediate": {
            "description": "Templates requiring research methodology knowledge",
            "requirements": ["Research planning skills", "Data analysis", "Critical thinking"],
            "estimated_completion": "1-7 days",
            "best_for": ["Comparative analysis", "Technical documentation", "Business research"]
        },
        "advanced": {
            "description": "Complex templates requiring domain expertise",
            "requirements": ["Subject matter expertise", "Advanced analysis", "Strategic thinking"],
            "estimated_completion": "1-2 weeks",
            "best_for": ["Industry analysis", "Academic research", "Complex technical projects"]
        },
        "expert": {
            "description": "Advanced templates for professional researchers",
            "requirements": ["Research methodology expertise", "Publication experience", "Statistical analysis"],
            "estimated_completion": "2-4 weeks",
            "best_for": ["Academic publications", "Comprehensive literature reviews", "Expert analysis"]
        }
    }

    return {
        "success": True,
        "difficulty_levels": difficulty_levels,
        "assessment_questions": [
            "How familiar are you with research methodology?",
            "What's your experience level in this subject area?",
            "How much time do you have to complete this research?",
            "What's the complexity level required for your use case?"
        ]
    }


@router.post("/validate")
async def validate_template_config(request: CreateTemplateRequest):
    """
    Validate a custom template configuration.

    Allows users to check their template before creation.
    """
    try:
        template_manager = ResearchTemplateManager()

        template_data = request.dict()
        validation_result = template_manager._validate_template_data(template_data)

        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"],
            "warnings": []
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate template configuration: {str(e)}"
        )
