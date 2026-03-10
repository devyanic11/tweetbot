import os
import random
from google import genai
from dotenv import load_dotenv

# Provide categories to randomly select from
CATEGORIES = [
    "Technical insight (AI systems / ML engineering)",
    "Product thinking observation",
    "Builder reflection",
    "Opinion about the tech ecosystem",
    "Student skill gap insight",
    "Short contrarian thought",
    "Mini framework or mental model"
]

def init_gemini():
    """Initializes and returns the Gemini API client safely."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")
    return genai.Client(api_key=api_key)

def generate_insight(article_text=None):
    """
    Generates an insight from the article text (or a random topic) using Gemini.
    """
    client = init_gemini()
    
    category = random.choice(CATEGORIES)
    
    if article_text:
        prompt = f"""
You are an AI/ML engineer, systems thinker, and a builder participating in "tech Twitter".
You want to write a single tweet expressing an original opinion, observation, or insight based on the article provided.

CRITICAL TONE REQUIREMENTS:
- Write exactly like a human texting a thought to another engineer.
- Be highly informal, blunt, and direct. Skip the flowery setup.
- OCCASIONALLY use lowercase formatting.
- NEVER use phrases like "The whole X narrative...", "A reminder that", "In the world of". 
- NEVER use corporate speak, hype tone, emojis, or hashtags.
- Sound slightly opinionated, cynical, or genuinely surprised by an engineering tradeoff.
- Do NOT sound polite, enthusiastic, or like a LinkedIn post.

STRICT CONSTRAINTS:
- The tweet MUST NOT be a summary of the article. It should be a single, sharp insight derived from the core signal.
- Max 220 characters.
- Do NOT add a URL here (it will be added later).
- Do NOT output anything other than the raw tweet itself.

The tweet should fit this category of thought: {category}

Article Text to process:
{article_text}

Raw Tweet generated:
"""
    else:
        prompt = f"""
You are an AI/ML engineer, systems thinker, and a builder participating in "tech Twitter".
You want to write a single tweet expressing an original opinion, observation, or insight out of the blue.

CRITICAL TONE REQUIREMENTS:
- Write exactly like a human texting a thought to another engineer.
- Be highly informal, blunt, and direct. Skip the flowery setup.
- OCCASIONALLY use lowercase formatting.
- NEVER use phrases like "The whole X narrative...", "A reminder that", "In the world of". 
- NEVER use corporate speak, hype tone, emojis, or hashtags.
- Sound slightly opinionated, cynical, or genuinely surprised by an engineering tradeoff.
- Do NOT sound polite, enthusiastic, or like a LinkedIn post.

STRICT CONSTRAINTS:
- Max 280 characters.
- Do NOT add a URL here.
- Do NOT output anything other than the raw tweet itself.

The tweet should fit this category of thought: {category}

Raw Tweet generated:
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating insight: {e}")
        return None

def generate_quote_tweet(original_tweet_text, original_author):
    """
    Generates a quote-tweet style response to a trending AI/ML tweet.
    Returns a short, opinionated reply the user can use when retweeting.
    """
    client = init_gemini()

    prompt = f"""
You are an AI/ML engineer on tech Twitter. Someone you follow just tweeted this:

@{original_author}: "{original_tweet_text}"

Write a short quote-tweet response. This is what you'd type above the retweet.

TONE:
- Casual, like texting a friend about a tweet you saw.
- Add your own take, agree/disagree, extend the thought, or drop a related observation.
- Be blunt, slightly opinionated, real.
- NEVER use emojis, hashtags, or corporate speak.
- Do NOT just agree politely. Add something new.

CONSTRAINTS:
- Max 200 characters.
- Output ONLY the raw response text. No quotes, no attribution.

Your quote-tweet response:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating quote tweet: {e}")
        return None
