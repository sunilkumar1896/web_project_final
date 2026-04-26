"""
Add reviews table to the existing colleges.db
Run this to add review functionality.
Usage: python add_reviews_table.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "colleges.db")

def add_reviews_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            college_id        INTEGER NOT NULL,
            student_name      TEXT NOT NULL,
            student_email     TEXT,
            review_text       TEXT NOT NULL,
            rating            INTEGER CHECK(rating >= 1 AND rating <= 5),
            id_card_image     TEXT,  -- Path to uploaded image
            verified          INTEGER DEFAULT 0,  -- 0: pending, 1: verified, 2: rejected
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (college_id) REFERENCES colleges (id)
        );
    """)

    # Create index for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_college_id ON reviews(college_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_verified ON reviews(verified);")

    conn.commit()
    conn.close()
    print("✅ Reviews table added successfully!")

if __name__ == "__main__":
    add_reviews_table()