import os
import re

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

    # Expect rows
    expect(page.locator("table tbody tr")).to_have_count(3)

    # Expect Rekenkamer row
    rekenkamer_row = page.locator("table tbody tr").nth(0)
    expect(rekenkamer_row.locator('td')).to_contain_text([
        "26.7",
        "Document title",
        "01-01-2022",
        "Algemene Rekenkamer",
        "Zeer kort",
        "Openen Details"
    ])
    expect(rekenkamer_row.get_by_text("Openen")).to_have_attribute("href", "https://rekenkamer.nl/document")
    expect(rekenkamer_row.get_by_text("Details")).to_have_attribute("href", "https://rekenkamer.nl/detail")

    # Expect Rathenau row
    rathenau_row = page.locator("table tbody tr").nth(1)
    expect(rathenau_row.locator('td')).to_contain_text([
        "1.7",
        "Document title 2",
        "01-02-2022",
        "Rathenau",
        "Kort",
        "Openen Details"
    ])
    expect(rathenau_row.get_by_text("Openen")).to_have_attribute("href", "https://rathenau.nl/document")
    expect(rathenau_row.get_by_text("Details")).to_have_attribute("href", "https://rathenau.nl/detail")

    # Expect Custom row
    custom_row = page.locator("table tbody tr").nth(2)
    expect(custom_row.locator('td')).to_contain_text([
        "1.1",
        "Document title 3",
        "01-03-2022",
        "custom-test",
        "Kort",
        "Openen"
    ])

    regex = re.compile(r'/private-document/source--custom/test/test.pdf')
    expect(custom_row.get_by_text("Openen")).to_have_attribute("href", regex)

    # ---------------------
    context.close()
    browser.close()

    assert True, 'Test passed'


def test_search():
    with sync_playwright() as playwright:
        run(playwright)
