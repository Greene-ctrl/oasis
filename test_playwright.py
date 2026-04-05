from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars'
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        # add init script to mock properties
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        page = context.new_page()

        print("Navigating to dawn.com...")
        response = page.goto("https://www.dawn.com", wait_until="domcontentloaded")
        print("Status code:", response.status if response else "None")
        page.wait_for_timeout(5000)

        title = page.title()
        print("Page title:", title)

        articles = []
        links = page.locator("a").element_handles()
        print("Found total links:", len(links))

        for link in links:
            try:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()
                if len(text) > 15 and href and ('/news/' in href or '/article/' in href):
                    if not href.startswith('http'):
                        if href.startswith('//'):
                            href = 'https:' + href
                        else:
                            href = "https://www.dawn.com" + href
                    if href not in [x['url'] for x in articles]:
                        articles.append({"title": text, "url": href})
                if len(articles) >= 5:
                    break
            except:
                pass

        with open("results.md", "w") as f:
            f.write("# Dawn.com Articles\n\n")
            f.write("Scanned articles from dawn.com:\n\n")
            for i, article in enumerate(articles):
                clean_title = " ".join(article['title'].splitlines())
                f.write(f"{i+1}. **{clean_title}**\n   - [Link]({article['url']})\n\n")

        print(f"results.md generated with {len(articles)} articles.")
        browser.close()

if __name__ == "__main__":
    main()
