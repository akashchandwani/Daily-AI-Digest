import os
import argparse
import yaml
import logging
import concurrent.futures
from dotenv import load_dotenv
from fetchers import arxiv, youtube, news, rss
import emailer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Daily AI Digest Generator")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending email")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    args = parser.parse_args()

    load_dotenv()

    # Load Configuration
    config = load_config(args.config)
    if not config:
        logger.warning("Using default configuration.")
        config = {
            "sources": {
                "arxiv": {"topics": ["cs.AI"], "limit": 5},
                "youtube": {"limit": 3}, # Fetcher has its own defaults if None passed
                "news": {"keywords": ["AI"], "limit": 5}
            }
        }

    # Config Check for Email
    if not os.getenv("EMAIL_USER") or not os.getenv("EMAIL_PASS") or not os.getenv("RECIPIENT_EMAIL"):
        if not args.dry_run:
            logger.error("Environment variables for email not set. Exiting.")
            return

    logger.info("Starting Daily AI Digest generation...")

    # Fetching Content in Parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Prepare futures
        futures = {}

        # arXiv: AI Papers
        arxiv_conf = config.get("sources", {}).get("arxiv", {})
        ai_topics = arxiv_conf.get("ai_topics", ["cs.AI", "cs.LG", "cs.CL", "cs.CV"])
        ai_limit = arxiv_conf.get("ai_limit", 5)
        futures[executor.submit(arxiv.fetch_papers, topics=ai_topics, limit=ai_limit)] = "ai_papers"

        # arXiv: System Design Papers
        sys_topics = arxiv_conf.get("system_design_topics", ["cs.DC", "cs.SE", "cs.NI", "cs.DB"])
        sys_limit = arxiv_conf.get("system_design_limit", 3)
        futures[executor.submit(arxiv.fetch_papers, topics=sys_topics, limit=sys_limit, sort_mode="random")] = "sys_papers"

        # YouTube: AI Videos
        yt_conf = config.get("sources", {}).get("youtube", {})
        ai_channels = yt_conf.get("ai_channels", None)
        ai_limit_yt = yt_conf.get("ai_limit", 3)
        futures[executor.submit(youtube.fetch_videos, channels=ai_channels, limit=ai_limit_yt)] = "ai_videos"

        # YouTube: System Design Videos
        sys_channels = yt_conf.get("system_design_channels", None)
        sys_limit_yt = yt_conf.get("system_design_limit", 3)
        futures[executor.submit(youtube.fetch_videos, channels=sys_channels, limit=sys_limit_yt)] = "sys_videos"

        # News
        news_conf = config.get("sources", {}).get("news", {})
        keywords = news_conf.get("keywords", ["AI", "LLM"])
        news_limit = news_conf.get("limit", 5)
        futures[executor.submit(news.fetch_news, keywords=keywords, limit=news_limit)] = "news"

        # RSS
        rss_conf = config.get("sources", {}).get("rss", {})
        feeds = rss_conf.get("feeds", [])
        rss_limit = rss_conf.get("limit", 5)
        futures[executor.submit(rss.fetch_rss, feeds=feeds, limit=rss_limit, one_per_source=True)] = "rss"

        # Engineering Blogs
        eng_conf = config.get("sources", {}).get("engineering_blogs", {})
        eng_feeds = eng_conf.get("feeds", [])
        eng_limit = eng_conf.get("limit", 5)
        futures[executor.submit(rss.fetch_rss, feeds=eng_feeds, limit=eng_limit, one_per_source=True)] = "eng_blogs"

        # Collect results
        results = {
            "ai_papers": [], "sys_papers": [],
            "ai_videos": [], "sys_videos": [],
            "news": [], "rss": [], "eng_blogs": []
        }

        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                data = future.result()
                results[name] = data
                logger.info(f"Fetched {len(data)} items for {name}")
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")

    # Extract results
    ai_papers = results["ai_papers"]
    sys_papers = results["sys_papers"]
    ai_videos = results["ai_videos"]
    sys_videos = results["sys_videos"]
    news_items = results["news"]
    rss_items = results["rss"]
    eng_blogs = results["eng_blogs"]

    if args.dry_run:
        print("\n=== DRY RUN MODE: Email Content Preview ===")

        print(f"AI Papers: {len(ai_papers)}")
        for p in ai_papers:
            print(f"- {p['title']}\n  Link: {p['link']}\n  Abstract length: {len(p['summary'])} chars\n")

        print(f"System Design Papers: {len(sys_papers)}")
        for p in sys_papers:
            print(f"- {p['title']}\n  Link: {p['link']}\n  Abstract length: {len(p['summary'])} chars\n")

        print(f"AI Videos: {len(ai_videos)}")
        for v in ai_videos:
            print(f"- {v['title']}\n  Link: {v['link']}\n  Thumbnail: {v['thumbnail']}\n")

        print(f"System Design Videos: {len(sys_videos)}")
        for v in sys_videos:
            print(f"- {v['title']}\n  Link: {v['link']}\n  Thumbnail: {v['thumbnail']}\n")

        print(f"News: {len(news_items)}")
        for n in news_items:
            print(f"- {n['title']}\n  Link: {n['link']}\n  Thumbnail: {n.get('thumbnail', 'None')}\n")

        print(f"RSS Items: {len(rss_items)}")
        for r in rss_items:
            print(f"- [{r['source']}] {r['title']}\n  Link: {r['link']}\n  Thumbnail: {r.get('thumbnail', 'None')}\n")

        print(f"Engineering Blogs: {len(eng_blogs)}")
        for r in eng_blogs:
            print(f"- [{r['source']}] {r['title']}\n  Link: {r['link']}\n  Thumbnail: {r.get('thumbnail', 'None')}\n")

        print("===========================================")
    else:
        recipient = os.getenv("RECIPIENT_EMAIL")
        if recipient:
            logger.info(f"Sending email to {recipient}...")
            # We pass the raw data, emailer handles formatting
            emailer.send_email(ai_papers, sys_papers, ai_videos, sys_videos, news_items, rss_items, eng_blogs, recipient)
        else:
            logger.warning("RECIPIENT_EMAIL not set. Skipping email.")

if __name__ == "__main__":
    main()
