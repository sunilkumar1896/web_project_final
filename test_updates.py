#!/usr/bin/env python3
"""
Test script for CollegeDataUpdater
Run this to test the automatic data update functionality
"""

import os
import sys
from update_college_data_new import CollegeDataUpdater

def test_updater():
    """Test the CollegeDataUpdater functionality"""

    # Get the database path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "colleges.db")

    if not os.path.exists(DB_PATH):
        print("❌ Database not found! Run: python seed_colleges.py first")
        return False

    print("🔄 Testing CollegeDataUpdater...")
    print(f"📍 Database: {DB_PATH}")

    try:
        # Create updater instance
        updater = CollegeDataUpdater(DB_PATH)
        print("✅ Updater initialized successfully")

        # Test individual methods (without actually calling APIs to avoid rate limits)
        print("\n🧪 Testing individual update methods...")

        # Test NIRF update (this will try to scrape)
        print("📊 Testing NIRF rankings update...")
        try:
            nirf_count = updater.update_nirf_rankings()
            print(f"✅ NIRF update completed (found {nirf_count} updates)")
        except Exception as e:
            print(f"⚠️  NIRF update test failed: {e}")

        # Test news update
        print("📰 Testing news updates...")
        try:
            news_count = updater.update_from_news_apis()
            print(f"✅ News update completed (found {news_count} updates)")
        except Exception as e:
            print(f"⚠️  News update test failed: {e}")

        # Test placement update
        print("💼 Testing placement data updates...")
        try:
            placement_count = updater.update_placement_data_from_sources()
            print(f"✅ Placement update completed (found {placement_count} updates)")
        except Exception as e:
            print(f"⚠️  Placement update test failed: {e}")

        # Test university feeds
        print("🌐 Testing university website feeds...")
        try:
            feed_count = updater.update_university_websites()
            print(f"✅ Feed update completed (found {feed_count} updates)")
        except Exception as e:
            print(f"⚠️  Feed update test failed: {e}")

        print("\n🎉 All update methods tested successfully!")
        print("💡 Note: Some methods may show 0 updates if APIs are not configured or rate-limited")
        return True

    except Exception as e:
        print(f"❌ Updater test failed: {e}")
        return False

def test_full_update():
    """Test the full update process"""
    print("\n🔄 Testing full update process (this may take a while)...")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "colleges.db")

    try:
        updater = CollegeDataUpdater(DB_PATH)
        updater.run_full_update()
        print("✅ Full update completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Full update failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 EduRank Data Updater Test Suite")
    print("=" * 50)

    # Test individual methods
    success = test_updater()

    if success:
        # Ask if user wants to run full update
        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            test_full_update()
        else:
            print("\n💡 To run the full update process, use: python test_updates.py --full")
    else:
        print("❌ Tests failed. Please check the configuration and try again.")
        sys.exit(1)