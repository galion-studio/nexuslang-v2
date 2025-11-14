"""
Custom persona creation and management for Deep Search.
Allows users to create personalized writing personas with custom styles.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import json

from ...models.research import ResearchTemplate
from ..deep_search.personas.persona_manager import PersonaManager

logger = logging.getLogger(__name__)


class CustomPersonaManager:
    """
    Manages user-created custom personas for deep search.

    Features:
    - Create custom writing personas with user-defined characteristics
    - Persona inheritance and templates
    - Persona sharing and community features
    - Persona performance analytics
    - Version control and updates
    """

    def __init__(self):
        self.base_persona_manager = PersonaManager()
        self.max_personas_per_user = 20
        self.max_public_personas = 100

    async def create_custom_persona(self, session: AsyncSession, user_id: str,
                                   persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom persona for a user.

        Args:
            session: Database session
            user_id: User identifier
            persona_data: Persona configuration data

        Returns:
            Creation result
        """
        try:
            # Validate persona data
            validation_result = self._validate_persona_data(persona_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid persona data: {', '.join(validation_result['errors'])}"
                }

            # Check user persona limit
            existing_count = await self._count_user_personas(session, user_id)
            if existing_count >= self.max_personas_per_user:
                return {
                    "success": False,
                    "error": f"Maximum {self.max_personas_per_user} personas per user reached"
                }

            # Create persona record
            custom_persona = ResearchTemplate(
                name=persona_data["name"],
                description=persona_data.get("description", ""),
                category="custom_persona",
                default_persona="custom",  # Special marker for custom personas
                workflow_steps=json.dumps(persona_data.get("characteristics", {})),
                created_by=user_id
            )

            # Store persona configuration in workflow_steps field
            persona_config = {
                "personality_traits": persona_data.get("personality_traits", {}),
                "writing_style": persona_data.get("writing_style", {}),
                "content_focus": persona_data.get("content_focus", []),
                "tone_preferences": persona_data.get("tone_preferences", []),
                "structural_patterns": persona_data.get("structural_patterns", []),
                "domain_expertise": persona_data.get("domain_expertise", []),
                "language_complexity": persona_data.get("language_complexity", "balanced"),
                "citation_style": persona_data.get("citation_style", "inline"),
                "base_persona": persona_data.get("base_persona"),  # Optional inheritance
                "is_public": persona_data.get("is_public", False),
                "tags": persona_data.get("tags", [])
            }

            custom_persona.workflow_steps = json.dumps(persona_config)

            session.add(custom_persona)
            await session.commit()
            await session.refresh(custom_persona)

            logger.info(f"Created custom persona '{persona_data['name']}' for user {user_id}")

            return {
                "success": True,
                "persona_id": str(custom_persona.id),
                "name": custom_persona.name,
                "created_at": custom_persona.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create custom persona: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def get_user_personas(self, session: AsyncSession, user_id: str,
                               include_public: bool = True) -> Dict[str, Any]:
        """
        Get all personas available to a user (custom + public).

        Args:
            session: Database session
            user_id: User identifier
            include_public: Whether to include public personas

        Returns:
            Available personas
        """
        try:
            # Get user's custom personas
            custom_personas = []
            custom_query = session.query(ResearchTemplate).filter(
                ResearchTemplate.created_by == user_id,
                ResearchTemplate.category == "custom_persona"
            ).order_by(ResearchTemplate.created_at.desc())

            custom_results = await session.execute(custom_query)
            for persona in custom_results.scalars():
                config = json.loads(persona.workflow_steps)
                custom_personas.append({
                    "id": str(persona.id),
                    "name": persona.name,
                    "description": persona.description,
                    "is_custom": True,
                    "usage_count": persona.usage_count,
                    "created_at": persona.created_at.isoformat(),
                    "config": config
                })

            # Get public personas if requested
            public_personas = []
            if include_public:
                public_query = session.query(ResearchTemplate).filter(
                    ResearchTemplate.category == "custom_persona",
                    ResearchTemplate.is_public == True,
                    ResearchTemplate.created_by != user_id  # Exclude user's own public personas
                ).order_by(ResearchTemplate.usage_count.desc())

                public_results = await session.execute(public_query)
                for persona in public_results.scalars():
                    config = json.loads(persona.workflow_steps)
                    public_personas.append({
                        "id": str(persona.id),
                        "name": persona.name,
                        "description": persona.description,
                        "is_custom": False,
                        "usage_count": persona.usage_count,
                        "created_at": persona.created_at.isoformat(),
                        "creator": persona.created_by,
                        "config": config
                    })

            # Get built-in personas
            builtin_personas = []
            for name, persona_info in self.base_persona_manager.get_available_personas().items():
                builtin_personas.append({
                    "id": f"builtin_{name}",
                    "name": name,
                    "description": persona_info["description"],
                    "is_custom": False,
                    "is_builtin": True,
                    "category": "builtin"
                })

            return {
                "success": True,
                "personas": {
                    "custom": custom_personas,
                    "public": public_personas,
                    "builtin": builtin_personas
                },
                "total": len(custom_personas) + len(public_personas) + len(builtin_personas)
            }

        except Exception as e:
            logger.error(f"Failed to get user personas: {e}")
            return {
                "success": False,
                "error": str(e),
                "personas": {"custom": [], "public": [], "builtin": []},
                "total": 0
            }

    async def update_custom_persona(self, session: AsyncSession, user_id: str,
                                   persona_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing custom persona.

        Args:
            session: Database session
            user_id: User identifier
            persona_id: Persona ID to update
            update_data: Fields to update

        Returns:
            Update result
        """
        try:
            # Find the persona
            persona_query = session.query(ResearchTemplate).filter(
                ResearchTemplate.id == persona_id,
                ResearchTemplate.created_by == user_id,
                ResearchTemplate.category == "custom_persona"
            )

            result = await session.execute(persona_query)
            persona = result.scalar_one_or_none()

            if not persona:
                return {
                    "success": False,
                    "error": "Persona not found or access denied"
                }

            # Update allowed fields
            if "name" in update_data:
                persona.name = update_data["name"]
            if "description" in update_data:
                persona.description = update_data["description"]

            # Update persona configuration
            current_config = json.loads(persona.workflow_steps)
            config_updates = {}

            # Handle configuration updates
            config_fields = [
                "personality_traits", "writing_style", "content_focus",
                "tone_preferences", "structural_patterns", "domain_expertise",
                "language_complexity", "citation_style", "tags"
            ]

            for field in config_fields:
                if field in update_data:
                    config_updates[field] = update_data[field]

            if config_updates:
                current_config.update(config_updates)
                persona.workflow_steps = json.dumps(current_config)

            # Handle public/private status
            if "is_public" in update_data:
                # Check public persona limit
                if update_data["is_public"]:
                    public_count = await self._count_public_personas(session)
                    if public_count >= self.max_public_personas:
                        return {
                            "success": False,
                            "error": f"Maximum {self.max_public_personas} public personas reached"
                        }
                persona.is_public = update_data["is_public"]

            persona.updated_at = datetime.utcnow()

            await session.commit()

            return {
                "success": True,
                "persona_id": str(persona.id),
                "updated_at": persona.updated_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to update custom persona: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_custom_persona(self, session: AsyncSession, user_id: str,
                                   persona_id: str) -> Dict[str, Any]:
        """
        Delete a custom persona.

        Args:
            session: Database session
            user_id: User identifier
            persona_id: Persona ID to delete

        Returns:
            Deletion result
        """
        try:
            # Find and delete the persona
            persona_query = session.query(ResearchTemplate).filter(
                ResearchTemplate.id == persona_id,
                ResearchTemplate.created_by == user_id,
                ResearchTemplate.category == "custom_persona"
            )

            result = await session.execute(persona_query)
            persona = result.scalar_one_or_none()

            if not persona:
                return {
                    "success": False,
                    "error": "Persona not found or access denied"
                }

            await session.delete(persona)
            await session.commit()

            logger.info(f"Deleted custom persona '{persona.name}' for user {user_id}")

            return {
                "success": True,
                "persona_id": persona_id
            }

        except Exception as e:
            logger.error(f"Failed to delete custom persona: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def synthesize_with_custom_persona(self, persona_config: Dict[str, Any],
                                           query: str, information: Dict[str, Any],
                                           context: Dict[str, Any] = None) -> str:
        """
        Synthesize information using a custom persona.

        Args:
            persona_config: Custom persona configuration
            query: Research query
            information: Information to synthesize
            context: Additional context

        Returns:
            Synthesized response
        """
        try:
            # Build persona prompt from configuration
            prompt_parts = []

            # Base persona inheritance
            base_persona = persona_config.get("base_persona")
            if base_persona and base_persona in self.base_persona_manager.personas:
                base_config = self.base_persona_manager.personas[base_persona]
                prompt_parts.append(base_config.get_personality_prompt())

            # Custom characteristics
            personality = persona_config.get("personality_traits", {})
            if personality:
                prompt_parts.append("Custom Personality Traits:")
                for trait, value in personality.items():
                    prompt_parts.append(f"- {trait}: {value}")

            writing_style = persona_config.get("writing_style", {})
            if writing_style:
                prompt_parts.append("\nCustom Writing Style:")
                for style, description in writing_style.items():
                    prompt_parts.append(f"- {style}: {description}")

            # Content focus
            content_focus = persona_config.get("content_focus", [])
            if content_focus:
                prompt_parts.append(f"\nContent Focus Areas: {', '.join(content_focus)}")

            # Tone preferences
            tone_prefs = persona_config.get("tone_preferences", [])
            if tone_prefs:
                prompt_parts.append(f"\nTone Preferences: {', '.join(tone_prefs)}")

            # Language complexity
            complexity = persona_config.get("language_complexity", "balanced")
            prompt_parts.append(f"\nLanguage Complexity: {complexity}")

            full_prompt = "\n".join(prompt_parts)

            # Use base persona synthesis with custom prompt
            if base_persona and base_persona in self.base_persona_manager.personas:
                base_persona_obj = self.base_persona_manager.personas[base_persona]
                return await base_persona_obj.synthesize(query, information, context)
            else:
                # Fallback to default synthesis with custom prompt
                return await self._synthesize_with_custom_prompt(full_prompt, query, information, context)

        except Exception as e:
            logger.error(f"Failed to synthesize with custom persona: {e}")
            # Fallback to basic synthesis
            main_points = information.get("main_points", [])
            return "\n".join([f"• {point}" for point in main_points[:5]])

    async def _synthesize_with_custom_prompt(self, custom_prompt: str, query: str,
                                           information: Dict[str, Any],
                                           context: Dict[str, Any] = None) -> str:
        """
        Synthesize using a custom prompt when no base persona is specified.
        """
        try:
            # Create a basic synthesis based on the information
            main_points = information.get("main_points", [])
            sources = information.get("sources_used", [])

            if not main_points:
                return f"Based on research about '{query}', no specific findings were identified."

            # Structure the response
            response_parts = [
                f"Research Summary: {query}",
                "",
                "Key Findings:"
            ]

            for i, point in enumerate(main_points[:8], 1):
                response_parts.append(f"{i}. {point}")

            if sources:
                response_parts.extend([
                    "",
                    "Sources:"
                ])
                for i, source in enumerate(sources[:3], 1):
                    title = source.get("title", f"Source {i}")
                    response_parts.append(f"{i}. {title}")

            return "\n".join(response_parts)

        except Exception as e:
            logger.error(f"Custom prompt synthesis failed: {e}")
            return f"Research on '{query}' completed, but synthesis encountered an error."

    def _validate_persona_data(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate custom persona configuration data.

        Args:
            persona_data: Persona data to validate

        Returns:
            Validation result
        """
        errors = []

        # Required fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in persona_data or not persona_data[field].strip():
                errors.append(f"Missing required field: {field}")

        # Name validation
        if "name" in persona_data:
            name = persona_data["name"].strip()
            if len(name) < 2 or len(name) > 50:
                errors.append("Name must be between 2 and 50 characters")
            if not name.replace(" ", "").replace("-", "").replace("_", "").isalnum():
                errors.append("Name can only contain letters, numbers, spaces, hyphens, and underscores")

        # Optional field validation
        if "description" in persona_data and len(persona_data["description"]) > 500:
            errors.append("Description cannot exceed 500 characters")

        # Personality traits validation
        if "personality_traits" in persona_data:
            traits = persona_data["personality_traits"]
            if not isinstance(traits, dict):
                errors.append("Personality traits must be a dictionary")
            elif len(traits) > 20:
                errors.append("Cannot have more than 20 personality traits")

        # Base persona validation
        if "base_persona" in persona_data:
            base_persona = persona_data["base_persona"]
            valid_bases = list(self.base_persona_manager.personas.keys())
            if base_persona not in valid_bases:
                errors.append(f"Base persona must be one of: {', '.join(valid_bases)}")

        # Language complexity validation
        if "language_complexity" in persona_data:
            valid_levels = ["simple", "balanced", "advanced", "technical"]
            if persona_data["language_complexity"] not in valid_levels:
                errors.append(f"Language complexity must be one of: {', '.join(valid_levels)}")

        # Citation style validation
        if "citation_style" in persona_data:
            valid_styles = ["inline", "footnotes", "endnotes", "apa", "mla", "chicago"]
            if persona_data["citation_style"] not in valid_styles:
                errors.append(f"Citation style must be one of: {', '.join(valid_styles)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _count_user_personas(self, session: AsyncSession, user_id: str) -> int:
        """Count the number of custom personas for a user."""
        try:
            from sqlalchemy import func
            count_query = session.query(func.count(ResearchTemplate.id)).filter(
                ResearchTemplate.created_by == user_id,
                ResearchTemplate.category == "custom_persona"
            )
            result = await session.execute(count_query)
            return result.scalar() or 0
        except Exception:
            return 0

    async def _count_public_personas(self, session: AsyncSession) -> int:
        """Count the number of public personas."""
        try:
            from sqlalchemy import func
            count_query = session.query(func.count(ResearchTemplate.id)).filter(
                ResearchTemplate.category == "custom_persona",
                ResearchTemplate.is_public == True
            )
            result = await session.execute(count_query)
            return result.scalar() or 0
        except Exception:
            return 0

    def get_persona_template(self, template_type: str = "basic") -> Dict[str, Any]:
        """
        Get a template for creating custom personas.

        Args:
            template_type: Type of template to return

        Returns:
            Persona template
        """
        templates = {
            "basic": {
                "name": "My Custom Persona",
                "description": "A custom writing persona tailored to my preferences",
                "personality_traits": {
                    "tone": "professional",
                    "formality": "balanced",
                    "verbosity": "concise"
                },
                "writing_style": {
                    "structure": "logical flow",
                    "language": "clear and accessible"
                },
                "content_focus": ["clarity", "accuracy", "practicality"],
                "tone_preferences": ["objective", "helpful"],
                "language_complexity": "balanced",
                "citation_style": "inline"
            },
            "academic": {
                "name": "Academic Researcher",
                "description": "Formal academic writing style for research papers",
                "personality_traits": {
                    "tone": "formal",
                    "objectivity": "high",
                    "rigor": "maximum"
                },
                "writing_style": {
                    "structure": "IMRAD format",
                    "language": "precise and technical"
                },
                "content_focus": ["methodology", "evidence", "analysis"],
                "tone_preferences": ["objective", "scholarly"],
                "language_complexity": "advanced",
                "citation_style": "apa"
            },
            "creative": {
                "name": "Storytelling Writer",
                "description": "Engaging narrative style for creative content",
                "personality_traits": {
                    "tone": "engaging",
                    "creativity": "high",
                    "narrative": "strong"
                },
                "writing_style": {
                    "structure": "story-driven",
                    "language": "vivid and descriptive"
                },
                "content_focus": ["engagement", "emotion", "connection"],
                "tone_preferences": ["conversational", "inspiring"],
                "language_complexity": "balanced",
                "citation_style": "inline"
            }
        }

        return templates.get(template_type, templates["basic"])

    async def get_persona_usage_stats(self, session: AsyncSession,
                                    persona_id: str) -> Dict[str, Any]:
        """
        Get usage statistics for a persona.

        Args:
            session: Database session
            persona_id: Persona identifier

        Returns:
            Usage statistics
        """
        try:
            # This would integrate with analytics to track persona usage
            # For now, return basic stats from the persona record
            persona_query = session.query(ResearchTemplate).filter(
                ResearchTemplate.id == persona_id
            )

            result = await session.execute(persona_query)
            persona = result.scalar_one_or_none()

            if not persona:
                return {"error": "Persona not found"}

            return {
                "persona_id": str(persona.id),
                "name": persona.name,
                "usage_count": persona.usage_count,
                "is_public": persona.is_public,
                "created_at": persona.created_at.isoformat(),
                "last_used": persona.updated_at.isoformat() if persona.updated_at else None
            }

        except Exception as e:
            logger.error(f"Failed to get persona usage stats: {e}")
            return {"error": str(e)}
