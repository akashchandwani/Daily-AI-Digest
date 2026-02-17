import feedparser
import urllib.parse
import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def fetch_papers(topics: List[str] = ["cs.AI"], limit: int = 5, sort_mode: str = "date") -> List[Dict]:
    """
    Fetches latest papers from arXiv for a given list of topics.

    Args:
        topics (List[str]): List of arXiv categories to search for (default: ["cs.AI"]).
        limit (int): The number of papers to fetch (default: 5).
        sort_mode (str): Sorting mode. "date" (default) or "random".

    Returns:
        List[Dict]: A list of dictionaries containing paper details.
    """
    base_url = "http://export.arxiv.org/api/query?"
    # Join topics with OR
    search_query = " OR ".join([f"cat:{topic}" for topic in topics])

    # Manually construct URL to ensure colons are not encoded if that's the issue,
    # or use quote with safe=':+'.
    encoded_query = urllib.parse.quote(search_query, safe=':+')

    # If random, fetch more results to sample from
    max_results = limit * 5 if sort_mode == "random" else limit

    query_params = {
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    url = f"{base_url}search_query={encoded_query}&{urllib.parse.urlencode(query_params)}"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        logger.error(f"Error fetching arXiv feed: {e}")
        return []

    papers = []
    for entry in feed.entries:
        paper = {
            "title": entry.title.replace('\n', ' ').strip(),
            "summary": entry.summary.replace('\n', ' ').strip(),
            "link": entry.link,
            "published": entry.published
        }
        papers.append(paper)

    if sort_mode == "random" and len(papers) > limit:
        return random.sample(papers, limit)

    return papers[:limit]

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    results = fetch_papers()
    for p in results:
        print(f"Title: {p['title']}")
        print(f"Link: {p['link']}")
        print("---")
