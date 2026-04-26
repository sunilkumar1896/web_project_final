import sqlite3

conn = sqlite3.connect('colleges.db')
cursor = conn.cursor()

# Check if FTS table exists
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="colleges_fts"')
result = cursor.fetchone()
print('FTS table exists:', result is not None)

if result:
    # Check FTS records
    cursor.execute('SELECT COUNT(*) FROM colleges_fts')
    count = cursor.fetchone()[0]
    print('FTS records:', count)

    # Test FTS search
    try:
        cursor.execute("SELECT * FROM colleges_fts WHERE colleges_fts MATCH 'IIT' LIMIT 3")
        rows = cursor.fetchall()
        print('FTS search results for "IIT":', len(rows))
        for row in rows[:2]:
            print('  ', row)
    except Exception as e:
        print('FTS search error:', e)

conn.close()