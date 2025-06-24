from typing import List
from pytrends.request import TrendReq
# Updated import for snscrape (modern API)
from snscrape.modules.twitter import TwitterSearchScraper
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def get_google_trend_score(keywords: List[str]) -> float:
    """
    Fetches daily interest for given keywords from Google Trends and returns
    the normalized average score (0.0 to 1.0).
    """
    try:
        pytrends = TrendReq()
        pytrends.build_payload(keywords, timeframe='now 1-d')
        data = pytrends.interest_over_time()
        if data.empty:
            return 0.0
        # Normalize (values range 0–100)
        return float(data[keywords].iloc[-1].mean() / 100)
    except Exception:
        return 0.0


def get_twitter_trend_score(keywords: List[str]) -> float:
    """
    Uses snscrape's TwitterSearchScraper to fetch recent tweets matching any keyword.
    Normalizes count by a ceiling (100 tweets) to return a 0.0–1.0 score.
    """
    try:
        query = " OR ".join(f"#{kw}" for kw in keywords)
        # Fetch up to 100 recent tweets
        tweets = list(TwitterSearchScraper(query).get_items())[:100]
        count = len(tweets)
        return min(count / 100, 1.0)
    except Exception:
        return 0.0


def get_youtube_trending_similarity(keywords: List[str]) -> float:
    """
    Scrapes YouTube's trending page and computes the maximum cosine similarity
    between your video's keywords and any trending video title.
    """
    try:
        resp = requests.get("https://www.youtube.com/feed/trending")
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [
            t.get('title')
            for t in soup.select('a#video-title')
            if t.get('title')
        ]

        # Load sentence-transformer model once per call
        model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = model.encode(" ".join(keywords))
        sims = [
            cosine_similarity([emb], [model.encode(title)])[0][0]
            for title in titles
        ]
        return max(sims) if sims else 0.0
    except Exception:
        return 0.0


def calculate_trending_score(
    keywords: List[str],
    w1: float = 0.4,
    w2: float = 0.3,
    w3: float = 0.3
) -> float:
    """
    Combines Google Trends, Twitter, and YouTube similarity scores
    into a single trending_score.
    """
    g = get_google_trend_score(keywords)
    t = get_twitter_trend_score(keywords)
    y = get_youtube_trending_similarity(keywords)
    return round(w1 * g + w2 * t + w3 * y, 4)
