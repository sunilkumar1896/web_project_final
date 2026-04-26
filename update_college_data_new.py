"""
College Data Update System
Fetches updates from various APIs and sources
"""

import requests
import sqlite3
import json
import os
from datetime import datetime, timedelta
import time
import feedparser  # For RSS feeds
from bs4 import BeautifulSoup  # For web scraping

class CollegeDataUpdater:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EduRank-DataUpdater/1.0 (https://edurank.example.com)'
        })

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def add_college_update(self, college_id, update_type, title, description, source_url=None):
        """Add a new update to the college_updates table"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO college_updates (college_id, update_type, title, description, source_url, published_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (college_id, update_type, title, description, source_url, datetime.now()))

        conn.commit()
        conn.close()

    def update_nirf_rankings(self):
        """Update NIRF rankings - using web scraping since no official API"""
        updates_count = 0
        try:
            # NIRF rankings are published annually
            nirf_url = "https://www.nirfindia.org/2024/EngineeringRanking.html"

            response = self.session.get(nirf_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Parse the rankings table (simplified example)
                rankings_table = soup.find('table', {'id': 'tbl_overall'})

                if rankings_table:
                    rows = rankings_table.find_all('tr')[1:]  # Skip header

                    conn = self.get_db_connection()
                    cursor = conn.cursor()

                    for row in rows[:100]:  # Top 100
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            rank = cols[0].text.strip()
                            name = cols[1].text.strip()
                            score = cols[3].text.strip()

                            # Update college ranking
                            cursor.execute("""
                                UPDATE colleges
                                SET nirf_rank = ?, score = ?, last_updated = ?, data_source = 'NIRF'
                                WHERE name LIKE ? OR short_name LIKE ?
                            """, (int(rank), score, datetime.now(), f"%{name}%", f"%{name}%"))

                            if cursor.rowcount > 0:
                                updates_count += 1

                                # Add update record
                                cursor.execute("SELECT id FROM colleges WHERE name LIKE ? OR short_name LIKE ?",
                                             (f"%{name}%", f"%{name}%"))
                                college_row = cursor.fetchone()
                                if college_row:
                                    self.add_college_update(
                                        college_row[0], 'ranking',
                                        f'NIRF Rank Updated to #{rank}',
                                        f'College ranked #{rank} in NIRF Engineering Rankings 2024 with score {score}',
                                        nirf_url
                                    )

                    conn.commit()
                    conn.close()
                    print(f"✅ Updated NIRF rankings for {updates_count} colleges")

        except Exception as e:
            print(f"❌ NIRF update failed: {e}")

        return updates_count

    def update_from_news_apis(self):
        """Update college information from news APIs"""
        updates_count = 0
        try:
            # Use NewsAPI or similar to get education news
            news_api_key = '4f16d90fbbe24e56976a9091718005e8'
            news_url = f"https://newsapi.org/v2/everything?q=indian+colleges+OR+iit+OR+nit&apiKey={news_api_key}"

            response = self.session.get(news_url, timeout=30)
            if response.status_code == 200:
                news_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for article in news_data.get('articles', []):
                    title = article.get('title', '')
                    description = article.get('description', '')
                    url = article.get('url', '')

                    # Check if it's about a specific college
                    for college_name in ['IIT', 'NIT', 'College', 'University']:
                        if college_name.lower() in title.lower():
                            # Find matching colleges
                            cursor.execute("""
                                SELECT id, name FROM colleges
                                WHERE ? LIKE '%' || name || '%' OR ? LIKE '%' || short_name || '%'
                            """, (title, title))

                            colleges = cursor.fetchall()
                            for college in colleges:
                                self.add_college_update(
                                    college[0], 'news', title, description, url
                                )
                                updates_count += 1
                            break

                conn.close()
                print(f"✅ Updated from news APIs ({updates_count} updates)")

        except Exception as e:
            print(f"❌ News API update failed: {e}")

        return updates_count

    def update_university_websites(self):
        """Scrape updates from university websites"""
        updates_count = 0
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Get colleges with websites
            cursor.execute("SELECT id, name, website FROM colleges WHERE website IS NOT NULL LIMIT 10")
            colleges = cursor.fetchall()
            conn.close()

            for college in colleges:
                try:
                    college_id, name, website = college

                    # Check for news RSS feed
                    rss_urls = [
                        f"{website}/feed/",
                        f"{website}/rss/",
                        f"{website}/news/feed/"
                    ]

                    for rss_url in rss_urls:
                        try:
                            feed = feedparser.parse(rss_url)
                            if feed.entries:
                                for entry in feed.entries[:3]:  # Last 3 news items
                                    published = entry.get('published_parsed')
                                    if published:
                                        pub_date = datetime(*published[:6])
                                        if datetime.now() - pub_date < timedelta(days=30):  # Recent news
                                            self.add_college_update(
                                                college_id, 'news',
                                                entry.title, entry.description,
                                                entry.link
                                            )
                                            updates_count += 1
                                break  # Found RSS feed, stop trying others
                        except:
                            continue

                    time.sleep(1)  # Be respectful to servers

                except Exception as e:
                    print(f"⚠️ Failed to update {name}: {e}")
                    continue

            print(f"✅ Updated from university websites ({updates_count} updates)")

        except Exception as e:
            print(f"❌ University website update failed: {e}")

        return updates_count

    def update_placement_data_from_sources(self):
        """Update placement data from various sources"""
        updates_count = 0
        try:
            # AmbitionBox API (example)
            ambitionbox_url = "https://www.ambitionbox.com/api/colleges"

            response = self.session.get(ambitionbox_url, timeout=30)
            if response.status_code == 200:
                placement_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for college_data in placement_data.get('colleges', []):
                    name = college_data.get('name', '')

                    cursor.execute("""
                        UPDATE colleges
                        SET highest_package = ?, median_package = ?, placement_percent = ?,
                            last_updated = ?, data_source = 'AmbitionBox'
                        WHERE name LIKE ? OR short_name LIKE ?
                    """, (
                        college_data.get('highest_package'),
                        college_data.get('average_package'),
                        college_data.get('placement_percentage'),
                        datetime.now(),
                        f"%{name}%", f"%{name}%"
                    ))

                    if cursor.rowcount > 0:
                        updates_count += 1

                        # Add update if placement data changed significantly
                        cursor.execute("SELECT id FROM colleges WHERE name LIKE ? OR short_name LIKE ?",
                                     (f"%{name}%", f"%{name}%"))
                        college_row = cursor.fetchone()
                        if college_row:
                            self.add_college_update(
                                college_row[0], 'placement',
                                'Placement Data Updated',
                                f'Highest Package: {college_data.get("highest_package")}, Average: {college_data.get("average_package")}',
                                'https://www.ambitionbox.com'
                            )

                conn.commit()
                conn.close()
                print(f"✅ Updated placement data ({updates_count} updates)")

        except Exception as e:
            print(f"❌ Placement data update failed: {e}")

        return updates_count

    def run_full_update(self):
        """Run all update processes"""
        print("🚀 Starting college data update process...")

        print("📊 Updating NIRF rankings...")
        self.update_nirf_rankings()
        time.sleep(2)

        print("📰 Updating from news APIs...")
        self.update_from_news_apis()
        time.sleep(2)

        print("🏛️ Updating from university websites...")
        self.update_university_websites()
        time.sleep(2)

        print("💼 Updating placement data...")
        self.update_placement_data_from_sources()

        print("✅ All updates completed!")

    def schedule_updates(self):
        """Set up scheduled updates"""
        last_update_file = os.path.join(os.path.dirname(self.db_path), 'last_update.txt')

        try:
            with open(last_update_file, 'r') as f:
                last_update = datetime.fromisoformat(f.read().strip())
        except:
            last_update = datetime.now() - timedelta(days=1)

        if datetime.now() - last_update > timedelta(hours=24):  # Update daily
            self.run_full_update()

            with open(last_update_file, 'w') as f:
                f.write(datetime.now().isoformat())


if __name__ == "__main__":
    updater = CollegeDataUpdater("colleges.db")
    updater.run_full_update()