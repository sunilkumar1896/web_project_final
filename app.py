from flask import Flask, jsonify, request, send_from_directory, session, redirect, Response
from flask_cors import CORS
import sqlite3
import os
import re
import uuid
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_PERMANENT'] = False
CORS(app)

# ✅ Absolute DB path (correct)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "colleges.db")

# Upload folder for ID cards
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def ensure_reviews_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            college_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_email TEXT,
            review_text TEXT NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            id_card_image TEXT,
            verified INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (college_id) REFERENCES colleges (id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_college_id ON reviews(college_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_verified ON reviews(verified)")
    conn.commit()
    conn.close()


app_initialized = False

@app.before_request
def ensure_db_initialized():
    global app_initialized
    if not app_initialized:
        init_db()
        ensure_reviews_table()
        app_initialized = True


def login_required(admin_only=False):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Authentication required"}), 401
                return redirect("/login")
            if admin_only and not session.get("is_admin"):
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Admin access required"}), 403
                return redirect("/login")
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required."}), 400

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
        (username.lower(), email)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username or email already exists."}), 409

    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully. Please log in."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    identifier = (data.get("email") or data.get("username") or "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"error": "Email/username and password are required."}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?",
        (identifier.lower(), identifier.lower())
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email/username or password."}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["is_admin"] = bool(user["is_admin"])

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_admin": bool(user["is_admin"])
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})


@app.route("/api/me", methods=["GET"])
def get_current_user():
    if not session.get("user_id"):
        return jsonify({"user": None}), 200
    return jsonify({
        "user": {
            "id": session.get("user_id"),
            "username": session.get("username"),
            "is_admin": session.get("is_admin")
        }
    })


@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect("/")
    return send_from_directory(BASE_DIR, "login.html")


@app.route("/register")
def register_page():
    if session.get("user_id"):
        return redirect("/")
    return send_from_directory(BASE_DIR, "register.html")


@app.route("/logout")
def logout_page():
    session.clear()
    return redirect("/login")


@app.route("/")
def home_page():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/index.html")
def index_page():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/robots.txt")
def robots_txt():
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return Response(content, mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    base_url = request.url_root.rstrip("/")
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{base_url}/</loc>',
        '  </url>',
        '</urlset>'
    ]
    return Response("\n".join(xml), mimetype="application/xml")


@app.route("/api/colleges", methods=["GET"])
def get_colleges():
    q = request.args.get("q", "").strip()
    types = [t.strip() for t in request.args.get("type", "").split(",") if t.strip()]
    states = [s.strip() for s in request.args.get("state", "").split(",") if s.strip()]
    naac = [n.strip() for n in request.args.get("naac", "").split(",") if n.strip()]
    fee_max = request.args.get("fee_max", type=float)
    sort = request.args.get("sort", "edurank")
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", 10, type=int)))

    conn = get_db()
    params = []

    # ✅ FIX: Use FTS search with fallback
    if q:
        # Try FTS search first
        base = """
            SELECT c.* FROM colleges c
            JOIN colleges_fts fts ON c.id = fts.rowid
            WHERE colleges_fts MATCH ?
        """
        params.append(q + "*")
    else:
        base = "SELECT * FROM colleges WHERE 1=1"

    if types:
        base += f" AND type IN ({','.join('?'*len(types))})"
        params.extend(types)

    if states:
        base += f" AND state IN ({','.join('?'*len(states))})"
        params.extend(states)

    if naac:
        base += f" AND naac_grade IN ({','.join('?'*len(naac))})"
        params.extend(naac)

    if fee_max is not None:
        base += " AND total_fees_num <= ?"
        params.append(fee_max)

    sort_map = {
        "edurank": "edurank ASC",
        "nirf": "nirf_rank ASC",
        "fees": "total_fees_num ASC",
        "placement": "median_package DESC",
    }

    base += f" ORDER BY {sort_map.get(sort, 'edurank ASC')}"

    try:
        total = conn.execute(f"SELECT COUNT(*) FROM ({base})", params).fetchone()[0]
        rows = conn.execute(
            base + " LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page]
        ).fetchall()
    except Exception as e:
        # If FTS fails, fallback to LIKE search
        if q and "fts" in str(e).lower():
            base = "SELECT * FROM colleges WHERE name LIKE ? OR location LIKE ?"
            params = [f"%{q}%", f"%{q}%"]
            total = conn.execute(f"SELECT COUNT(*) FROM ({base})", params).fetchone()[0]
            rows = conn.execute(
                base + " LIMIT ? OFFSET ?",
                params + [per_page, (page - 1) * per_page]
            ).fetchall()
        else:
            conn.close()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "colleges": [dict(r) for r in rows],
    })


