from typing import List
from pytrends.request import TrendReq
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
        return float(data[keywords].iloc[-1].mean() / 100)
    except Exception:
        return 0.0


def get_twitter_trend_score(keywords: List[str]) -> float:
    """
    Scrapes Twitter's trending topics page and returns a normalized
    count of how many trending hashtags match the provided keywords.
    """
    try:
        url = "https://twitter.com/explore/tabs/trending"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        hashtags = [tag.get_text().lstrip("#") for tag in soup.find_all("span")]
        matches = sum(
            1 for kw in keywords
            if any(kw.lower() in h.lower() for h in hashtags)
        )
        max_count = len(hashtags) or 1
        return matches / max_count
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
        titles = [t.get('title') for t in soup.select('a#video-title') if t.get('title')]
        model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = model.encode(" ".join(keywords))
        sims = [
            cosine_similarity([emb], [model.encode(t)])[0][0]
            for t in titles
        ]
        return max(sims) if sims else 0.0
    except Exception:
        return 0.0


def calculate_trending_score(keywords: List[str], w1: float = 0.4, w2: float = 0.3, w3: float = 0.3) -> float:
    """
    Combines Google Trends, Twitter, and YouTube similarity scores
    into a single trending_score.
    """
    g = get_google_trend_score(keywords)
    t = get_twitter_trend_score(keywords)
    y = get_youtube_trending_similarity(keywords)
    return round(w1 * g + w2 * t + w3 * y, 4)
