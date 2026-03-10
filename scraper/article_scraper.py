import requests
from bs4 import BeautifulSoup

def scrape_article_text(url, max_chars=2000):
    """
    Scrapes the main paragraph text from an article URL.
    Limits the extracted text to roughly max_chars to save LLM token usage.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Extract text from paragraph tags
        paragraphs = soup.find_all('p')
        
        text_content = ""
        for p in paragraphs:
            para_text = p.get_text(strip=True)
            if len(para_text) > 20: # skip very short paragraphs (usually nav or meta)
                text_content += para_text + "\n\n"
                
            if len(text_content) >= max_chars:
                break
                
        # Truncate to exactly max_chars, trying to cleanly cut near end of sentence if possible
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars]
            # Try to back up to the last period
            last_period = text_content.rfind('.')
            if last_period > max_chars * 0.8: # If there's a period in the last 20%
                text_content = text_content[:last_period + 1]
                
        return text_content.strip()
        
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
        return ""

if __name__ == "__main__":
    test_url = "https://techcrunch.com/2024/05/14/google-announces-gemini-1-5-pro/"
    print(f"Scraping {test_url} ...")
    text = scrape_article_text(test_url)
    print(f"Scraped {len(text)} characters.")
    print("-" * 40)
    print(text[:500] + "...")
