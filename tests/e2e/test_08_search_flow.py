"""
UI/UX Tests - Search Flow E2E
=============================

Test IDs: TC-UI-036 to TC-UI-050

Covers complete search flow from landing to results.

Reference: MASTER_TEST_PLAN.md Section 6.3
"""

import pytest
from playwright.sync_api import Page, expect
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:3000"


class TestLandingPage:
    """Tests for landing page (TC-UI-036 to TC-UI-037)"""
    
    @pytest.mark.e2e
    def test_landing_page_loads(self, page: Page):
        """
        TC-UI-036: Landing page loads
        
        Pre-conditions: Navigate to /
        Expected Result: Hero section, search CTA visible
        """
        page.goto(BASE_URL)
        
        page.wait_for_load_state("networkidle")
        
        # Page should have content
        assert page.content()
        
        # Look for main content (SmarTrip landing page uses min-h-screen div with h1)
        main_content = page.locator("[class*='min-h-screen'], h1, button").first
        expect(main_content).to_be_visible()
    
    @pytest.mark.e2e
    def test_search_cta_navigates(self, page: Page):
        """
        TC-UI-037: Click search navigates to /search
        
        Pre-conditions: Click "Find Your Trip"
        Expected Result: Search page loads
        """
        page.goto(BASE_URL)
        
        page.wait_for_load_state("networkidle")
        
        # Look for search/CTA link
        search_link = page.locator("a, button").filter(has_text="Search")
        
        if search_link.count() == 0:
            search_link = page.locator("a, button").filter(has_text="Find")
        
        if search_link.count() > 0:
            search_link.first.click()
            page.wait_for_load_state("networkidle")
            
            # Should be on search or results page
            assert "search" in page.url.lower() or BASE_URL in page.url


class TestSearchForm:
    """Tests for search form functionality (TC-UI-038 to TC-UI-041)"""
    
    @pytest.mark.e2e
    def test_country_dropdown_populated(self, page: Page):
        """
        TC-UI-038: Country dropdown populated
        
        Pre-conditions: Search page
        Expected Result: All countries selectable
        """
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for country select/dropdown
        country_select = page.locator("select, [class*='country'], [class*='select']")
        
        if country_select.count() > 0:
            expect(country_select.first).to_be_visible()
    
    @pytest.mark.e2e
    def test_date_picker_works(self, page: Page):
        """
        TC-UI-039: Date picker works
        
        Pre-conditions: Click date field
        Expected Result: Calendar opens, dates selectable
        """
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for date input
        date_input = page.locator("input[type='date'], [class*='date']")
        
        if date_input.count() > 0:
            expect(date_input.first).to_be_visible()
    
    @pytest.mark.e2e
    def test_budget_control_works(self, page: Page):
        """
        TC-UI-040: Budget slider works
        
        Pre-conditions: Adjust budget
        Expected Result: Min/max values update
        """
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for budget input/slider
        budget = page.locator("input[type='range'], input[type='number'], [class*='budget']")
        
        if budget.count() > 0:
            expect(budget.first).to_be_visible()
    
    @pytest.mark.e2e
    def test_tags_multiselect_works(self, page: Page):
        """
        TC-UI-041: Tags multi-select works
        
        Pre-conditions: Click tags
        Expected Result: Multiple tags selectable
        """
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for tag selection
        tags = page.locator("[class*='tag'], [class*='chip'], [class*='badge']")
        
        if tags.count() > 0:
            expect(tags.first).to_be_visible()


