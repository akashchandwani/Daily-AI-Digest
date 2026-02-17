import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from datetime import datetime

def send_email(ai_papers, sys_papers, ai_videos, sys_videos, news, rss, recipient_email):
    """
    Sends the daily digest email.

    Args:
        ai_papers (list): List of AI paper dictionaries.
        sys_papers (list): List of System Design paper dictionaries.
        ai_videos (list): List of AI video dictionaries.
        sys_videos (list): List of System Design video dictionaries.
        news (list): List of news dictionaries.
        rss (list): List of RSS dictionaries.
        recipient_email (str): The email address to send to.
    """
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("Email credentials not found. Skipping email sending.")
        return

    # HTML Template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; text-align: center; }
            h2 { color: #3498db; margin-top: 30px; border-left: 5px solid #3498db; padding-left: 10px; }

            .item { margin-bottom: 25px; padding: 15px; background: #fff; border: 1px solid #e1e1e1; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .item h3 { margin-top: 0; margin-bottom: 10px; }
            .item a { color: #e74c3c; text-decoration: none; font-weight: bold; }
            .meta { font-size: 0.85em; color: #7f8c8d; margin-top: 5px; }

            /* Papers */
            details { margin-top: 10px; cursor: pointer; }
            summary { font-weight: bold; color: #555; outline: none; }
            .abstract { margin-top: 10px; font-size: 0.95em; color: #444; background: #f9f9f9; padding: 10px; border-radius: 4px; }

            /* Videos & News with thumbnails */
            .media-content { display: flex; gap: 15px; align-items: start; }
            .thumbnail { width: 160px; height: 90px; object-fit: cover; border-radius: 4px; flex-shrink: 0; background: #eee; }
            .text-content { flex-grow: 1; }

            @media (max-width: 600px) {
                .media-content { flex-direction: column; }
                .thumbnail { width: 100%; height: auto; margin-bottom: 10px; }
            }

            .footer { margin-top: 40px; font-size: 0.8em; text-align: center; color: #999; border-top: 1px solid #eee; padding-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Daily AI Digest - {{ date }}</h1>

        <h2>Latest Research Papers (arXiv)</h2>
        {% for paper in ai_papers %}
        <div class="item">
            <h3><a href="{{ paper.link }}">{{ paper.title }}</a></h3>
            <div class="meta">Published: {{ paper.published }}</div>
            <details>
                <summary>Read Abstract</summary>
                <div class="abstract">{{ paper.summary }}</div>
            </details>
        </div>
        {% endfor %}

        <h2>System Design Papers (Random Selection)</h2>
        {% for paper in sys_papers %}
        <div class="item">
            <h3><a href="{{ paper.link }}">{{ paper.title }}</a></h3>
            <div class="meta">Published: {{ paper.published }}</div>
            <details>
                <summary>Read Abstract</summary>
                <div class="abstract">{{ paper.summary }}</div>
            </details>
        </div>
        {% endfor %}

        <h2>Trending AI Videos</h2>
        {% for video in ai_videos %}
        <div class="item">
            <div class="media-content">
                {% if video.thumbnail %}
                <a href="{{ video.link }}">
                    <img src="{{ video.thumbnail }}" class="thumbnail" alt="Video Thumbnail">
                </a>
                {% endif %}
                <div class="text-content">
                    <h3><a href="{{ video.link }}">{{ video.title }}</a></h3>
                    <div class="meta">
                        Source: {{ video.source }}
                        {% if video.views %} • {{ "{:,}".format(video.views) }} views {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <h2>System Design Videos</h2>
        {% for video in sys_videos %}
        <div class="item">
            <div class="media-content">
                {% if video.thumbnail %}
                <a href="{{ video.link }}">
                    <img src="{{ video.thumbnail }}" class="thumbnail" alt="Video Thumbnail">
                </a>
                {% endif %}
                <div class="text-content">
                    <h3><a href="{{ video.link }}">{{ video.title }}</a></h3>
                    <div class="meta">
                        Source: {{ video.source }}
                        {% if video.views %} • {{ "{:,}".format(video.views) }} views {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <h2>Hacker News Top AI Stories</h2>
        {% for item in news %}
        <div class="item">
            <div class="media-content">
                {% if item.thumbnail %}
                <a href="{{ item.link }}">
                    <img src="{{ item.thumbnail }}" class="thumbnail" alt="Article Thumbnail" onerror="this.style.display='none'">
                </a>
                {% endif %}
                <div class="text-content">
                    <h3><a href="{{ item.link }}">{{ item.title }}</a></h3>
                    <div class="meta">
                        <a href="{{ item.comments }}" style="color: #7f8c8d; font-weight: normal; text-decoration: underline;">View Comments</a>
                        | Score: {{ item.score }}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <h2>Latest Blog Posts</h2>
        {% for item in rss %}
        <div class="item">
            <div class="media-content">
                {% if item.thumbnail %}
                <a href="{{ item.link }}">
                    <img src="{{ item.thumbnail }}" class="thumbnail" alt="Thumbnail" onerror="this.style.display='none'">
                </a>
                {% endif %}
                <div class="text-content">
                    <h3><a href="{{ item.link }}">{{ item.title }}</a></h3>
                    <div class="meta">
                        Source: {{ item.source }} | {{ item.published }}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <div class="footer">
            Generated by Open Source AI Digest Bot
            <p>Generated by automated agent • <a href="#">Unsubscribe</a></p>
        </div>
    </body>
    </html>
    """

    template = Template(template_str)
    html_content = template.render(
        date=datetime.now().strftime("%Y-%m-%d"),
        ai_papers=ai_papers,
        sys_papers=sys_papers,
        ai_videos=ai_videos,
        sys_videos=sys_videos,
        news=news,
        rss=rss
    )

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient_email
    msg['Subject'] = f"Daily AI Digest - {datetime.now().strftime('%Y-%m-%d')}"

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    print("Emailer module loaded.")
