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

class CollegeDataUpdater:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EduRank-DataUpdater/1.0'
        })

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def update_nirf_rankings(self):
        """Update NIRF rankings from official source"""
        try:
            # NIRF API or web scraping (simplified example)
            # In reality, you'd need to check NIRF's actual API endpoints
            nirf_url = "https://www.nirfindia.org/api/rankings"  # Example endpoint

            response = self.session.get(nirf_url, timeout=30)
            if response.status_code == 200:
                nirf_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for college in nirf_data.get('colleges', []):
                    cursor.execute("""
                        UPDATE colleges
                        SET nirf_rank = ?, score = ?
                        WHERE name LIKE ? OR short_name LIKE ?
                    """, (
                        college.get('rank'),
                        college.get('score'),
                        f"%{college.get('name', '')}%",
                        f"%{college.get('name', '')}%"
                    ))

                conn.commit()
                conn.close()
                print(f"✅ Updated NIRF rankings for {len(nirf_data.get('colleges', []))} colleges")

        except Exception as e:
            print(f"❌ NIRF update failed: {e}")

    def update_naac_grades(self):
        """Update NAAC accreditation grades"""
        try:
            # NAAC API endpoint (example)
            naac_url = "https://naac.gov.in/api/accreditation-data"

            response = self.session.get(naac_url, timeout=30)
            if response.status_code == 200:
                naac_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for institution in naac_data.get('institutions', []):
                    cursor.execute("""
                        UPDATE colleges
                        SET naac_grade = ?
                        WHERE name LIKE ? OR short_name LIKE ?
                    """, (
                        institution.get('grade'),
                        f"%{institution.get('name', '')}%",
                        f"%{institution.get('name', '')}%"
                    ))

                conn.commit()
                conn.close()
                print(f"✅ Updated NAAC grades for {len(naac_data.get('institutions', []))} institutions")

        except Exception as e:
            print(f"❌ NAAC update failed: {e}")

    def update_aicte_approvals(self):
        """Update AICTE approval status"""
        try:
            # AICTE approval data
            aicte_url = "https://www.aicte-india.org/api/approved-institutions"

            response = self.session.get(aicte_url, timeout=30)
            if response.status_code == 200:
                aicte_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for institution in aicte_data.get('institutions', []):
                    cursor.execute("""
                        UPDATE colleges
                        SET aicte_approved = 1
                        WHERE name LIKE ? OR short_name LIKE ?
                    """, (
                        f"%{institution.get('name', '')}%",
                        f"%{institution.get('name', '')}%"
                    ))

                conn.commit()
                conn.close()
                print(f"✅ Updated AICTE approvals for {len(aicte_data.get('institutions', []))} institutions")

        except Exception as e:
            print(f"❌ AICTE update failed: {e}")

    def update_placement_data(self):
        """Update placement statistics from various sources"""
        try:
            # This could come from individual college APIs or placement portals
            # Example: LinkedIn, Glassdoor, or college career services APIs

            sources = [
                "https://api.linkedin.com/v2/college-placement-data",
                "https://api.glassdoor.com/college-salaries",
                "https://api.ambitionbox.com/college-reviews"
            ]

            for source_url in sources:
                try:
                    response = self.session.get(source_url, timeout=30)
                    if response.status_code == 200:
                        placement_data = response.json()

                        conn = self.get_db_connection()
                        cursor = conn.cursor()

                        for college_data in placement_data.get('colleges', []):
                            cursor.execute("""
                                UPDATE colleges
                                SET highest_package = ?, median_package = ?, placement_percent = ?
                                WHERE name LIKE ? OR short_name LIKE ?
                            """, (
                                college_data.get('highest_package'),
                                college_data.get('median_package'),
                                college_data.get('placement_percentage'),
                                f"%{college_data.get('name', '')}%",
                                f"%{college_data.get('name', '')}%"
                            ))

                        conn.commit()
                        conn.close()
                        print(f"✅ Updated placement data from {source_url}")

                except Exception as e:
                    print(f"⚠️ Failed to update from {source_url}: {e}")

        except Exception as e:
            print(f"❌ Placement data update failed: {e}")

    def update_university_news(self):
        """Fetch latest news and updates from universities"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Get all colleges with websites
            cursor.execute("SELECT id, name, website FROM colleges WHERE website IS NOT NULL")
            colleges = cursor.fetchall()
            conn.close()

            for college in colleges:
                try:
                    # Check university news RSS or API
                    news_url = f"{college['website']}/api/news"  # Example endpoint

                    response = self.session.get(news_url, timeout=15)
                    if response.status_code == 200:
                        news_data = response.json()

                        # Store news in a separate table (you might want to create this)
                        # For now, just log significant updates
                        for news_item in news_data.get('news', []):
                            if 'admission' in news_item.get('title', '').lower() or 'fee' in news_item.get('title', '').lower():
                                print(f"📰 {college['name']}: {news_item.get('title')}")

                except Exception as e:
                    # Skip individual college failures
                    continue

        except Exception as e:
            print(f"❌ University news update failed: {e}")

    def update_from_ugc_api(self):
        """Update data from UGC (University Grants Commission)"""
        try:
            ugc_url = "https://www.ugc.ac.in/api/university-data"

            response = self.session.get(ugc_url, timeout=30)
            if response.status_code == 200:
                ugc_data = response.json()

                conn = self.get_db_connection()
                cursor = conn.cursor()

                for university in ugc_data.get('universities', []):
                    cursor.execute("""
                        UPDATE colleges
                        SET type = 'University',
                            established = ?,
                            total_students = ?
                        WHERE name LIKE ? OR short_name LIKE ?
                    """, (
                        university.get('established_year'),
                        university.get('student_count'),
                        f"%{university.get('name', '')}%",
                        f"%{university.get('name', '')}%"
                    ))

                conn.commit()
                conn.close()
                print(f"✅ Updated UGC data for {len(ugc_data.get('universities', []))} universities")

        except Exception as e:
            print(f"❌ UGC update failed: {e}")

    def run_full_update(self):
        """Run all update processes"""
        print("🚀 Starting college data update process...")

        self.update_nirf_rankings()
        time.sleep(2)  # Rate limiting

        self.update_naac_grades()
        time.sleep(2)

        self.update_aicte_approvals()
        time.sleep(2)

        self.update_placement_data()
        time.sleep(2)

        self.update_university_news()
        time.sleep(2)

        self.update_from_ugc_api()

        print("✅ All updates completed!")

    def schedule_updates(self):
        """Set up scheduled updates (daily/weekly)"""
        # This would typically be run as a cron job or scheduled task
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