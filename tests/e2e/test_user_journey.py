"""
End-to-end tests for complete user journeys through the Galion Platform.
Tests the full stack from frontend interactions to backend processing.
"""

import pytest
from playwright.async_api import async_playwright, Page, Browser
import asyncio
from unittest.mock import patch, AsyncMock
import json
import os
import time


class TestUserJourney:
    """Test complete user journeys through the platform"""

    @pytest.fixture(scope="class")
    async def browser_context(self):
        """Set up browser context for e2e tests"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            # Create incognito context for clean testing
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Galion-E2E-Test/1.0'
            )

            yield context

            await context.close()
            await browser.close()

    @pytest.fixture
    async def page(self, browser_context):
        """Create a new page for each test"""
        page = await browser_context.new_page()
        yield page
        await page.close()

    async def setup_platform(self, page: Page):
        """Set up the platform for testing"""
        # Navigate to the platform
        await page.goto("http://localhost:3000")  # Galion.app

        # Wait for the page to load
        await page.wait_for_load_state('networkidle')

        # Set platform data attribute
        await page.evaluate('document.documentElement.setAttribute("data-platform", "galion-app")')

    @pytest.mark.asyncio
    async def test_voice_activation_journey(self, page: Page):
        """Test the complete voice activation user journey"""
        await self.setup_platform(page)

        # Check initial page state
        await page.wait_for_selector('[data-testid="voice-activation"]')

        # Click the voice button
        voice_button = page.locator('[data-testid="voice-button"]').first
        await voice_button.click()

        # Should transition to voice interface
        await page.wait_for_selector('[data-testid="voice-interface"]')

        # Check that greeting is displayed
        greeting = page.locator('[data-testid="voice-greeting"]')
        await expect(greeting).to_contain_text("Hello")

        # Check voice button is present and interactive
        voice_button_active = page.locator('[data-testid="voice-button-active"]')
        await expect(voice_button_active).to_be_visible()

    @pytest.mark.asyncio
    async def test_voice_conversation_flow(self, page: Page):
        """Test a complete voice conversation"""
        await self.setup_platform(page)

        # Activate voice interface
        await page.locator('[data-testid="voice-button"]').first.click()
        await page.wait_for_selector('[data-testid="voice-interface"]')

        # Mock voice input (in real test, would use actual microphone)
        with patch('navigator.mediaDevices.getUserMedia') as mock_get_user_media:
            mock_stream = AsyncMock()
            mock_get_user_media.return_value = mock_stream

            # Start voice input
            await page.locator('[data-testid="start-voice"]').click()

            # Should show listening indicator
            listening_indicator = page.locator('[data-testid="listening-indicator"]')
            await expect(listening_indicator).to_be_visible()

            # Simulate speech input and response
            await page.wait_for_timeout(1000)  # Simulate processing time

            # Check that transcription appears
            transcription = page.locator('[data-testid="transcription"]')
            await expect(transcription).to_be_visible()

            # Check that AI response appears
            ai_response = page.locator('[data-testid="ai-response"]')
            await expect(ai_response).to_be_visible()

    @pytest.mark.asyncio
    async def test_beta_signup_journey(self, page: Page):
        """Test the beta signup user journey"""
        await page.goto("http://localhost:3000")  # Galion.app

        # Navigate to beta signup
        await page.locator('[data-testid="beta-signup-link"]').click()

        # Fill out signup form
        email_input = page.locator('[data-testid="email-input"]')
        await email_input.fill('test@example.com')

        # Submit form
        submit_button = page.locator('[data-testid="signup-submit"]')
        await submit_button.click()

        # Check success message
        success_message = page.locator('[data-testid="signup-success"]')
        await expect(success_message).to_be_visible()

        # Check for waitlist position
        waitlist_position = page.locator('[data-testid="waitlist-position"]')
        await expect(waitlist_position).to_be_visible()

    @pytest.mark.asyncio
    async def test_onboarding_flow(self, page: Page):
        """Test the complete user onboarding flow"""
        await page.goto("http://localhost:3000/onboarding")

        # Step 1: Welcome screen
        welcome_title = page.locator('[data-testid="onboarding-title"]')
        await expect(welcome_title).to_contain_text("Welcome to Galion")

        next_button = page.locator('[data-testid="onboarding-next"]')
        await next_button.click()

        # Step 2: Voice introduction
        voice_title = page.locator('[data-testid="onboarding-title"]')
        await expect(voice_title).to_contain_text("Voice-First Experience")

        await next_button.click()

        # Step 3: Features overview
        features_title = page.locator('[data-testid="onboarding-title"]')
        await expect(features_title).to_contain_text("Powerful Features")

        await next_button.click()

        # Step 4: Ready to start
        ready_title = page.locator('[data-testid="onboarding-title"]')
        await expect(ready_title).to_contain_text("You're All Set")

        finish_button = page.locator('[data-testid="onboarding-finish"]')
        await finish_button.click()

        # Should redirect to voice interface
        await page.wait_for_url("**/voice")
        await expect(page).to_have_url("**/voice")

    @pytest.mark.asyncio
    async def test_developer_platform_journey(self, page: Page):
        """Test developer platform user journey"""
        await page.goto("http://localhost:3001")  # developer.Galion.app

        # Set platform attribute
        await page.evaluate('document.documentElement.setAttribute("data-platform", "developer")')

        # Check IDE interface loads
        await page.wait_for_selector('[data-testid="ide-interface"]')

        # Check file explorer is present
        file_explorer = page.locator('[data-testid="file-explorer"]')
        await expect(file_explorer).to_be_visible()

        # Check editor is present
        editor = page.locator('[data-testid="code-editor"]')
        await expect(editor).to_be_visible()

        # Check terminal is present
        terminal = page.locator('[data-testid="terminal"]')
        await expect(terminal).to_be_visible()

    @pytest.mark.asyncio
    async def test_admin_dev_interface(self, page: Page):
        """Test admin development interface"""
        await page.goto("http://localhost:3001/admin/dev-interface")

        # Check admin interface loads
        await page.wait_for_selector('[data-testid="admin-dev-interface"]')

        # Check agent prompt interface
        agent_prompt = page.locator('[data-testid="agent-prompt"]')
        await expect(agent_prompt).to_be_visible()

        # Check file manager
        file_manager = page.locator('[data-testid="file-manager"]')
        await expect(file_manager).to_be_visible()

        # Check agent monitor
        agent_monitor = page.locator('[data-testid="agent-monitor"]')
        await expect(agent_monitor).to_be_visible()

    @pytest.mark.asyncio
    async def test_cross_platform_navigation(self, page: Page):
        """Test navigation between different platform components"""
        # Start at Galion.app
        await page.goto("http://localhost:3000")

        # Navigate to developer platform
        dev_link = page.locator('[data-testid="developer-platform-link"]')
        await dev_link.click()

        # Should navigate to developer platform
        await page.wait_for_url("http://localhost:3001")
        await expect(page).to_have_url("http://localhost:3001")

        # Navigate back to main platform
        main_link = page.locator('[data-testid="main-platform-link"]')
        await main_link.click()

        # Should navigate back
        await page.wait_for_url("http://localhost:3000")
        await expect(page).to_have_url("http://localhost:3000")

    @pytest.mark.asyncio
    async def test_responsive_design(self, page: Page):
        """Test responsive design across different screen sizes"""
        await self.setup_platform(page)

        # Test mobile viewport
        await page.set_viewport_size({'width': 375, 'height': 667})
        await page.reload()

        # Check mobile layout
        mobile_menu = page.locator('[data-testid="mobile-menu"]')
        await expect(mobile_menu).to_be_visible()

        # Test tablet viewport
        await page.set_viewport_size({'width': 768, 'height': 1024})
        await page.reload()

        # Check tablet layout
        tablet_layout = page.locator('[data-testid="tablet-layout"]')
        await expect(tablet_layout).to_be_visible()

        # Test desktop viewport
        await page.set_viewport_size({'width': 1280, 'height': 720})
        await page.reload()

        # Check desktop layout
        desktop_layout = page.locator('[data-testid="desktop-layout"]')
        await expect(desktop_layout).to_be_visible()

    @pytest.mark.asyncio
    async def test_error_handling(self, page: Page):
        """Test error handling and recovery"""
        await self.setup_platform(page)

        # Trigger an error condition (simulate network failure)
        await page.route('**/api/**', lambda route: route.abort())

        # Try to perform an action that requires API
        voice_button = page.locator('[data-testid="voice-button"]')
        await voice_button.click()

        # Check error message appears
        error_message = page.locator('[data-testid="error-message"]')
        await expect(error_message).to_be_visible()

        # Check retry button is available
        retry_button = page.locator('[data-testid="retry-button"]')
        await expect(retry_button).to_be_visible()

        # Test retry functionality
        await retry_button.click()

        # Error should be handled gracefully
        await expect(error_message).not_to_be_visible()

    @pytest.mark.asyncio
    async def test_performance_metrics(self, page: Page):
        """Test performance metrics and loading times"""
        start_time = time.time()

        await page.goto("http://localhost:3000")
        await page.wait_for_load_state('networkidle')

        load_time = time.time() - start_time

        # Page should load within 3 seconds
        assert load_time < 3.0

        # Check Core Web Vitals approximation
        metrics = page.metrics()
        assert 'Timestamp' in metrics

        # Test interaction performance
        interaction_start = time.time()
        voice_button = page.locator('[data-testid="voice-button"]')
        await voice_button.click()

        interaction_time = time.time() - interaction_start

        # Interactions should be responsive (< 100ms)
        assert interaction_time < 0.1

    @pytest.mark.asyncio
    async def test_accessibility(self, page: Page):
        """Test accessibility compliance"""
        await self.setup_platform(page)

        # Run axe-core accessibility tests
        results = await page.accessibility.snapshot()

        # Check for critical accessibility issues
        violations = [node for node in results if node.get('level') == 'error']

        # Should have minimal accessibility violations
        assert len(violations) < 5

        # Test keyboard navigation
        await page.keyboard.press('Tab')
        focused_element = page.locator(':focus')
        await expect(focused_element).to_be_visible()

        # Test screen reader support
        aria_labels = page.locator('[aria-label]')
        count = await aria_labels.count()
        assert count > 0  # Should have ARIA labels

    @pytest.mark.asyncio
    async def test_voice_pipeline_integration(self, page: Page):
        """Test complete voice pipeline integration"""
        await self.setup_platform(page)

        # Activate voice interface
        await page.locator('[data-testid="voice-button"]').first.click()
        await page.wait_for_selector('[data-testid="voice-interface"]')

        # Mock the complete voice pipeline
        with patch('navigator.mediaDevices.getUserMedia') as mock_get_user_media, \
             patch('WebSocket') as mock_ws_class, \
             patch('fetch') as mock_fetch:

            # Mock successful API responses
            mock_fetch.return_value = AsyncMock()
            mock_fetch.return_value.json = AsyncMock(return_value={
                'text': 'Hello, I heard you clearly!',
                'confidence': 0.95
            })

            mock_stream = AsyncMock()
            mock_get_user_media.return_value = mock_stream

            mock_ws = AsyncMock()
            mock_ws_class.return_value = mock_ws

            # Start voice interaction
            start_button = page.locator('[data-testid="start-voice"]')
            await start_button.click()

            # Wait for processing
            await page.wait_for_timeout(2000)

            # Check transcription appears
            transcription = page.locator('[data-testid="transcription-display"]')
            await expect(transcription).to_contain_text('Hello')

            # Check AI response
            ai_response = page.locator('[data-testid="ai-response"]')
            await expect(ai_response).to_be_visible()

            # Check voice synthesis trigger
            tts_trigger = page.locator('[data-testid="tts-active"]')
            await expect(tts_trigger).to_be_visible()

    @pytest.mark.asyncio
    async def test_multi_agent_orchestration(self, page: Page):
        """Test multi-agent orchestration through the UI"""
        await page.goto("http://localhost:3001/admin/dev-interface")

        # Check agent prompt interface
        agent_selector = page.locator('[data-testid="agent-selector"]')
        await expect(agent_selector).to_be_visible()

        # Select financial advisor agent
        await agent_selector.select_option('financial_advisor')

        # Enter a prompt
        prompt_input = page.locator('[data-testid="agent-prompt-input"]')
        await prompt_input.fill('Help me create a budget')

        # Submit prompt
        submit_button = page.locator('[data-testid="agent-submit"]')
        await submit_button.click()

        # Check response appears
        response_area = page.locator('[data-testid="agent-response"]')
        await expect(response_area).to_be_visible()

        # Check agent monitor updates
        agent_status = page.locator('[data-testid="agent-status-financial_advisor"]')
        await expect(agent_status).to_contain_text('active')

    @pytest.mark.asyncio
    async def test_concurrent_users_simulation(self, page: Page, browser_context):
        """Simulate multiple concurrent users"""
        # Create multiple pages for concurrent users
        pages = []
        for i in range(3):
            user_page = await browser_context.new_page()
            pages.append(user_page)

        try:
            # All users navigate to platform
            navigation_tasks = []
            for user_page in pages:
                task = user_page.goto("http://localhost:3000")
                navigation_tasks.append(task)

            await asyncio.gather(*navigation_tasks)

            # All users activate voice
            activation_tasks = []
            for user_page in pages:
                task = user_page.locator('[data-testid="voice-button"]').first.click()
                activation_tasks.append(task)

            await asyncio.gather(*activation_tasks)

            # Check all users can use the platform concurrently
            for user_page in pages:
                voice_interface = user_page.locator('[data-testid="voice-interface"]')
                await expect(voice_interface).to_be_visible()

        finally:
            # Cleanup
            for user_page in pages:
                await user_page.close()


# Custom expect function for better test readability
async def expect(locator):
    """Custom expect function that mimics Playwright's expect"""
    class ExpectWrapper:
        def __init__(self, locator):
            self.locator = locator

        async def to_be_visible(self):
            assert await self.locator.is_visible()

        async def to_contain_text(self, text):
            content = await self.locator.text_content()
            assert text in content

        async def not_to_be_visible(self):
            assert not await self.locator.is_visible()

    return ExpectWrapper(locator)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
