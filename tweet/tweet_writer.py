import os
import json
from google import genai
from google.genai import types

from analysis.insight_generator import generate_insight, init_gemini

def evaluate_tweet(tweet_text):
    """
    Acts as a Twitter quality reviewer and scores the tweet.
    Returns the score and a dictionary of the review.
    """
    client = init_gemini()
    
    prompt = f"""
You are an expert Twitter content reviewer evaluating tech tweets for an AI/ML engineer persona.
Read this tweet:

{tweet_text}

Score it on a scale of 1 to 10 for the following 5 criteria:
1. Hook strength: Does the first line make someone stop scrolling?
2. Clarity: Is the idea easy to understand quickly?
3. Insight value: Does the tweet contain a real insight or observation (not a summary)?
4. Originality: Does it avoid generic or obvious statements?
5. Twitter-native tone: Does it sound like a real, slightly cynical human engineer texting a thought? (A 10 means ZERO AI cliches).

Return your evaluation EXACTLY as JSON in the following format:
{{
  "hook_strength": <int>,
  "clarity": <int>,
  "insight_value": <int>,
  "originality": <int>,
  "twitter_native_tone": <int>,
  "feedback": "<string explanation of weaknesses>",
  "average_score": <float>
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        result = json.loads(response.text)
        
        # Recalculate average to be safe
        scores = [
            result.get("hook_strength", 0),
            result.get("clarity", 0),
            result.get("insight_value", 0),
            result.get("originality", 0),
            result.get("twitter_native_tone", 0)
        ]
        avg = sum(scores) / len(scores) if scores else 0
        result['average_score'] = round(avg, 2)
        
        return result
    except Exception as e:
        print(f"Error evaluating tweet: {e}")
        return {"average_score": 0.0, "feedback": str(e)}

def rewrite_tweet(tweet_text, feedback, article_text=None):
    """Rewrites the tweet based on reviewer feedback."""
    client = init_gemini()
    
    article_context = f"Original Source Article Text for context:\n{article_text}\n" if article_text else ""
    
    prompt = f"""
You are refining a tweet for tech Twitter (author persona: AI/ML engineer).

Original Tweet:
{tweet_text}

Critic Feedback:
{feedback}

{article_context}
Task: Write a new version of the tweet addressing the feedback.

CRITICAL TONE REQUIREMENTS:
- Write exactly like a human texting a thought to another engineer.
- Be raw, blunt, and direct. Skip the flowery setup.
- OCCASIONALLY use all lowercase. Use short sentence fragments.
- NEVER use phrases like "The whole X narrative...", "A reminder that...", "In the world of...", etc.
- NEVER use corporate speak, emojis, or hashtags.
- Do NOT sound polite or enthusiastic.

Constraints:
- Max 280 characters.
- Start with a solid hook line.
- Do NOT summarize the article. Keep it to an insight/take.
- Output ONLY the raw rewritten tweet.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error rewriting tweet: {e}")
        return tweet_text

def craft_final_tweet(article_url=None, article_text=None, max_attempts=3):
    """
    End-to-end process: Generate -> Evaluate -> (Rewrite if needed) -> Format
    """
    tweet = generate_insight(article_text)
    if not tweet:
        return None, None, None
        
    attempts = 0
    best_tweet = tweet
    best_score = 0
    
    while attempts < max_attempts:
        eval_result = evaluate_tweet(best_tweet)
        score = eval_result.get("average_score", 0.0)
        
        if score >= 7.5:
            # Good enough!
            best_score = score
            break
            
        # Needs rewrite
        feedback = eval_result.get("feedback", "")
        # print(f"DEBUG - Attempt {{attempts+1}} Failed ({{score}}/10). Feedback: {{feedback}}")
        best_tweet = rewrite_tweet(best_tweet, feedback, article_text)
        best_score = score # Track score for final even if we fail out
        attempts += 1
        
    if best_score < 7.5:
        # We failed 3 times
        return None, None, best_score
        
    return best_tweet, article_url, best_score