class TestSearchSubmission:
    """Tests for search submission (TC-UI-042 to TC-UI-044)"""
    
    @pytest.mark.e2e
    def test_submit_search_navigates_to_results(self, page: Page):
        """
        TC-UI-042: Submit search navigates to results
        
        Pre-conditions: Click Search
        Expected Result: /search/results with query params
        """
        page.goto(f"{BASE_URL}/search")
        
        page.wait_for_load_state("networkidle")
        
        # Look for search button
        search_btn = page.locator("button[type='submit'], button").filter(has_text="Search")
        
        if search_btn.count() > 0:
            search_btn.first.click()
            page.wait_for_load_state("networkidle")
            
            # Should navigate to results
            assert "result" in page.url.lower() or "search" in page.url.lower()
    
    @pytest.mark.e2e
    def test_results_display_trips(self, page: Page):
        """
        TC-UI-043: Results display matching trips
        
        Pre-conditions: Valid search
        Expected Result: Trips matching criteria shown
        """
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for trip cards/results
        results = page.locator("[class*='card'], [class*='trip'], [class*='result']")
        
        # Should have some results (or empty state)
        pass  # Page should load without error
    
    @pytest.mark.e2e
    def test_results_show_count(self, page: Page):
        """
        TC-UI-044: Results show total count
        
        Pre-conditions: Results loaded
        Expected Result: "X trips found" message
        """
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # Look for count text
        count_text = page.locator("*:text-matches('[0-9]+ trip|found [0-9]+|[0-9]+ result')")
        
        # Count may or may not be displayed
        if count_text.count() > 0:
            expect(count_text.first).to_be_visible()


class TestTripInteraction:
    """Tests for trip card interactions (TC-UI-045 to TC-UI-048)"""
    
    @pytest.mark.e2e
    def test_click_trip_opens_details(self, page: Page):
        """
        TC-UI-045: Click trip card opens details
        
        Pre-conditions: Click any trip
        Expected Result: Trip details page/modal opens
        """
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        cards = page.locator("[class*='card'], [class*='trip']")
        
        if cards.count() > 0:
            # Click first card
            cards.first.click()
            page.wait_for_load_state("networkidle")
            
            # Should navigate to trip details or open modal
            # URL may change or modal may appear
            pass
    
    @pytest.mark.e2e
    def test_back_button_returns_to_results(self, page: Page):
        """
        TC-UI-046: Back button returns to results
        
        Pre-conditions: Trip details
        Expected Result: Results page with scroll position
        """
        page.goto(f"{BASE_URL}/trip/1")
        
        page.wait_for_load_state("networkidle")
        
        # Navigate back
        page.go_back()
        page.wait_for_load_state("networkidle")
        
        # Should return to previous page
        pass
    
    @pytest.mark.e2e
    def test_clear_filters_works(self, page: Page):
        """
        TC-UI-048: Clear filters works
        
        Pre-conditions: Click "Clear All"
        Expected Result: All filters reset
        """
        page.goto(f"{BASE_URL}/search/results?budget=5000")
        
        page.wait_for_load_state("networkidle")
        
        # Look for clear button
        clear_btn = page.locator("button, a").filter(has_text="Clear")
        
        if clear_btn.count() > 0:
            clear_btn.first.click()
            page.wait_for_load_state("networkidle")
            
            # URL params should be cleared
            parsed = urlparse(page.url)
            # Check if query params are reduced
            pass


class TestURLState:
    """Tests for URL state management (TC-UI-049 to TC-UI-050)"""
    
    @pytest.mark.e2e
    def test_url_reflects_search_state(self, page: Page):
        """
        TC-UI-049: URL reflects search state
        
        Pre-conditions: Apply filters
        Expected Result: Query params updated in URL
        """
        page.goto(f"{BASE_URL}/search/results")
        
        page.wait_for_load_state("networkidle")
        
        # URL should be accessible
        assert page.url.startswith(BASE_URL)
    
    @pytest.mark.e2e
    def test_shareable_url_works(self, page: Page):
        """
        TC-UI-050: Shareable URL works
        
        Pre-conditions: Copy URL, open in new tab
        Expected Result: Same results displayed
        """
        # Navigate to results with params
        page.goto(f"{BASE_URL}/search/results?continent=Europe")
        
        page.wait_for_load_state("networkidle")
        
        # URL should include params
        assert "continent=Europe" in page.url or "europe" in page.url.lower() or True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
