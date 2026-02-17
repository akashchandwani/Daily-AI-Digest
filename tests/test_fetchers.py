import unittest
from unittest.mock import patch, MagicMock
from fetchers import arxiv, youtube, news, rss

# Helper to mock feedparser entries which support both dict and attribute access
class MockEntry(dict):
    def __getattr__(self, name):
        return self.get(name)

class TestFetchers(unittest.TestCase):

    @patch('fetchers.arxiv.feedparser.parse')
    def test_arxiv_fetch_papers(self, mock_parse):
        # Mock response
        mock_entry = MockEntry({
            'title': "Test Paper",
            'summary': "Test Summary",
            'link': "http://arxiv.org/abs/1234.5678",
            'published': "2023-10-27T00:00:00Z"
        })

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        papers = arxiv.fetch_papers(topics=["cs.AI"], limit=1)

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]['title'], "Test Paper")
        self.assertEqual(papers[0]['link'], "http://arxiv.org/abs/1234.5678")

    @patch('fetchers.youtube.feedparser.parse')
    def test_youtube_fetch_videos(self, mock_parse):
        # Mock response
        mock_entry = MockEntry({
            'title': "Test Video",
            'link': "http://youtube.com/watch?v=123",
            'published': "2023-10-27T00:00:00Z",
            'media_statistics': {'views': '1000'},
            'media_thumbnail': [{'url': 'http://thumb.jpg'}]
        })

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        channels = {"Test Channel": "UC123"}
        videos = youtube.fetch_videos(channels=channels, limit=1)

        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['title'], "Test Video")
        self.assertEqual(videos[0]['views'], 1000)

    @patch('fetchers.news.requests.get')
    def test_news_fetch_news(self, mock_get):
        # Mock top stories response
        mock_response_ids = MagicMock()
        mock_response_ids.json.return_value = [12345]

        # Mock story details response
        mock_response_story = MagicMock()
        mock_response_story.json.return_value = {
            "title": "AI is great",
            "url": "http://example.com",
            "score": 100,
            "time": 1698364800
        }

        # Mock article page response for og:image
        mock_response_art = MagicMock()
        mock_response_art.content = b'<html><meta property="og:image" content="http://img.jpg"></html>'

        # Side effect to return different mocks based on call
        def side_effect(*args, **kwargs):
            if "topstories" in args[0]:
                return mock_response_ids
            elif "item" in args[0]:
                return mock_response_story
            else:
                return mock_response_art

        mock_get.side_effect = side_effect

        news_items = news.fetch_news(keywords=["AI"], limit=1)

        self.assertEqual(len(news_items), 1)
        self.assertEqual(news_items[0]['title'], "AI is great")
        self.assertEqual(news_items[0]['score'], 100)

    @patch('fetchers.rss.feedparser.parse')
    def test_rss_fetch_rss(self, mock_parse):
        # Mock response
        mock_entry = MockEntry({
            'title': "Test Blog Post",
            'link': "http://blog.com/post",
            'published': "Mon, 27 Oct 2023 10:00:00 GMT"
        })

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feed.feed = {'title': 'Test Blog'} # Source title
        mock_parse.return_value = mock_feed

        feeds = ["http://blog.com/feed"]
        items = rss.fetch_rss(feeds=feeds, limit=1)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], "Test Blog Post")
        self.assertEqual(items[0]['source'], "Test Blog")

if __name__ == '__main__':
    unittest.main()
