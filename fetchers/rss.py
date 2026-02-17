import feedparser
import requests
import datetime
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import timezone
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def fetch_rss(feeds: List[str] = [], limit: int = 5) -> List[Dict]:
    """
    Fetches latest items from a list of RSS feeds.

    Args:
        feeds (List[str]): List of RSS feed URLs.
        limit (int): The number of items to return (default: 5).

    Returns:
        List[Dict]: A list of dictionaries containing feed items.
    """
    all_items = []

    for feed_url in feeds:
        try:
            import certifi
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml;q=0.9, */*;q=0.8'
            }
            try:
                resp = requests.get(feed_url, headers=headers, timeout=10, verify=certifi.where())
            except requests.exceptions.SSLError:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                resp = requests.get(feed_url, headers=headers, timeout=10, verify=False)
            feed = feedparser.parse(resp.content)

            for entry in feed.entries:
                title = entry.title
                link = entry.link

                # Fetch OG Image
                image_url = None
                try:
                    # Some feeds might put image in content/summary, but fetching URL is safer for og:image
                    art_resp = requests.get(link, timeout=5)
                    soup = BeautifulSoup(art_resp.content, 'html.parser')
                    og_image = soup.find('meta', property='og:image')
                    if og_image:
                        image_url = og_image['content']
                except Exception:
                    pass

                # Parse date
                published_dt = datetime.datetime.now(timezone.utc)
                if hasattr(entry, 'published'):
                    try:
                        published_dt = parser.parse(entry.published)
                        if published_dt.tzinfo is None:
                            published_dt = published_dt.replace(tzinfo=timezone.utc)
                    except:
                        pass
                elif hasattr(entry, 'updated'):
                     try:
                        published_dt = parser.parse(entry.updated)
                        if published_dt.tzinfo is None:
                            published_dt = published_dt.replace(tzinfo=timezone.utc)
                     except:
                        pass

                item = {
                    "source": feed.feed.get('title', 'Unknown Blog'),
                    "title": title,
                    "link": link,
                    "published": published_dt.strftime("%Y-%m-%d"),
                    "published_dt": published_dt, # For sorting
                    "thumbnail": image_url
                }
                all_items.append(item)

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            continue

    # Sort by date descending
    all_items.sort(key=lambda x: x['published_dt'], reverse=True)

    return all_items[:limit]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    feeds = ["https://openai.com/index/rss.xml"]
    results = fetch_rss(feeds)
    for i in results:
        print(f"[{i['source']}] {i['title']}")
        print(f"Link: {i['link']}")
        print(f"Image: {i['thumbnail']}")
        print("---")
