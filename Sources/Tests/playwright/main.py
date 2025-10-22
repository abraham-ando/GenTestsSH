"""
Main test file with Playwright tests for project-sample-1
"""
import pytest
import asyncio
from pathlib import Path
from playwright.async_api import Page, expect

from test_runner import AutoHealTestRunner

# Base URL for the sample project
BASE_URL = "file://" + str(Path(__file__).parent.parent.parent / "src" / "project-sample-1")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def runner():
    """Fixture for AutoHealTestRunner"""
    runner = AutoHealTestRunner()
    await runner.setup()
    yield runner
    await runner.teardown()


class TestLoginPage:
    """Test suite for login page"""

    async def test_login_success(self, runner: AutoHealTestRunner):
        """Test successful login"""
        async def test_func(page: Page):
            # Navigate to login page
            await page.goto(f"{BASE_URL}/index.html")

            # Fill in credentials
            await page.fill("#username", "admin")
            await page.fill("#password", "password123")

            # Click submit button
            await page.click("#submit")

            # Wait for dashboard
            await page.wait_for_url("**/dashboard.html", timeout=5000)

            # Verify we're on the dashboard
            await expect(page.locator("h1")).to_contain_text("Bienvenue")

        result = await runner.run_test_with_healing(test_func)
        assert result["status"] == "passed"

    async def test_login_failure(self, runner: AutoHealTestRunner):
        """Test failed login"""
        async def test_func(page: Page):
            await page.goto(f"{BASE_URL}/index.html")

            # Fill in wrong credentials
            await page.fill("#username", "wrong")
            await page.fill("#password", "wrong")

            # Click submit
            await page.click("#submit")

            # Verify error message appears
            await expect(page.locator(".message.error")).to_be_visible()
            await expect(page.locator(".message.error")).to_contain_text("incorrect")

        result = await runner.run_test_with_healing(test_func)
        assert result["status"] == "passed"


class TestDashboard:
    """Test suite for dashboard page"""

    async def test_dashboard_loads(self, runner: AutoHealTestRunner):
        """Test dashboard loads correctly"""
        async def test_func(page: Page):
            await page.goto(f"{BASE_URL}/dashboard.html")

            # Verify main elements are present
            await expect(page.locator("h1")).to_contain_text("Bienvenue")
            await expect(page.locator(".card")).to_have_count(3)

        result = await runner.run_test_with_healing(test_func)
        assert result["status"] == "passed"

    async def test_logout_button(self, runner: AutoHealTestRunner):
        """Test logout button"""
        async def test_func(page: Page):
            await page.goto(f"{BASE_URL}/dashboard.html")

            # Click logout
            await page.click("#logout-btn")

            # Should redirect to login
            await page.wait_for_url("**/index.html", timeout=5000)

        result = await runner.run_test_with_healing(test_func)
        assert result["status"] == "passed"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])

