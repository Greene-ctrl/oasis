import asyncio
from bs4 import BeautifulSoup
from oasis.social_agent.browser_manager import browser_manager

async def run_test():
    agent_id = 999
    print("Starting browser session...")
    await browser_manager.get_session(agent_id).start()

    print("Fetching dawn.com RSS...")
    # Cloudflare blocks headless browsers easily, so let's just grab the RSS feed which is easier for automated tools
    await browser_manager.get_session(agent_id).navigate("https://www.dawn.com/feeds/home/")

    await asyncio.sleep(2)

    print("Extracting DOM...")
    response = await browser_manager.get_session(agent_id).extract_dom()
    dom = response["dom"]

    # Simple regex or bs4 for XML since it's RSS
    soup = BeautifulSoup(dom, 'xml')
    links = []

    print("Finding articles in RSS...")
    article_data = []
    for item in soup.find_all('item'):
        link_tag = item.find('link')
        title_tag = item.find('title')
        desc_tag = item.find('description')

        if link_tag and title_tag and desc_tag:
            href = link_tag.text.strip()
            title = title_tag.text.strip()

            # Clean up description
            desc = desc_tag.text.strip()
            desc_soup = BeautifulSoup(desc, 'html.parser')
            clean_desc = desc_soup.get_text().strip()

            if href not in links:
                links.append(href)
                article_data.append({
                    "url": href,
                    "title": title,
                    "preview": clean_desc
                })

            if len(links) >= 5:
                break

    print(f"Found {len(links)} articles.")

    results = "# Dawn.com Articles Scan\n\n"

    for i, article in enumerate(article_data, 1):
        print(f"Scanning article {i}: {article['url']}...")
        # Since cloudflare blocks the headless browser navigating directly to the article links,
        # we extract the details right from the RSS feed item, which contains full previews.
        results += f"## {i}. {article['title']}\n"
        results += f"**URL:** {article['url']}\n\n"
        results += f"**Preview:**\n{article['preview']}\n\n---\n\n"

    print("Closing session...")
    await browser_manager.get_session(agent_id).close()

    with open("results.md", "w") as f:
        f.write(results)

    print("Results saved to results.md")

if __name__ == "__main__":
    asyncio.run(run_test())
