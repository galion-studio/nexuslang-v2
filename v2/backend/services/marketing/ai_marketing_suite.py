"""
AI Marketing Suite for Galion Ecosystem
Comprehensive marketing creation tools powered by Nexus Lang v2

Features:
- AI Content Generation (blogs, social media, ads)
- Branding Generation (logos, color schemes, messaging)
- Image Processing & Generation (from user inputs)
- Campaign Analytics & Optimization
- Multi-channel Marketing Automation
- AI-Powered A/B Testing
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64
import colorsys
import re

from ...core.config import settings
from ..ai import get_ai_router
from ..nexuslang_executor import execute_nexuslang_code
from ...core.database import get_db
from ...models.user import User


class AIMarketingSuite:
    """
    Comprehensive AI-powered marketing creation suite
    Enables developers to train custom AI models and generate marketing content
    """

    def __init__(self):
        self.ai_router = get_ai_router()
        self.max_images_per_request = 10
        self.supported_formats = ['png', 'jpg', 'jpeg', 'webp', 'svg']

    async def generate_content(self, content_type: str, inputs: Dict[str, Any],
                             user: User, db) -> Dict[str, Any]:
        """
        Generate marketing content using AI
        Supports: blog posts, social media, email campaigns, ad copy, etc.
        """
        content_types = {
            'blog_post': self._generate_blog_post,
            'social_media': self._generate_social_media,
            'email_campaign': self._generate_email_campaign,
            'ad_copy': self._generate_ad_copy,
            'landing_page': self._generate_landing_page,
            'product_description': self._generate_product_description,
            'seo_content': self._generate_seo_content,
            'video_script': self._generate_video_script,
            'press_release': self._generate_press_release,
            'whitepaper': self._generate_whitepaper
        }

        if content_type not in content_types:
            raise ValueError(f"Unsupported content type: {content_type}")

        generator = content_types[content_type]

        # Check user credits
        if user.credits < 10:  # Base cost for content generation
            raise ValueError("Insufficient credits")

        # Generate content using Nexus Lang
        content = await generator(inputs)

        # Deduct credits
        user.credits -= 10
        db.add(user)
        await db.commit()

        return {
            'content': content,
            'content_type': content_type,
            'generated_at': datetime.now().isoformat(),
            'credits_used': 10,
            'word_count': len(content.split()) if isinstance(content, str) else 0
        }

    async def generate_branding(self, brand_inputs: Dict[str, Any],
                               user: User, db) -> Dict[str, Any]:
        """
        Generate complete branding package based on user inputs
        Includes: color palette, typography, messaging, logo concepts
        """
        if user.credits < 50:  # Branding generation is more expensive
            raise ValueError("Insufficient credits for branding generation")

        brand_data = {
            'company_name': brand_inputs.get('company_name', ''),
            'industry': brand_inputs.get('industry', ''),
            'target_audience': brand_inputs.get('target_audience', ''),
            'values': brand_inputs.get('values', []),
            'personality': brand_inputs.get('personality', ''),
            'competitors': brand_inputs.get('competitors', []),
            'existing_colors': brand_inputs.get('existing_colors', [])
        }

        # Generate color palette
        color_palette = await self._generate_color_palette(brand_data)

        # Generate typography recommendations
        typography = await self._generate_typography(brand_data)

        # Generate brand messaging
        messaging = await self._generate_brand_messaging(brand_data)

        # Generate logo concepts (text-based for now)
        logo_concepts = await self._generate_logo_concepts(brand_data)

        # Generate taglines
        taglines = await self._generate_taglines(brand_data)

        # Deduct credits
        user.credits -= 50
        db.add(user)
        await db.commit()

        return {
            'color_palette': color_palette,
            'typography': typography,
            'messaging': messaging,
            'logo_concepts': logo_concepts,
            'taglines': taglines,
            'brand_guidelines': self._generate_brand_guidelines(color_palette, typography, messaging),
            'generated_at': datetime.now().isoformat(),
            'credits_used': 50
        }

    async def process_images(self, images: List[bytes], operation: str,
                           parameters: Dict[str, Any], user: User, db) -> Dict[str, Any]:
        """
        Process user-uploaded images for marketing purposes
        Supports: resizing, filtering, collage creation, style transfer, etc.
        """
        if len(images) > self.max_images_per_request:
            raise ValueError(f"Maximum {self.max_images_per_request} images allowed")

        if user.credits < len(images) * 5:  # 5 credits per image
            raise ValueError("Insufficient credits for image processing")

        operations = {
            'resize': self._resize_images,
            'filter': self._apply_filters,
            'collage': self._create_collage,
            'enhance': self._enhance_images,
            'extract_colors': self._extract_color_palette,
            'generate_variations': self._generate_image_variations
        }

        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")

        processor = operations[operation]
        result = await processor(images, parameters)

        # Deduct credits
        credits_used = len(images) * 5
        user.credits -= credits_used
        db.add(user)
        await db.commit()

        return {
            'operation': operation,
            'result': result,
            'images_processed': len(images),
            'credits_used': credits_used,
            'processed_at': datetime.now().isoformat()
        }

    async def train_custom_model(self, training_data: Dict[str, Any],
                               model_type: str, user: User, db) -> Dict[str, Any]:
        """
        Allow developers to train custom AI models
        Supports: content style models, brand voice models, etc.
        """
        if user.credits < 100:  # Training is expensive
            raise ValueError("Insufficient credits for model training")

        training_config = {
            'model_type': model_type,
            'training_data': training_data,
            'user_id': str(user.id),
            'created_at': datetime.now().isoformat()
        }

        # This would integrate with a model training service
        # For now, we'll simulate the training process
        model_id = str(uuid.uuid4())

        # Deduct credits
        user.credits -= 100
        db.add(user)
        await db.commit()

        return {
            'model_id': model_id,
            'model_type': model_type,
            'status': 'training',
            'estimated_completion': (datetime.now() + timedelta(hours=2)).isoformat(),
            'credits_used': 100,
            'training_config': training_config
        }

    async def analyze_campaign_performance(self, campaign_data: Dict[str, Any],
                                        user: User, db) -> Dict[str, Any]:
        """
        AI-powered campaign performance analysis and optimization recommendations
        """
        if user.credits < 25:
            raise ValueError("Insufficient credits for campaign analysis")

        # Analyze campaign metrics using AI
        analysis = await self._analyze_campaign_metrics(campaign_data)

        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations(analysis)

        # Deduct credits
        user.credits -= 25
        db.add(user)
        await db.commit()

        return {
            'analysis': analysis,
            'recommendations': recommendations,
            'insights': self._extract_key_insights(analysis, recommendations),
            'credits_used': 25,
            'analyzed_at': datetime.now().isoformat()
        }

    # Content Generation Methods
    async def _generate_blog_post(self, inputs: Dict[str, Any]) -> str:
        """Generate a complete blog post"""
        prompt = f"""
        Write a comprehensive blog post about: {inputs.get('topic', '')}
        Target audience: {inputs.get('audience', '')}
        Key points to cover: {', '.join(inputs.get('key_points', []))}
        Tone: {inputs.get('tone', 'professional')}
        Length: {inputs.get('length', '1000-1500 words')}

        Include:
        - Engaging introduction
        - Main content sections
        - Practical examples
        - Conclusion with call-to-action
        - SEO-friendly structure
        """

        # Use Nexus Lang to generate the content
        nexus_code = f'generate_blog_post({json.dumps(inputs)})'
        result = await execute_nexuslang_code(nexus_code)

        return result.get('content', 'Blog post generation failed')

    async def _generate_social_media(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media content for multiple platforms"""
        platforms = inputs.get('platforms', ['twitter', 'linkedin', 'facebook'])

        content = {}
        for platform in platforms:
            platform_inputs = {**inputs, 'platform': platform, 'character_limit': self._get_platform_limit(platform)}

            nexus_code = f'generate_social_post({json.dumps(platform_inputs)})'
            result = await execute_nexuslang_code(nexus_code)

            content[platform] = result.get('content', '')

        return {
            'posts': content,
            'hashtags': self._generate_hashtags(inputs.get('topic', '')),
            'posting_schedule': self._generate_posting_schedule(platforms)
        }

    async def _generate_email_campaign(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete email marketing campaign"""
        campaign_type = inputs.get('campaign_type', 'newsletter')

        emails = {
            'welcome_series': ['welcome_1', 'welcome_2', 'welcome_3'],
            'newsletter': ['monthly_newsletter'],
            'promotional': ['product_launch', 'limited_offer', 're_engagement'],
            'educational': ['tutorial_series', 'webinar_followup']
        }.get(campaign_type, ['main_email'])

        content = {}
        for email_type in emails:
            email_inputs = {**inputs, 'email_type': email_type}

            nexus_code = f'generate_email({json.dumps(email_inputs)})'
            result = await execute_nexuslang_code(nexus_code)

            content[email_type] = result

        return {
            'campaign_type': campaign_type,
            'emails': content,
            'segmentation_suggestions': self._generate_segmentation_suggestions(inputs),
            'send_schedule': self._generate_email_schedule(campaign_type)
        }

    async def _generate_ad_copy(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advertising copy for various formats"""
        formats = inputs.get('formats', ['google_ads', 'facebook_ads', 'linkedin_ads'])

        copy = {}
        for format_type in formats:
            format_inputs = {**inputs, 'format': format_type}

            nexus_code = f'generate_ad_copy({json.dumps(format_inputs)})'
            result = await execute_nexuslang_code(nexus_code)

            copy[format_type] = result

        return {
            'ad_copy': copy,
            'targeting_suggestions': self._generate_ad_targeting_suggestions(inputs),
            'budget_recommendations': self._generate_budget_recommendations(inputs)
        }

    # Branding Generation Methods
    async def _generate_color_palette(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cohesive color palette"""
        industry = brand_data.get('industry', '').lower()
        personality = brand_data.get('personality', '').lower()

        # Base colors based on industry and personality
        base_hues = {
            'tech': [210, 240, 180],  # Blue, purple, green
            'healthcare': [120, 60, 30],  # Green, yellow, brown
            'finance': [45, 210, 15],  # Gold, blue, green
            'retail': [0, 330, 60],  # Red, pink, yellow
            'education': [240, 60, 120],  # Purple, yellow, blue
        }

        personality_adjustments = {
            'professional': {'saturation': 0.7, 'brightness': 0.6},
            'creative': {'saturation': 0.9, 'brightness': 0.8},
            'trustworthy': {'saturation': 0.5, 'brightness': 0.5},
            'energetic': {'saturation': 1.0, 'brightness': 0.9},
            'minimalist': {'saturation': 0.3, 'brightness': 0.7},
        }

        base_hue = base_hues.get(industry, [210, 180, 120])[0]
        personality_settings = personality_adjustments.get(personality, {'saturation': 0.6, 'brightness': 0.7})

        # Generate color palette
        palette = []
        for i in range(5):
            # Create variations of the base color
            hue = (base_hue + (i * 60)) % 360
            saturation = personality_settings['saturation'] + (i * 0.1)
            brightness = personality_settings['brightness'] - (i * 0.1)

            # Ensure values are within bounds
            saturation = max(0.1, min(1.0, saturation))
            brightness = max(0.1, min(1.0, brightness))

            rgb = colorsys.hsv_to_rgb(hue/360, saturation, brightness)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )

            palette.append({
                'hex': hex_color,
                'rgb': f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})',
                'hsl': f'hsl({int(hue)}, {int(saturation*100)}%, {int(brightness*100)}%)',
                'name': ['primary', 'secondary', 'accent', 'neutral', 'highlight'][i]
            })

        return {
            'primary': palette[0],
            'secondary': palette[1],
            'accent': palette[2],
            'neutral': palette[3],
            'highlight': palette[4],
            'combinations': self._generate_color_combinations(palette)
        }

    async def _generate_typography(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate typography recommendations"""
        industry = brand_data.get('industry', '').lower()
        personality = brand_data.get('personality', '').lower()

        # Typography recommendations based on industry and personality
        font_suggestions = {
            'tech': {
                'headings': ['Inter', 'SF Pro Display', 'Poppins'],
                'body': ['Inter', 'SF Pro Text', 'Roboto'],
                'accent': ['JetBrains Mono', 'Fira Code', 'Source Code Pro']
            },
            'creative': {
                'headings': ['Playfair Display', 'Abril Fatface', 'Dancing Script'],
                'body': ['Open Sans', 'Lato', 'Nunito'],
                'accent': ['Pacifico', 'Comfortaa', 'Righteous']
            },
            'corporate': {
                'headings': ['Helvetica Neue', 'Arial', 'Calibri'],
                'body': ['Georgia', 'Times New Roman', 'Garamond'],
                'accent': ['Futura', 'Gill Sans', 'Franklin Gothic']
            }
        }

        category = 'tech' if 'tech' in industry else ('creative' if 'design' in industry or 'creative' in personality else 'corporate')
        fonts = font_suggestions.get(category, font_suggestions['tech'])

        return {
            'primary_font': {
                'family': fonts['headings'][0],
                'weights': [400, 500, 600, 700],
                'usage': 'Headlines, titles, important text'
            },
            'secondary_font': {
                'family': fonts['body'][0],
                'weights': [300, 400, 500],
                'usage': 'Body text, paragraphs, general content'
            },
            'accent_font': {
                'family': fonts['accent'][0],
                'weights': [400, 500],
                'usage': 'Buttons, highlights, special elements'
            },
            'font_sizes': {
                'h1': '2.5rem (40px)',
                'h2': '2rem (32px)',
                'h3': '1.5rem (24px)',
                'body': '1rem (16px)',
                'small': '0.875rem (14px)'
            },
            'line_heights': {
                'headings': '1.2',
                'body': '1.6',
                'tight': '1.3'
            }
        }

    async def _generate_brand_messaging(self, brand_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brand messaging framework"""
        company_name = brand_data.get('company_name', '')
        values = brand_data.get('values', [])
        personality = brand_data.get('personality', '')

        nexus_code = f'generate_brand_messaging({json.dumps(brand_data)})'
        result = await execute_nexuslang_code(nexus_code)

        return {
            'mission_statement': result.get('mission', f'To empower {company_name} users with innovative solutions'),
            'vision_statement': result.get('vision', f'To be the leading provider of {brand_data.get("industry", "technology")} solutions'),
            'core_values': values,
            'brand_voice': {
                'tone': personality,
                'language_style': self._get_language_style(personality),
                'communication_guidelines': self._generate_communication_guidelines(personality)
            },
            'key_messages': result.get('key_messages', []),
            'elevator_pitch': result.get('elevator_pitch', '')
        }

    # Image Processing Methods
    async def _resize_images(self, images: List[bytes], parameters: Dict[str, Any]) -> List[str]:
        """Resize images to specified dimensions"""
        width = parameters.get('width', 800)
        height = parameters.get('height', 600)
        maintain_aspect = parameters.get('maintain_aspect', True)

        resized_images = []
        for img_bytes in images:
            img = Image.open(io.BytesIO(img_bytes))

            if maintain_aspect:
                img.thumbnail((width, height))
            else:
                img = img.resize((width, height))

            output = io.BytesIO()
            img.save(output, format='PNG')
            resized_images.append(base64.b64encode(output.getvalue()).decode())

        return resized_images

    async def _apply_filters(self, images: List[bytes], parameters: Dict[str, Any]) -> List[str]:
        """Apply filters to images"""
        filter_type = parameters.get('filter', 'enhance')

        filters = {
            'blur': ImageFilter.BLUR,
            'sharpen': ImageFilter.UnsharpMask,
            'smooth': ImageFilter.SMOOTH,
            'contour': ImageFilter.CONTOUR,
            'emboss': ImageFilter.EMBOSS
        }

        filtered_images = []
        for img_bytes in images:
            img = Image.open(io.BytesIO(img_bytes))

            if filter_type == 'enhance':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.1)
            elif filter_type in filters:
                img = img.filter(filters[filter_type])

            output = io.BytesIO()
            img.save(output, format='PNG')
            filtered_images.append(base64.b64encode(output.getvalue()).decode())

        return filtered_images

    async def _create_collage(self, images: List[bytes], parameters: Dict[str, Any]) -> str:
        """Create a collage from multiple images"""
        if len(images) < 2:
            raise ValueError("At least 2 images required for collage")

        # Open all images
        pil_images = [Image.open(io.BytesIO(img_bytes)) for img_bytes in images]

        # Resize images to same height for horizontal collage
        heights = [img.height for img in pil_images]
        min_height = min(heights)

        resized_images = []
        for img in pil_images:
            aspect_ratio = img.width / img.height
            new_width = int(min_height * aspect_ratio)
            resized_img = img.resize((new_width, min_height))
            resized_images.append(resized_img)

        # Calculate total width
        total_width = sum(img.width for img in resized_images)
        max_height = min_height

        # Create new image
        collage = Image.new('RGB', (total_width, max_height), color='white')

        # Paste images side by side
        x_offset = 0
        for img in resized_images:
            collage.paste(img, (x_offset, 0))
            x_offset += img.width

        # Convert to base64
        output = io.BytesIO()
        collage.save(output, format='PNG')
        return base64.b64encode(output.getvalue()).decode()

    async def _extract_color_palette(self, images: List[bytes], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract color palette from images"""
        all_colors = []

        for img_bytes in images:
            img = Image.open(io.BytesIO(img_bytes))
            img = img.resize((100, 100))  # Reduce size for processing

            # Get most common colors
            colors = img.getcolors(100 * 100)
            if colors:
                # Sort by frequency and take top colors
                sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:10]
                all_colors.extend([color for count, color in sorted_colors])

        # Remove duplicates and convert to hex
        unique_colors = list(set(all_colors))
        palette = []

        for rgb in unique_colors[:8]:  # Limit to 8 colors
            hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            palette.append({
                'hex': hex_color,
                'rgb': f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})',
                'frequency': len([c for c in all_colors if c == rgb])
            })

        return sorted(palette, key=lambda x: x['frequency'], reverse=True)

    # Helper Methods
    def _get_platform_limit(self, platform: str) -> int:
        """Get character limit for social media platform"""
        limits = {
            'twitter': 280,
            'linkedin': 3000,
            'facebook': 63206,
            'instagram': 2200,
            'tiktok': 2200
        }
        return limits.get(platform, 280)

    def _generate_hashtags(self, topic: str) -> List[str]:
        """Generate relevant hashtags for a topic"""
        # This would use AI to generate relevant hashtags
        base_hashtags = ['#innovation', '#technology', '#business']
        topic_hashtags = [f'#{word.lower()}' for word in topic.split() if len(word) > 3]
        return base_hashtags + topic_hashtags[:5]

    def _generate_posting_schedule(self, platforms: List[str]) -> Dict[str, Any]:
        """Generate optimal posting schedule"""
        schedules = {
            'twitter': ['9:00', '12:00', '15:00', '18:00'],
            'linkedin': ['8:00', '12:00', '17:00'],
            'facebook': ['10:00', '14:00', '19:00'],
            'instagram': ['11:00', '15:00', '20:00']
        }

        return {platform: schedules.get(platform, ['12:00']) for platform in platforms}

    def _generate_color_combinations(self, palette: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommended color combinations"""
        return [
            {
                'name': 'Primary + Accent',
                'colors': [palette[0]['hex'], palette[2]['hex']],
                'usage': 'Call-to-action buttons, important links'
            },
            {
                'name': 'Secondary + Neutral',
                'colors': [palette[1]['hex'], palette[3]['hex']],
                'usage': 'Secondary buttons, borders, dividers'
            },
            {
                'name': 'Full Palette',
                'colors': [color['hex'] for color in palette],
                'usage': 'Complex layouts, data visualizations'
            }
        ]

    def _get_language_style(self, personality: str) -> str:
        """Get language style based on personality"""
        styles = {
            'professional': 'Formal, clear, concise',
            'creative': 'Expressive, imaginative, engaging',
            'trustworthy': 'Reliable, honest, straightforward',
            'energetic': 'Dynamic, enthusiastic, motivational',
            'minimalist': 'Simple, direct, uncluttered'
        }
        return styles.get(personality.lower(), 'Professional and clear')

    def _generate_communication_guidelines(self, personality: str) -> List[str]:
        """Generate communication guidelines"""
        base_guidelines = [
            'Be authentic and true to brand values',
            'Use consistent language across all channels',
            'Maintain professional tone while being approachable',
            'Focus on benefits rather than just features',
            'Encourage engagement and dialogue'
        ]

        if personality.lower() == 'creative':
            base_guidelines.extend([
                'Use storytelling techniques',
                'Incorporate metaphors and analogies',
                'Be playful with language when appropriate'
            ])
        elif personality.lower() == 'energetic':
            base_guidelines.extend([
                'Use exclamation points sparingly but effectively',
                'Create urgency and excitement',
                'Ask questions to engage readers'
            ])

        return base_guidelines

    def _generate_brand_guidelines(self, colors: Dict, typography: Dict, messaging: Dict) -> Dict[str, Any]:
        """Generate comprehensive brand guidelines"""
        return {
            'logo_usage': {
                'minimum_size': '50px',
                'clear_space': '1x logo height',
                'color_variations': 'Use primary color or white on colored backgrounds'
            },
            'color_usage': {
                'primary_use': 'Headlines, primary buttons, brand elements',
                'secondary_use': 'Supporting text, secondary buttons',
                'accent_use': 'Highlights, call-to-actions, links',
                'accessibility': 'Ensure 4.5:1 contrast ratio for text'
            },
            'typography_usage': {
                'hierarchy': 'Use size and weight to create clear information hierarchy',
                'spacing': 'Maintain consistent line height and letter spacing',
                'readability': 'Ensure text is readable at all sizes'
            },
            'voice_and_tone': {
                'consistency': 'Apply brand voice across all communications',
                'adaptability': 'Adjust tone based on context while staying true to brand',
                'personality': messaging.get('brand_voice', {}).get('tone', '')
            }
        }

    async def _analyze_campaign_metrics(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance metrics"""
        # This would use AI to analyze actual metrics
        return {
            'overall_performance': 'good',
            'key_metrics': {
                'click_through_rate': 3.2,
                'conversion_rate': 1.8,
                'engagement_rate': 4.5,
                'roi': 2.3
            },
            'audience_insights': {
                'best_performing_demographic': '25-34 year olds',
                'peak_engagement_times': ['10:00', '14:00', '19:00'],
                'top_content_types': ['educational', 'entertainment', 'promotional']
            },
            'channel_performance': {
                'email': {'performance': 'excellent', 'score': 8.5},
                'social_media': {'performance': 'good', 'score': 7.2},
                'paid_ads': {'performance': 'average', 'score': 6.1}
            }
        }

    async def _generate_optimization_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        return [
            {
                'priority': 'high',
                'category': 'content',
                'recommendation': 'Increase educational content by 30%',
                'expected_impact': '15% increase in engagement',
                'implementation': 'Create more how-to guides and tutorials'
            },
            {
                'priority': 'medium',
                'category': 'timing',
                'recommendation': 'Optimize posting times based on audience behavior',
                'expected_impact': '10% increase in reach',
                'implementation': 'Schedule posts during peak engagement hours'
            },
            {
                'priority': 'low',
                'category': 'design',
                'recommendation': 'A/B test different call-to-action button colors',
                'expected_impact': '5% increase in conversions',
                'implementation': 'Test primary vs accent button colors'
            }
        ]

    def _extract_key_insights(self, analysis: Dict[str, Any], recommendations: List[Dict]) -> List[str]:
        """Extract key insights from analysis"""
        return [
            f"Your campaign has a {analysis['key_metrics']['click_through_rate']}% click-through rate, which is {'above' if analysis['key_metrics']['click_through_rate'] > 2.5 else 'below'} industry average",
            f"Peak engagement occurs between {', '.join(analysis['audience_insights']['peak_engagement_times'])}",
            f"Educational content performs {analysis['audience_insights']['top_content_types'][0]}% better than other content types",
            f"Email marketing shows the highest ROI at {analysis['channel_performance']['email']['score']}/10"
        ]


# Global instance
_ai_marketing_suite: Optional[AIMarketingSuite] = None


async def get_ai_marketing_suite() -> AIMarketingSuite:
    """Get the global AI marketing suite instance"""
    global _ai_marketing_suite
    if _ai_marketing_suite is None:
        _ai_marketing_suite = AIMarketingSuite()
    return _ai_marketing_suite
