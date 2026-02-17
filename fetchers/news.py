import requests
import datetime
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

def fetch_news(keywords: List[str] = ["AI"], limit: int = 5) -> List[Dict]:
    """
    Fetches latest news from Hacker News matching the keywords.

    Args:
        keywords (List[str]): List of search terms to filter by (default: ["AI"]).
        limit (int): The number of news items to return (default: 5).

    Returns:
        List[Dict]: A list of dictionaries containing news details.
    """
    # Get top stories IDs
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(top_stories_url)
        story_ids = response.json()
    except Exception as e:
        logger.error(f"Error fetching top stories: {e}")
        return []

    news_items = []
    count = 0

    # We check more stories to find matches, but limit the API calls
    for story_id in story_ids[:100]:
        if count >= limit:
            break

        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        try:
            story_resp = requests.get(story_url)
            story = story_resp.json()

            if not story or 'title' not in story or 'url' not in story:
                continue

            title = story['title']
            title_lower = title.lower()

            # Check if any keyword is in the title
            match_found = False
            for keyword in keywords:
                k_lower = keyword.lower()
                # Use regex for short acronyms to avoid partial matches
                if len(k_lower) <= 3:
                     if re.search(r'\b' + re.escape(k_lower) + r'\b', title_lower):
                         match_found = True
                         break
                else:
                    if k_lower in title_lower:
                        match_found = True
                        break

            if match_found:
                # Fetch OG Image
                image_url = None
                try:
                    art_resp = requests.get(story['url'], timeout=5)
                    soup = BeautifulSoup(art_resp.content, 'html.parser')
                    og_image = soup.find('meta', property='og:image')
                    if og_image:
                        image_url = og_image['content']
                except Exception:
                    pass # Ignore errors fetching image

                # Calculate popularity score: HN Score / (Days + 1)
                story_time = story.get('time', datetime.datetime.now().timestamp())
                story_dt = datetime.datetime.fromtimestamp(story_time)
                now = datetime.datetime.now()
                days_ago = (now - story_dt).total_seconds() / 86400
                if days_ago < 0: days_ago = 0

                hn_score = story.get('score', 0)
                popularity_score = hn_score / (days_ago + 1)

                news_item = {
                    "title": title,
                    "link": story['url'],
                    "score": hn_score,
                    "comments": f"https://news.ycombinator.com/item?id={story_id}",
                    "thumbnail": image_url,
                    "popularity": popularity_score
                }
                news_items.append(news_item)
                count += 1

        except Exception as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            continue

    # Sort by popularity score descending
    news_items.sort(key=lambda x: x['popularity'], reverse=True)

    return news_items

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = fetch_news()
    for n in results:
        print(f"Title: {n['title']}")
        print(f"Link: {n['link']}")
        print(f"Score: {n['score']} | Pop: {n['popularity']:.2f}")
        print("---")