@app.route("/api/colleges/<int:college_id>", methods=["GET"])
def get_college(college_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM colleges WHERE id = ?", (college_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "College not found"}), 404

    return jsonify(dict(row))


@app.route("/api/filters/meta", methods=["GET"])
def filter_meta():
    conn = get_db()

    states = [dict(r) for r in conn.execute(
        "SELECT state, COUNT(*) as count FROM colleges GROUP BY state"
    ).fetchall()]

    types = [dict(r) for r in conn.execute(
        "SELECT type, COUNT(*) as count FROM colleges GROUP BY type"
    ).fetchall()]

    conn.close()

    return jsonify({"states": states, "types": types})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend is working."""
    try:
        conn = get_db()
        result = conn.execute("SELECT COUNT(*) FROM colleges").fetchone()
        count = result[0] if result else 0
        conn.close()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "colleges_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route("/api/suggest", methods=["GET"])
def suggest():
    q = request.args.get("q", "").strip()

    if len(q) < 2:
        return jsonify([])

    conn = get_db()

    # Search in multiple fields for better suggestions
    rows = conn.execute("""
        SELECT id, name, short_name, location, state
        FROM colleges
        WHERE name LIKE ? OR short_name LIKE ? OR location LIKE ? OR state LIKE ?
        ORDER BY
            CASE
                WHEN name LIKE ? THEN 1
                WHEN short_name LIKE ? THEN 2
                ELSE 3
            END,
            name
        LIMIT 8
    """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"{q}%", f"{q}%")).fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])


# ── COLLEGE UPDATES ENDPOINTS ─────────────────────────────────────────────

@app.route("/api/colleges/<int:college_id>/updates", methods=["GET"])
def get_college_updates(college_id):
    """Get recent updates for a specific college"""
    limit = request.args.get("limit", 10, type=int)

    conn = get_db()
    rows = conn.execute("""
        SELECT update_type, title, description, source_url, published_date
        FROM college_updates
        WHERE college_id = ?
        ORDER BY published_date DESC
        LIMIT ?
    """, (college_id, limit)).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


@app.route("/api/updates/recent", methods=["GET"])
def get_recent_updates():
    """Get recent updates across all colleges"""
    limit = request.args.get("limit", 20, type=int)

    conn = get_db()
    rows = conn.execute("""
        SELECT cu.*, c.name as college_name, c.short_name
        FROM college_updates cu
        JOIN colleges c ON cu.college_id = c.id
        ORDER BY cu.published_date DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


@app.route("/api/admin/update-data", methods=["POST"])
@login_required(admin_only=True)
def trigger_data_update():
    """Admin endpoint to trigger data updates from APIs"""
    try:
        # Import the updater here to avoid circular imports
        from update_college_data_new import CollegeDataUpdater

        updater = CollegeDataUpdater(DB_PATH)
        # Run in background (in production, use proper async/task queue)
        import threading
        thread = threading.Thread(target=updater.run_full_update)
        thread.daemon = True
        thread.start()

        return jsonify({"message": "Data update started in background"}), 202

    except Exception as e:
        return jsonify({"error": f"Failed to start update: {e}"}), 500


# ── REVIEWS ENDPOINTS ─────────────────────────────────────────────────────

@app.route("/api/colleges/<int:college_id>/reviews", methods=["GET"])
def get_reviews(college_id):
    """Get all verified reviews for a college"""
    conn = get_db()
    rows = conn.execute("""
        SELECT id, student_name, review_text, rating, verified, created_at
        FROM reviews
        WHERE college_id = ? AND verified = 1
        ORDER BY created_at DESC
    """, (college_id,)).fetchall()
    conn.close()

    reviews = []
    for r in rows:
        review = dict(r)
        # Calculate average rating
        reviews.append(review)

    return jsonify(reviews)


@app.route("/api/reviews", methods=["POST"])
def submit_review():
    """Submit a new review with ID card upload"""
    try:
        college_id = request.form.get("college_id", type=int)
        student_name = request.form.get("student_name", "").strip()
        student_email = request.form.get("student_email", "").strip()
        review_text = request.form.get("review_text", "").strip()
        rating = request.form.get("rating", type=int)

        if not all([college_id, student_name, review_text, rating]):
            return jsonify({"error": "Missing required fields"}), 400

        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1-5"}), 400

        # Handle ID card upload
        id_card_path = None
        if 'id_card' in request.files and request.files['id_card'].filename:
            file = request.files['id_card']
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            id_card_path = f"/uploads/{filename}"  # Relative path for serving

        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (college_id, student_name, student_email, review_text, rating, id_card_image, verified)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (college_id, student_name, student_email, review_text, rating, id_card_path))

        review_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Review submitted successfully! It will be visible after verification.",
            "review_id": review_id
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to submit review: {str(e)}"}), 500


@app.route("/api/reviews/<int:review_id>", methods=["GET"])
def get_review(review_id):
    """Get a specific review (for admin verification)"""
    conn = get_db()
    row = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Review not found"}), 404

    return jsonify(dict(row))


@app.route("/api/reviews/<int:review_id>/verify", methods=["POST"])
@login_required(admin_only=True)
def verify_review(review_id):
    """Verify or reject a review (admin endpoint)"""
    action = request.json.get("action")  # "verify" or "reject"

    if action not in ["verify", "reject"]:
        return jsonify({"error": "Invalid action"}), 400

    verified = 1 if action == "verify" else 2

    conn = get_db()
    conn.execute("UPDATE reviews SET verified = ? WHERE id = ?", (verified, review_id))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Review {action}ed successfully"})


@app.route("/admin")
@login_required(admin_only=True)
def admin_page():
    """Serve the admin interface"""
    return send_from_directory(BASE_DIR, "admin.html")


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    """Serve uploaded ID card images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    print("Using DB at:", DB_PATH)

    if not os.path.exists(DB_PATH):
        print("[ERROR] Database not found! Run: python seed_colleges.py")
    else:
        init_db()
        print("[OK] Database found. Starting server...")

    app.run(host="0.0.0.0", debug=True, port=5000)