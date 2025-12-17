"""
E2E Test Configuration for Playwright
======================================

Provides fixtures for Playwright browser testing.
"""

import pytest
from playwright.sync_api import Page, Browser, BrowserContext

# Base URL for the frontend application
BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with default viewport"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "base_url": BASE_URL,
    }


@pytest.fixture(scope="session")
def mobile_context_args():
    """Mobile viewport configuration"""
    return {
        "viewport": {"width": 375, "height": 667},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        "has_touch": True,
        "is_mobile": True,
    }


@pytest.fixture(scope="session")
def tablet_context_args():
    """Tablet viewport configuration"""
    return {
        "viewport": {"width": 768, "height": 1024},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        "has_touch": True,
    }


# Note: Don't override base_url - use pytest-playwright's built-in fixture
# Set base_url via command line: pytest --base-url http://localhost:3000


@pytest.fixture(scope="session")
def api_url():
    """API URL"""
    return API_URL


@pytest.fixture
def desktop_page(browser: Browser):
    """Desktop browser page"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def mobile_page(browser: Browser, mobile_context_args):
    """Mobile browser page"""
    context = browser.new_context(**mobile_context_args)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def tablet_page(browser: Browser, tablet_context_args):
    """Tablet browser page"""
    context = browser.new_context(**tablet_context_args)
    page = context.new_page()
    yield page
    context.close()


def pytest_configure(config):
    """Configure pytest markers for E2E tests"""
    config.addinivalue_line("markers", "e2e: End-to-end browser tests")
    config.addinivalue_line("markers", "desktop: Desktop viewport tests")
    config.addinivalue_line("markers", "mobile: Mobile viewport tests")
    config.addinivalue_line("markers", "tablet: Tablet viewport tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
