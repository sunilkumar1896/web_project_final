═══════════════════════════════════════════════
        EduRank — B.Tech College Finder
═══════════════════════════════════════════════

FEATURES:
  ✅ College search with autocomplete
  ✅ Advanced filtering (state, type, fees, NAAC grade)
  ✅ Student reviews with ID card verification
  ✅ Automatic data updates from external APIs
  ✅ Admin panel for data management
  ✅ Real-time news and announcements

FILES INCLUDED:
  - index.html           → Frontend (open in browser)
  - admin.html           → Admin panel for data updates
  - app.py               → Flask backend API
  - seed_colleges.py     → Database seeder (100+ colleges + API-fetched)
  - update_college_data_new.py → Automatic data updater
  - test_updates.py      → Test script for updates
  - requirements.txt     → Python dependencies

HOW TO RUN:
─────────────────────────────────────────────
STEP 1: Open this folder in VS Code

STEP 2: Open terminal (Ctrl + `)

STEP 3: Create virtual environment
  python -m venv venv

STEP 4: Activate virtual environment
  Windows:    venv\Scripts\activate
  Mac/Linux:  source venv/bin/activate

STEP 5: Install dependencies
  pip install -r requirements.txt

STEP 6: Seed the database (includes API fetching for missing colleges)
  python seed_colleges.py

STEP 7: Start the backend
  python app.py

STEP 8: Open frontend in Chrome
  - Main app: Visit http://localhost:5000/ in Chrome
  - Admin panel: Visit http://localhost:5000/admin
  - From another device on the same Wi-Fi, open http://<your-pc-ip>:5000/

─────────────────────────────────────────────
SEARCH EXAMPLES:
  - Type "IIT"        → All IITs
  - Type "Bihar"      → All Bihar colleges
  - Type "Jharkhand"  → All Jharkhand colleges
  - Type "Kolkata"    → All Kolkata colleges
  - Type "GL Bajaj"   → GL Bajaj details
─────────────────────────────────────────────

AUTOMATIC DATA FETCHING:
─────────────────────────────────────────────
The seed script automatically fetches missing colleges from APIs:
  • IILM University details fetched from NewsAPI if not in database
  • Fallback to curated default data if API unavailable
  • Keeps college data current and comprehensive

To manually check for missing colleges:
  python seed_colleges.py (run multiple times to fetch different colleges)
─────────────────────────────────────────────

API ENDPOINTS:
  GET  /api/colleges              → List colleges with search/filters
  GET  /api/colleges/{id}         → Get college details
  GET  /api/suggest?q=query       → Search suggestions
  GET  /api/filters/meta          → Filter options
  GET  /api/health                → System health check
  POST /api/admin/update-data     → Trigger data updates
  GET  /api/colleges/{id}/updates → College updates
  GET  /api/updates/recent        → Recent updates across all colleges
  POST /api/reviews               → Submit review with ID card
  GET  /api/colleges/{id}/reviews → Get verified reviews
─────────────────────────────────────────────
