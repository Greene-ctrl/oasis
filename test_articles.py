import requests
from bs4 import BeautifulSoup
import json

def main():
    url = "https://www.dawn.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    articles = []
    # Broaden search to any link with 'news' in URL and decent length text
    for a in soup.find_all('a', href=True):
        title = a.get_text(strip=True)
        link = a['href']
        if '/news/' in link and title and len(title) > 20:
            if not link.startswith('http'):
                if link.startswith('//'):
                    link = 'https:' + link
                else:
                    link = "https://www.dawn.com" + link
            if link not in [x['url'] for x in articles]:
                articles.append({"title": title, "url": link})
        if len(articles) >= 5:
            break

    with open("results.md", "w") as f:
        f.write("# Dawn.com Articles\n\n")
        f.write("Scanned articles from dawn.com:\n\n")
        for i, article in enumerate(articles):
            f.write(f"{i+1}. **{article['title']}**\n   - [Link]({article['url']})\n\n")

    print(f"results.md generated with {len(articles)} articles.")

main()
