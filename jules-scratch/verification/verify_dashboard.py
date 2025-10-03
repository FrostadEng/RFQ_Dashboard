from playwright.sync_api import sync_playwright, expect

def run(playwright):
    """
    This script verifies that the refactored RFQ Dashboard loads correctly.
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the running Streamlit application
    page.goto("http://localhost:8501", timeout=60000)

    # Wait for a key element to be visible, indicating the app has loaded.
    # We'll wait for the main title of the dashboard.
    expect(page.get_by_role("heading", name="RFQ Dashboard")).to_be_visible(timeout=30000)

    # Instead of looking for the collapsed label, we'll look for a specific, visible project radio button.
    # This confirms that the data connection and initial render are working.
    expect(page.get_by_role("radio", name="Project 12345")).to_be_visible(timeout=30000)

    # Take a screenshot of the initial state
    page.screenshot(path="jules-scratch/verification/verification.png")

    # Clean up
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)