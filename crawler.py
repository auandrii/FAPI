from playwright.async_api import async_playwright
import re

proxy = {
    "server": "http://gate.smartproxy.com:7000",
    # Add credentials if your proxy requires authentication
}


async def crawl_and_extract_text(url):
    """
    Use Playwright to crawl the given URL and extract text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy=proxy)
        page = await browser.new_page()
        await page.goto(url)
        # Extract main page text
        text = await page.text_content('body')

        # Additional URLs to crawl
        additional_urls = [url + "/contact", url + "/about"]
        for additional_url in additional_urls:
            try:
                await page.goto(additional_url)
                text += "\n" + await page.text_content('body')
            except Exception as e:
                print(f"Error crawling {additional_url}: {str(e)}")

        await browser.close()

        # Process and clean the text
        clean_text = re.sub(r'\s+', ' ', text).strip()
        return clean_text
