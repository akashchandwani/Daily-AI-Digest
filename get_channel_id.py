import requests
from bs4 import BeautifulSoup

def get_channel_id(handle):
    url = f"https://www.youtube.com/{handle}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Method 1: meta tag
        meta_id = soup.find('meta', itemprop='channelId')
        if meta_id:
            return meta_id['content']

        # Method 2: link tag
        link_id = soup.find('link', rel='canonical')
        if link_id:
            href = link_id['href']
            if '/channel/' in href:
                return href.split('/channel/')[-1]

        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

handles = ["@ByteByteGo", "@gkcs", "@hnasr"]
for handle in handles:
    cid = get_channel_id(handle)
    print(f"{handle}: {cid}")
