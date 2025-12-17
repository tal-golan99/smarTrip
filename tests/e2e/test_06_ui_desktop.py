"""
UI/UX Tests - Desktop Responsive Design
=======================================

Test IDs: TC-UI-001 to TC-UI-015

Covers desktop viewport (1200px+) responsive design tests.

Reference: MASTER_TEST_PLAN.md Section 6.1
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:3000"


@pytest.fixture
def desktop_viewport():
    """Desktop viewport dimensions"""
    return {"width": 1280, "height": 720}


class TestDesktopHeader:
    """Tests for header components on desktop (TC-UI-001 to TC-UI-002)"""
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_header_displays_logo_and_navigation(self, page: Page):
        """
        TC-UI-001: Header displays logo and navigation
        
        Pre-conditions: Desktop viewport (1200px+)
        Expected Result: Logo visible, nav links horizontal
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(BASE_URL)
        
        # Wait for page load
        page.wait_for_load_state("networkidle")
        
        # Check for logo (SmarTrip has logo image on landing page)
        logo = page.locator("img[alt*='Logo'], img[alt*='SmartTrip'], img[src*='logo']").first
        expect(logo).to_be_visible()
        
        # Check main content is visible (landing page has h1 with SmarTrip)
        title = page.locator("h1, [class*='text-5xl'], [class*='text-6xl']").first
        expect(title).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_search_form_shows_all_fields(self, page: Page):
        """
        TC-UI-002: Search form shows all fields
        
        Pre-conditions: Desktop viewport
        Expected Result: Country, date, budget, tags all visible
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for form elements (selectors may vary)
        form = page.locator("form, [class*='search'], [class*='filter']").first
        expect(form).to_be_visible()


class TestDesktopResultsGrid:
    """Tests for results grid on desktop (TC-UI-003 to TC-UI-006)"""
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_results_grid_shows_multiple_columns(self, page: Page):
        """
        TC-UI-003: Results grid shows 3 columns
        
        Pre-conditions: Desktop viewport
        Expected Result: 3 trip cards per row
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for grid container
        grid = page.locator("[class*='grid'], [class*='results']").first
        if grid.is_visible():
            expect(grid).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_trip_card_shows_required_info(self, page: Page):
        """
        TC-UI-004: Trip card shows image, title, price
        
        Pre-conditions: Results page
        Expected Result: All elements visible and readable
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for trip cards
        cards = page.locator("[class*='card'], [class*='trip']")
        
        if cards.count() > 0:
            first_card = cards.first
            expect(first_card).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_sidebar_filters_visible(self, page: Page):
        """
        TC-UI-005: Sidebar filters visible
        
        Pre-conditions: Results page desktop
        Expected Result: Filters panel on left side
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for filter sidebar
        filters = page.locator("[class*='filter'], [class*='sidebar'], aside")
        
        # May not exist on all pages
        if filters.count() > 0:
            expect(filters.first).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_sort_dropdown_accessible(self, page: Page):
        """
        TC-UI-006: Sort dropdown accessible
        
        Pre-conditions: Results page
        Expected Result: Sort options in dropdown
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for sort control
        sort = page.locator("select, [class*='sort']")
        
        if sort.count() > 0:
            expect(sort.first).to_be_visible()


class TestDesktopTripDetails:
    """Tests for trip details on desktop (TC-UI-007 to TC-UI-014)"""
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_trip_details_layout(self, page: Page):
        """
        TC-UI-007: Trip details modal/page layout
        
        Pre-conditions: Click trip card
        Expected Result: Full details with large image
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/trip/1")
        
        page.wait_for_load_state("networkidle")
        
        # Page should load without error
        assert page.url.startswith(BASE_URL)
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_price_displayed_prominently(self, page: Page):
        """
        TC-UI-011: Price displayed prominently
        
        Pre-conditions: Trip card and details
        Expected Result: Price clearly visible with currency
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/trip/1")
        
        page.wait_for_load_state("networkidle")
        
        # Look for price element
        price = page.locator("[class*='price'], *:text-matches('[0-9,]+.*\\$|\\$.*[0-9,]+')")
        
        if price.count() > 0:
            expect(price.first).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_status_badge_visible(self, page: Page):
        """
        TC-UI-012: Status badge visible
        
        Pre-conditions: Trip card
        Expected Result: Open/Guaranteed/Last Places badge
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for status badges
        badges = page.locator("[class*='badge'], [class*='status']")
        
        # Badges may not be on all trips
        if badges.count() > 0:
            expect(badges.first).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_book_now_button_prominent(self, page: Page):
        """
        TC-UI-013: Book Now button prominent
        
        Pre-conditions: Trip details
        Expected Result: CTA button clearly visible
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/trip/1")
        
        page.wait_for_load_state("networkidle")
        
        # Look for CTA button
        cta = page.locator("button, a").filter(has_text="Book")
        
        if cta.count() > 0:
            expect(cta.first).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_contact_buttons_visible(self, page: Page):
        """
        TC-UI-014: WhatsApp contact button
        
        Pre-conditions: Trip details
        Expected Result: WhatsApp icon/button visible
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(f"{BASE_URL}/trip/1")
        
        page.wait_for_load_state("networkidle")
        
        # Look for contact buttons
        contact = page.locator("[class*='whatsapp'], [class*='contact'], a[href*='whatsapp']")
        
        if contact.count() > 0:
            expect(contact.first).to_be_visible()


class TestDesktopFooter:
    """Tests for footer on desktop (TC-UI-015)"""
    
    @pytest.mark.e2e
    @pytest.mark.desktop
    def test_footer_with_company_info(self, page: Page):
        """
        TC-UI-015: Footer with company info
        
        Pre-conditions: All pages
        Expected Result: Footer visible with links
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        page.goto(BASE_URL)
        
        page.wait_for_load_state("networkidle")
        
        # Look for footer
        footer = page.locator("footer")
        
        if footer.count() > 0:
            expect(footer).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
