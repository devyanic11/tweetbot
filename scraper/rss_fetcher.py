import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

RSS_FEEDS = [
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/"
]

HTML_FEEDS = [
    "https://techcrunch.com/latest/"
]

def fetch_rss_links():
    """Fetches the latest article links from the configured RSS and HTML feeds."""
    links = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Process RSS Feeds
    for feed_url in RSS_FEEDS:
        try:
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Find all item/link elements (RSS 2.0 format)
            for item in root.findall('.//item'):
                link = item.find('link')
                if link is not None and link.text:
                    if link.text.strip() not in links:
                        links.append(link.text.strip())
                    
        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")
            
    # Process HTML Feeds like TechCrunch Latest
    for html_url in HTML_FEEDS:
        try:
            response = requests.get(html_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                # TechCrunch articles typically have /202X/ in the URL
                if 'techcrunch.com/202' in href or href.startswith('/202'):
                    full_link = href if href.startswith('http') else "https://techcrunch.com" + href
                    if full_link not in links:
                        links.append(full_link)
        except Exception as e:
            print(f"Error fetching HTML feed {html_url}: {e}")
            
    return list(set(links))

if __name__ == "__main__":
    links = fetch_rss_links()
    print(f"Fetched {len(links)} links from RSS feeds.")
    for link in links[:5]:
        print("-", link)
