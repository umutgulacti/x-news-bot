import feedparser
import tweepy
import os
import json
from datetime import datetime, timezone

# --- Ayarlar ---
RSS_URL = "https://www.hurriyet.com.tr/rss/anasayfa"  # ← Kendi RSS linkini yaz
MAX_TWEET_LENGTH = 270
POSTED_FILE = "posted.json"

# --- X API Bağlantısı ---
client = tweepy.Client(
    consumer_key=os.environ["API_KEY"],
    consumer_secret=os.environ["API_SECRET"],
    access_token=os.environ["ACCESS_TOKEN"],
    access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
)

def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(posted[-100:], f)  # Son 100 haberi tut

def format_tweet(title, link):
    tweet = f"{title}\n\n{link}"
    if len(tweet) > MAX_TWEET_LENGTH:
        max_title = MAX_TWEET_LENGTH - len(link) - 10
        tweet = f"{title[:max_title]}...\n\n{link}"
    return tweet

def main():
    feed = feedparser.parse(RSS_URL)
    posted = load_posted()
    new_count = 0

    for entry in feed.entries[:5]:  # En son 5 haberi kontrol et
        link = entry.get("link", "")
        title = entry.get("title", "")

        if link in posted:
            continue

        tweet_text = format_tweet(title, link)
        
        try:
            client.create_tweet(text=tweet_text)
            posted.append(link)
            new_count += 1
            print(f"✅ Tweet atıldı: {title[:50]}...")
            break  # Her çalışmada 1 tweet at (spam önlemi)
        except Exception as e:
            print(f"❌ Hata: {e}")
            break

    save_posted(posted)
    print(f"Tamamlandı. {new_count} yeni tweet.")

if __name__ == "__main__":
    main()
