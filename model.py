from typing import List
from pytrends.request import TrendReq
import snscrape.modules.twitter as sntwitter
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def get_google_trend_score(keywords: List[str]) -> float:
    try:
        pytrends = TrendReq()
        pytrends.build_payload(keywords, timeframe='now 1-d')
        data = pytrends.interest_over_time()
        if data.empty:
            return 0.0
        return float(data[keywords].iloc[-1].mean() / 100)
    except:
        return 0.0


def get_twitter_trend_score(keywords: List[str]) -> float:
    try:
        query = " OR ".join(f"#{kw}" for kw in keywords)
        tweets = list(sntwitter.TwitterSearchScraper(query).get_items())
        return min(len(tweets) / 1000, 1.0)
    except:
        return 0.0


def get_youtube_trending_similarity(keywords: List[str]) -> float:
    try:
        resp = requests.get("https://www.youtube.com/feed/trending")
        soup = BeautifulSoup(resp.text, "html.parser")
        titles = [t.get('title') for t in soup.select('a#video-title') if t.get('title')]
        model = SentenceTransformer('all-MiniLM-L6-v2')
        emb = model.encode(" ".join(keywords))
        sims = [cosine_similarity([emb], [model.encode(t)])[0][0] for t in titles]
        return max(sims) if sims else 0.0
    except:
        return 0.0


def calculate_trending_score(keywords: List[str], w1=0.4, w2=0.3, w3=0.3) -> float:
    g = get_google_trend_score(keywords)
    t = get_twitter_trend_score(keywords)
    y = get_youtube_trending_similarity(keywords)
    return round(w1 * g + w2 * t + w3 * y, 4)