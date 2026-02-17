import feedparser
import datetime
from dateutil import parser
from datetime import timezone
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def fetch_videos(channels: Optional[Dict[str, str]] = None, limit: int = 3) -> List[Dict]:
    """
    Fetches latest videos from selected AI YouTube channels.

    Args:
        channels (Optional[Dict[str, str]]): Dictionary of channel names and IDs.
        limit (int): The number of videos to fetch per channel (default: 3).

    Returns:
        List[Dict]: A list of dictionaries containing video details.
    """
    if channels is None:
        # Default fallback
        channels = {
            "Two Minute Papers": "UCbfYPyITQ-7l4upoX8nvctg",
            "AI Explained": "UCNJ1Ymd5yFuUPtn21xxR7kw"
        }

    all_videos = []

    for channel_name, channel_id in channels.items():
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                # Extract views
                views = 0
                if 'media_statistics' in entry and 'views' in entry.media_statistics:
                    views = int(entry.media_statistics['views'])

                # Parse date
                try:
                    published_dt = parser.parse(entry.published)
                    # Ensure timezone awareness for subtraction
                    if published_dt.tzinfo is None:
                            published_dt = published_dt.replace(tzinfo=timezone.utc)

                    now = datetime.datetime.now(timezone.utc)
                    days_ago = (now - published_dt).total_seconds() / 86400
                    if days_ago < 0: days_ago = 0
                except Exception as e:
                    logger.debug(f"Error parsing date for video {entry.get('title', 'Unknown')}: {e}")
                    days_ago = 1 # Fallback

                # Calculate popularity score: Views / (Days + 1)
                # Add 1 to avoid huge scores for very fresh videos or div by zero
                popularity_score = views / (days_ago + 1)

                video = {
                    "source": channel_name,
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                    "thumbnail": entry.media_thumbnail[0]['url'] if 'media_thumbnail' in entry else None,
                    "views": views,
                    "score": popularity_score
                }
                all_videos.append(video)
        except Exception as e:
            logger.error(f"Error fetching/parsing channel {channel_name}: {e}")
            continue

    # Sort all collected videos by score descending
    all_videos.sort(key=lambda x: x['score'], reverse=True)

    return all_videos

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = fetch_videos()
    for v in results:
        print(f"[{v['source']}] {v['title']}")
        print(f"Views: {v['views']} | Score: {v['score']:.2f}")
        print("---")
