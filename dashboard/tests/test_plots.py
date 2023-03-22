import os
import time

from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(os.getenv('DASHBOARD_HOST', "http://localhost:8501/"))

    # Do search
    search_bar = page.get_by_placeholder("Wat zoek je?")
    search_bar.fill("cyber")
    search_bar.press("Enter")

    time.sleep(3)
    page.get_by_role("tab", name="Grafieken 📊").click()

    # Expect screenshots
    expect(page.locator("div[role='tabpanel'] img")).to_have_count(4, timeout=60000)

    for i in range(0, 4):
        page.get_by_role("img", name="0").nth(i).screenshot(path=f"./dashboard/tests/screenshots/plots_{i}.png")

    # ---------------------
    context.close()
    browser.close()

    assert True, 'Test passed'


def test_plots():
    with sync_playwright() as playwright:
        run(playwright)
