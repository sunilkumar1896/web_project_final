"""
Run this once to populate your colleges.db with sample data.
Usage: python seed_colleges.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "colleges.db")

# ── 1. CREATE TABLES ─────────────────────────────────────────────────────────
def create_tables(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS colleges_fts;
        DROP TABLE IF EXISTS colleges;

        CREATE TABLE colleges (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            name              TEXT NOT NULL,
            short_name        TEXT,
            location          TEXT,
            state             TEXT,
            type              TEXT,
            naac_grade        TEXT,
            nirf_rank         INTEGER,
            edurank           INTEGER,
            qs_asia_rank      INTEGER,
            iirf_rank         INTEGER,
            score             TEXT,
            total_fees        TEXT,
            total_fees_num    REAL,
            highest_package   TEXT,
            median_package    TEXT,
            entrance_exam     TEXT,
            logo_gradient     TEXT,
            aicte_approved    INTEGER DEFAULT 1,
            established       INTEGER,
            total_students    INTEGER,
            placement_percent INTEGER,
            website           TEXT,
            about             TEXT
        );

        CREATE VIRTUAL TABLE colleges_fts
            USING fts5(
                name, short_name, location, state, entrance_exam, about,
                content='colleges', content_rowid='id'
            );

        CREATE TRIGGER colleges_ai AFTER INSERT ON colleges BEGIN
            INSERT INTO colleges_fts(rowid, name, short_name, location, state, entrance_exam, about)
            VALUES (new.id, new.name, new.short_name, new.location, new.state, new.entrance_exam, new.about);
        END;

        CREATE TRIGGER colleges_ad AFTER DELETE ON colleges BEGIN
            INSERT INTO colleges_fts(colleges_fts, rowid, name, short_name, location, state, entrance_exam, about)
            VALUES ('delete', old.id, old.name, old.short_name, old.location, old.state, old.entrance_exam, old.about);
        END;
    """)
    print("✅ Tables created.")


# ── 2. COLLEGE DATA ───────────────────────────────────────────────────────────
COLLEGES = [
    # (name, short_name, location, state, type, naac, nirf, edurank, qs_asia, iirf, score,
    #  total_fees, fees_num, highest_pkg, median_pkg, exam, gradient, aicte, est, students, placement%, website, about)

    ("Indian Institute of Technology Bombay",
     "IIT Bombay", "Powai, Mumbai", "Maharashtra", "Government", "A++",
     3, 1, 40, 2, "1950/2000",
     "₹8.50L", 8.50, "₹1.80 CR", "₹21.8 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a3a6b,#2d5fa8)", 1,
     1958, 10000, 95, "https://www.iitb.ac.in",
     "IIT Bombay is one of India's premier engineering institutes, known for cutting-edge research and world-class placements. Located in Mumbai, it offers B.Tech, M.Tech and PhD programmes."),

    ("Indian Institute of Technology Delhi",
     "IIT Delhi", "Hauz Khas, New Delhi", "Delhi", "Government", "A++",
     2, 2, 50, 1, "1940/2000",
     "₹8.30L", 8.30, "₹2.00 CR", "₹20.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a1a6b,#2d2da8)", 1,
     1961, 8500, 94, "https://home.iitd.ac.in",
     "IIT Delhi is ranked among the top engineering colleges in India, situated in the heart of New Delhi. It is known for its excellent research output and industry connections."),

    ("Indian Institute of Technology Madras",
     "IIT Madras", "Adyar, Chennai", "Tamil Nadu", "Government", "A++",
     1, 3, 45, 3, "1935/2000",
     "₹7.90L", 7.90, "₹1.50 CR", "₹19.8 LPA",
     "JEE Advanced", "linear-gradient(135deg,#6b1a1a,#a82d2d)", 1,
     1959, 9200, 93, "https://www.iitm.ac.in",
     "IIT Madras is the top-ranked engineering institute in India (NIRF 2024). Known for research, innovation and strong alumni network across the globe."),

    ("Indian Institute of Technology Kanpur",
     "IIT Kanpur", "Kalyanpur, Kanpur", "Uttar Pradesh", "Government", "A++",
     4, 4, 60, 4, "1920/2000",
     "₹8.10L", 8.10, "₹1.42 CR", "₹18.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a4a2a,#2d8a4a)", 1,
     1959, 8000, 92, "https://www.iitk.ac.in",
     "IIT Kanpur is one of the oldest IITs and is famous for its computer science and aerospace engineering programs. It has produced many successful entrepreneurs and scientists."),

    ("Indian Institute of Technology Kharagpur",
     "IIT KGP", "Kharagpur", "West Bengal", "Government", "A++",
     5, 5, 65, 5, "1910/2000",
     "₹7.50L", 7.50, "₹1.20 CR", "₹17.2 LPA",
     "JEE Advanced", "linear-gradient(135deg,#4a1a6b,#7a2da8)", 1,
     1951, 12000, 91, "https://www.iitkgp.ac.in",
     "The first IIT established in India, IIT Kharagpur is the largest IIT by campus area. It offers more than 100 departments and schools with strong industry partnerships."),

    ("Indian Institute of Technology Roorkee",
     "IIT Roorkee", "Roorkee", "Uttarakhand", "Government", "A++",
     6, 6, 70, 8, "1900/2000",
     "₹7.80L", 7.80, "₹1.10 CR", "₹16.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#6b4a1a,#a87a2d)", 1,
     1847, 7800, 90, "https://www.iitr.ac.in",
     "IIT Roorkee is the oldest technical institution in Asia, established in 1847. It is well known for its civil, electrical and computer science engineering programs."),

    ("Indian Institute of Technology Hyderabad",
     "IIT Hyderabad", "Sangareddy, Hyderabad", "Telangana", "Government", "A+",
     8, 7, 90, 9, "1870/2000",
     "₹7.20L", 7.20, "₹98 LPA", "₹15.0 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a5a4a,#2d9a7a)", 1,
     2008, 4500, 88, "https://www.iith.ac.in",
     "IIT Hyderabad is a new-generation IIT known for its research in AI, machine learning and data science. It has strong industry ties with companies in Hyderabad's tech corridor."),

    ("Indian Institute of Technology Guwahati",
     "IIT Guwahati", "Amingaon, Guwahati", "Assam", "Government", "A+",
     7, 8, 85, 10, "1860/2000",
     "₹7.40L", 7.40, "₹88 LPA", "₹14.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a3a5a,#2d6a9a)", 1,
     1994, 5500, 87, "https://www.iitg.ac.in",
     "IIT Guwahati is situated on the banks of the Brahmaputra river and serves as the premier technical institute for Northeast India. Known for its peaceful campus and strong research culture."),

    ("National Institute of Technology Trichy",
     "NIT Trichy", "Tiruchirappalli", "Tamil Nadu", "Government", "A++",
     9, 9, 100, 12, "1820/2000",
     "₹5.30L", 5.30, "₹72 LPA", "₹12.5 LPA",
     "JEE Main", "linear-gradient(135deg,#5a1a3a,#9a2d6a)", 1,
     1964, 6800, 89, "https://www.nitt.edu",
     "NIT Trichy is consistently ranked as the best NIT in India. Known for its vibrant campus life, strong placement record and excellent faculty across all engineering disciplines."),

    ("National Institute of Technology Warangal",
     "NIT Warangal", "Warangal", "Telangana", "Government", "A+",
     23, 10, 120, 15, "1790/2000",
     "₹4.90L", 4.90, "₹65 LPA", "₹11.8 LPA",
     "JEE Main", "linear-gradient(135deg,#3a1a5a,#6a2d9a)", 1,
     1959, 6200, 88, "https://www.nitw.ac.in",
     "NIT Warangal is one of the oldest NITs and is highly regarded for its Computer Science and Electronics programs. It has a strong alumni network in top tech companies globally."),

    ("Vellore Institute of Technology",
     "VIT Vellore", "Vellore", "Tamil Nadu", "Private", "A++",
     11, 11, 175, 14, "1760/2000",
     "₹7.83L", 7.83, "₹52 LPA", "₹7.8 LPA",
     "VITEEE", "linear-gradient(135deg,#5a1a7a,#9a2dc4)", 1,
     1984, 35000, 82, "https://vit.ac.in",
     "VIT Vellore is one of India's largest private engineering universities. It is known for its international collaborations, industry-ready curriculum and massive placement drives attracting 1000+ companies."),

    ("BITS Pilani",
     "BITS Pilani", "Pilani", "Rajasthan", "Deemed", "A",
     20, 14, 220, 16, "1720/2000",
     "₹18.92L", 18.92, "₹1.20 CR", "₹19.2 LPA",
     "BITSAT", "linear-gradient(135deg,#7a4a1a,#c47a2d)", 1,
     1964, 6000, 90, "https://www.bits-pilani.ac.in",
     "BITS Pilani is one of India's most prestigious private universities. Its Practice School program gives students real industry exposure. It has a legendary alumni base in Silicon Valley and top Indian companies."),

    ("Delhi Technological University",
     "DTU", "Rohini, New Delhi", "Delhi", "Government", "A+",
     36, 15, 140, 18, "1700/2000",
     "₹3.20L", 3.20, "₹62 LPA", "₹10.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a6b,#2d7aab)", 1,
     1941, 9500, 85, "https://dtu.ac.in",
     "DTU (formerly Delhi College of Engineering) is one of Delhi's top engineering colleges. Its location in the capital gives students great access to internships, startups and top MNCs."),

    ("Netaji Subhas University of Technology",
     "NSUT", "Dwarka, New Delhi", "Delhi", "Government", "A",
     55, 16, 160, 22, "1650/2000",
     "₹2.80L", 2.80, "₹48 LPA", "₹9.2 LPA",
     "JEE Main", "linear-gradient(135deg,#2a1a6b,#4a2da8)", 1,
     1983, 7000, 83, "https://www.nsut.ac.in",
     "NSUT is a premier government engineering university in Delhi, offering excellent programs in Computer Science, IT and Electronics. Strong placement record with top tech companies."),

    ("Manipal Institute of Technology",
     "MIT Manipal", "Manipal", "Karnataka", "Deemed", "A+",
     52, 17, 190, 25, "1680/2000",
     "₹14.20L", 14.20, "₹44 LPA", "₹8.5 LPA",
     "MET / JEE Main", "linear-gradient(135deg,#1a6b3a,#2dab6a)", 1,
     1957, 14000, 80, "https://manipal.edu/mit.html",
     "MIT Manipal is a top-ranked private engineering college known for its international exposure, well-equipped labs and a lively coastal campus. It attracts students from across India and abroad."),

    ("Jadavpur University",
     "JU", "Jadavpur, Kolkata", "West Bengal", "Government", "A++",
     12, 18, 130, 20, "1710/2000",
     "₹0.36L", 0.36, "₹42 LPA", "₹8.0 LPA",
     "WBJEE", "linear-gradient(135deg,#1a6b5a,#2dab8a)", 1,
     1955, 8500, 84, "https://jadavpuruniversity.in",
     "Jadavpur University is one of the best government universities in India at an incredibly low fee. It is known for its strong academics, research output and alumni in top global companies."),

    ("PSG College of Technology",
     "PSG Tech", "Coimbatore", "Tamil Nadu", "Private", "A+",
     40, 19, 200, 28, "1640/2000",
     "₹3.60L", 3.60, "₹38 LPA", "₹7.2 LPA",
     "TNEA / JEE Main", "linear-gradient(135deg,#5a3a1a,#9a6a2d)", 1,
     1951, 7500, 81, "https://www.psgtech.edu",
     "PSG Tech is one of Tamil Nadu's finest engineering colleges, run by the PSG & Sons' Charities Trust. Known for strong industry connections, excellent labs and high placement rates."),

    ("Amity University",
     "Amity", "Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A+",
     None, 20, None, 35, "1580/2000",
     "₹12.50L", 12.50, "₹32 LPA", "₹6.5 LPA",
     "Amity JEE / JEE Main", "linear-gradient(135deg,#6b1a4a,#ab2d7a)", 1,
     1995, 45000, 75, "https://www.amity.edu",
     "Amity University is one of India's largest private universities with campuses across India and abroad. Known for its modern infrastructure, global tie-ups and diverse student community."),

    ("SRM Institute of Science and Technology",
     "SRM IST", "Kattankulathur, Chennai", "Tamil Nadu", "Deemed", "A++",
     45, 21, 210, 30, "1620/2000",
     "₹11.20L", 11.20, "₹42 LPA", "₹7.0 LPA",
     "SRMJEEE / JEE Main", "linear-gradient(135deg,#1a2a6b,#2d4aab)", 1,
     1985, 38000, 78, "https://www.srmist.edu.in",
     "SRM Institute is one of India's top-ranked private universities. It has strong research programs, international collaborations and a massive placement cell that engages 1200+ recruiters."),

    ("Thapar Institute of Engineering & Technology",
     "Thapar", "Patiala", "Punjab", "Deemed", "A",
     28, 22, 180, 24, "1660/2000",
     "₹13.70L", 13.70, "₹55 LPA", "₹11.0 LPA",
     "JEE Main", "linear-gradient(135deg,#3a5a1a,#6a9a2d)", 1,
     1956, 10000, 86, "https://www.thapar.edu",
     "Thapar Institute is a top-ranked deemed university in Punjab known for its excellent Computer Science, Mechanical and Electronics programs. It has strong industry ties with companies in Punjab and beyond."),

    ("PES University",
     "PES University", "Bengaluru", "Karnataka", "Private", "A+",
     None, 23, None, 40, "1600/2000",
     "₹8.40L", 8.40, "₹60 LPA", "₹9.5 LPA",
     "PESSAT / JEE Main", "linear-gradient(135deg,#1a5a6b,#2d9aab)", 1,
     1972, 8000, 85, "https://pes.edu",
     "PES University in Bangalore is a premier private engineering institution known for its excellent CSE program, startup culture and proximity to Bangalore's booming tech ecosystem."),

    ("Birla Institute of Technology Mesra",
     "BIT Mesra", "Mesra, Ranchi", "Jharkhand", "Deemed", "A",
     57, 24, 215, 42, "1590/2000",
     "₹9.10L", 9.10, "₹35 LPA", "₹7.8 LPA",
     "JEE Main", "linear-gradient(135deg,#5a1a1a,#9a2d2d)", 1,
     1955, 7500, 79, "https://www.bitmesra.ac.in",
     "BIT Mesra is one of the oldest private engineering institutes in India. Located in the lush greenery of Jharkhand, it offers strong programs in engineering, pharmacy and management."),

    ("Indian Institute of Information Technology Allahabad",
     "IIIT Allahabad", "Allahabad, Prayagraj", "Uttar Pradesh", "Government", "A+",
     33, 25, 145, 30, "1690/2000",
     "₹5.10L", 5.10, "₹72 LPA", "₹13.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a5a,#2d7a8a)", 1,
     1999, 3500, 88, "https://www.iiita.ac.in",
     "IIIT Allahabad is one of the premier IIITs in India, known for its exceptional Computer Science and IT programs. It produces graduates who are highly sought after by top tech companies globally."),

    ("Kalinga Institute of Industrial Technology",
     "KIIT", "Bhubaneswar", "Odisha", "Deemed", "A++",
     16, 26, 195, 32, "1640/2000",
     "₹12.80L", 12.80, "₹48 LPA", "₹8.2 LPA",
     "KIITEE / JEE Main", "linear-gradient(135deg,#1a6b1a,#2dab2d)", 1,
     1992, 30000, 80, "https://kiit.ac.in",
     "KIIT Bhubaneswar is one of the fastest-growing deemed universities in India. Known for its international student body, modern infrastructure and strong placement record across IT and core sectors."),

    ("Lovely Professional University",
     "LPU", "Phagwara, Jalandhar", "Punjab", "Private", "A+",
     None, 27, None, 50, "1560/2000",
     "₹6.60L", 6.60, "₹44 LPA", "₹5.5 LPA",
     "LPUNEST / JEE Main", "linear-gradient(135deg,#6b3a1a,#ab6a2d)", 1,
     2005, 50000, 72, "https://www.lpu.in",
     "LPU is India's largest residential university. It offers over 200 programs and has a diverse student body from 50+ countries. Known for affordable fees, good infrastructure and industry exposure."),

    ("Chandigarh University",
     "CU", "Mohali, Chandigarh", "Punjab", "Private", "A+",
     26, 28, 185, 38, "1610/2000",
     "₹7.20L", 7.20, "₹50 LPA", "₹6.8 LPA",
     "CUCET / JEE Main", "linear-gradient(135deg,#4a1a5a,#7a2d9a)", 1,
     2012, 28000, 77, "https://www.cuchd.in",
     "Chandigarh University is a rapidly growing university in Punjab, known for its modern campus, international tie-ups and strong placement drive. It is one of India's fastest-rising private universities."),

    ("Coimbatore Institute of Technology",
     "CIT", "Coimbatore", "Tamil Nadu", "Government", "A+",
     None, 29, None, 55, "1580/2000",
     "₹1.20L", 1.20, "₹28 LPA", "₹5.5 LPA",
     "TNEA", "linear-gradient(135deg,#1a3a3a,#2d6a6a)", 1,
     1956, 4500, 78, "https://www.cit.edu.in",
     "CIT Coimbatore is one of Tamil Nadu's top government-aided engineering colleges. Known for its highly affordable fees, good academics and strong alumni network in Coimbatore's industrial belt."),

    ("R.V. College of Engineering",
     "RVCE", "Bengaluru", "Karnataka", "Private", "A+",
     None, 30, None, 48, "1600/2000",
     "₹6.50L", 6.50, "₹58 LPA", "₹9.0 LPA",
     "KCET / COMEDK", "linear-gradient(135deg,#3a1a4a,#6a2d7a)", 1,
     1963, 6000, 84, "https://www.rvce.edu.in",
     "RVCE is one of Bangalore's top private engineering colleges, located close to the city's IT hub. It has strong industry connections with companies like Infosys, Wipro and many startups."),

    ("M.S. Ramaiah Institute of Technology",
     "MSRIT", "Bengaluru", "Karnataka", "Private", "A+",
     None, 31, None, 52, "1580/2000",
     "₹6.80L", 6.80, "₹52 LPA", "₹8.5 LPA",
     "KCET / COMEDK", "linear-gradient(135deg,#1a4a3a,#2d7a6a)", 1,
     1962, 6500, 82, "https://www.msrit.edu",
     "M.S. Ramaiah Institute of Technology is a premier private engineering college in Bangalore. Known for its strong CSE and ECE programs and excellent placement record with top MNCs."),

    ("Anna University",
     "Anna University", "Guindy, Chennai", "Tamil Nadu", "Government", "A++",
     17, 32, 150, 26, "1680/2000",
     "₹0.50L", 0.50, "₹45 LPA", "₹7.5 LPA",
     "TNEA", "linear-gradient(135deg,#6b1a3a,#ab2d6a)", 1,
     1978, 13000, 80, "https://www.annauniv.edu",
     "Anna University is Tamil Nadu's apex technical university. It affiliates over 500 engineering colleges in the state. Its main campus at Guindy is known for its strong research output and affordable fees."),

    # ── GREATER NOIDA COLLEGES ────────────────────────────────────────────────

    ("GL Bajaj Institute of Technology and Management",
     "GL Bajaj", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 33, None, 60, "1420/2000",
     "₹4.80L", 4.80, "₹18 LPA", "₹4.5 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#c47a1a,#e8a020)", 1,
     2008, 6000, 72, "https://www.glbitm.ac.in",
     "GL Bajaj Institute of Technology and Management is one of the top private engineering colleges in Greater Noida. It offers B.Tech, M.Tech and MBA programs with strong industry connections in the NCR region. Known for its active placement cell and modern labs."),

    ("Galgotias University",
     "Galgotias", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A+",
     None, 34, None, 55, "1450/2000",
     "₹6.20L", 6.20, "₹42 LPA", "₹5.8 LPA",
     "JEE Main / UPSEE / GAT", "linear-gradient(135deg,#1a4a8a,#2d72c8)", 1,
     2011, 18000, 75, "https://www.galgotiasuniversity.edu.in",
     "Galgotias University is a fast-growing private university in Greater Noida offering engineering, management, law and pharmacy programs. It has a large campus with modern infrastructure and attracts top recruiters from the IT and automotive sectors."),

    ("Galgotias College of Engineering and Technology",
     "GCET", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 35, None, 62, "1400/2000",
     "₹5.40L", 5.40, "₹32 LPA", "₹4.8 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a6a3a,#2da85a)", 1,
     2000, 7500, 70, "https://www.galgotiacollege.edu",
     "Galgotias College of Engineering and Technology (GCET) is one of Greater Noida's most established engineering colleges. It is AICTE approved and NBA accredited, known for its Computer Science and Mechanical Engineering programs."),

    ("Greater Noida Institute of Technology",
     "GNIOT", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "B+",
     None, 36, None, 70, "1350/2000",
     "₹4.20L", 4.20, "₹15 LPA", "₹3.8 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#8a1a1a,#c82d2d)", 1,
     1998, 5000, 65, "https://www.gniot.net",
     "GNIOT is a well-known engineering college in Greater Noida affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU). It offers B.Tech programs in CSE, ECE, ME and Civil Engineering with a focus on practical training."),

    ("Sharda University",
     "Sharda", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A+",
     None, 37, None, 48, "1480/2000",
     "₹7.80L", 7.80, "₹38 LPA", "₹6.2 LPA",
     "JEE Main / SU JEE", "linear-gradient(135deg,#5a1a6a,#8a2daa)", 1,
     2009, 20000, 74, "https://www.sharda.ac.in",
     "Sharda University is a prominent private university in Greater Noida with a large international student community from 80+ countries. It offers engineering, medical, law and management programs and has strong placement records in IT and finance sectors."),

    ("Bennett University",
     "Bennett", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 38, None, 45, "1500/2000",
     "₹10.50L", 10.50, "₹45 LPA", "₹7.5 LPA",
     "JEE Main / Bennett Entrance Test", "linear-gradient(135deg,#c41a1a,#e82d2d)", 1,
     2016, 5000, 78, "https://www.bennett.edu.in",
     "Bennett University, promoted by The Times Group, is a modern private university in Greater Noida. Known for its excellent CSE and media programs, entrepreneurship culture and strong industry tie-ups with top tech companies and media houses."),

    ("Noida Institute of Engineering and Technology",
     "NIET", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 39, None, 65, "1380/2000",
     "₹4.60L", 4.60, "₹22 LPA", "₹4.2 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a3a6a,#2d5aaa)", 1,
     2001, 8000, 68, "https://www.niet.co.in",
     "NIET Greater Noida is a leading AKTU-affiliated engineering college. It is NBA and NAAC accredited and known for its vibrant campus life, active training and placement cell, and strong alumni network across NCR industries."),

    ("JSS Academy of Technical Education Noida",
     "JSS Noida", "Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 40, None, 68, "1370/2000",
     "₹5.00L", 5.00, "₹28 LPA", "₹5.0 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#2a5a1a,#4a9a2d)", 1,
     1998, 4500, 71, "https://www.jssaten.ac.in",
     "JSS Academy of Technical Education Noida is a well-regarded private engineering college near Greater Noida. Run by the JSS Mahavidyapeetha, it is known for its discipline, quality academics and good placement record with IT and core companies."),

    ("Hindustan College of Science and Technology",
     "HCST", "Mathura, Near Greater Noida", "Uttar Pradesh", "Private", "B+",
     None, 41, None, 75, "1320/2000",
     "₹3.80L", 3.80, "₹12 LPA", "₹3.2 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#6a4a1a,#aa7a2d)", 1,
     2000, 4000, 62, "https://www.hcst.edu.in",
     "Hindustan College of Science and Technology is an AKTU-affiliated engineering college serving students from Greater Noida and surrounding districts. It offers affordable B.Tech programs in CSE, ECE and Mechanical Engineering."),

    ("Delhi Institute of Technological Sciences (DITS)",
     "DITS", "Bhagyanagar, Greater Noida", "Uttar Pradesh", "Private", "B",
     None, 42, None, 80, "1290/2000",
     "₹3.50L", 3.50, "₹10 LPA", "₹3.0 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a1a4a,#2d2d8a)", 1,
     2007, 3000, 60, "https://www.ditsgreaternoida.com",
     "DITS is an AICTE-approved engineering college in Greater Noida offering B.Tech programs affiliated to AKTU. It is known for affordable fees and a student-friendly campus environment with focus on practical engineering skills."),

    ("Skyline Institute of Engineering and Technology",
     "SIET", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "B+",
     None, 43, None, 78, "1310/2000",
     "₹3.60L", 3.60, "₹11 LPA", "₹3.2 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a5a5a,#2d9a9a)", 1,
     2008, 2800, 61, "https://www.skylineinstitutions.ac.in",
     "Skyline Institute of Engineering and Technology is an AKTU-affiliated college in Greater Noida. It offers B.Tech in CSE, ECE and ME with emphasis on skill development and campus placements in the NCR belt."),

    ("Lloyd Institute of Engineering and Technology",
     "Lloyd IET", "Greater Noida, Uttar Pradesh", "Uttar Pradesh", "Private", "A",
     None, 44, None, 63, "1360/2000",
     "₹4.40L", 4.40, "₹20 LPA", "₹4.0 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#4a1a4a,#7a2d7a)", 1,
     2008, 4200, 66, "https://www.lloydinstitutions.com",
     "Lloyd Institute of Engineering and Technology Greater Noida is a reputed AKTU-affiliated college known for its Computer Science and Management programs. It has a strong industry interface with companies operating in the NCR and Delhi corridor."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 1 — JHARKHAND
    # ════════════════════════════════════════════════════════════════════════

    ("Birla Institute of Technology Mesra",
     "BIT Mesra", "Mesra, Ranchi", "Jharkhand", "Deemed", "A",
     57, 45, None, 38, "1560/2000",
     "₹9.10L", 9.10, "₹35 LPA", "₹7.8 LPA",
     "JEE Main", "linear-gradient(135deg,#5a1a1a,#9a2d2d)", 1,
     1955, 7500, 79, "https://www.bitmesra.ac.in",
     "BIT Mesra is one of the oldest and most prestigious engineering institutes in Jharkhand. Situated in a lush green campus near Ranchi, it is a deemed university offering B.Tech, M.Tech and PhD programs. Known for strong placements in IT and core engineering."),

    ("National Institute of Technology Jamshedpur",
     "NIT Jamshedpur", "Jamshedpur", "Jharkhand", "Government", "A",
     30, 46, None, 40, "1540/2000",
     "₹5.60L", 5.60, "₹40 LPA", "₹8.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a3a5a,#2d6a9a)", 1,
     1960, 4500, 82, "https://www.nitjsr.ac.in",
     "NIT Jamshedpur is one of the premier government engineering institutes in Jharkhand. Located in the steel city of Jamshedpur, it has excellent industry connections with Tata Steel, TISCO and other companies. Strong in Mechanical and Metallurgical Engineering."),

    ("Jharkhand University of Technology",
     "JUT", "Ranchi", "Jharkhand", "Government", "B+",
     None, 47, None, 72, "1300/2000",
     "₹1.80L", 1.80, "₹12 LPA", "₹3.5 LPA",
     "JCECE", "linear-gradient(135deg,#3a5a1a,#6a9a2d)", 1,
     2004, 6000, 60, "https://www.jut.ac.in",
     "Jharkhand University of Technology is the state technical university affiliating engineering colleges across Jharkhand. It offers affordable B.Tech programs to students from Jharkhand and neighboring states."),

    ("RVS College of Engineering and Technology",
     "RVS CET", "Jamshedpur", "Jharkhand", "Private", "B+",
     None, 48, None, 80, "1270/2000",
     "₹3.20L", 3.20, "₹10 LPA", "₹3.0 LPA",
     "JEE Main / JCECE", "linear-gradient(135deg,#5a3a1a,#9a6a2d)", 1,
     2008, 3000, 58, "https://www.rvscet.ac.in",
     "RVS College of Engineering and Technology is a private engineering college in Jamshedpur offering B.Tech programs in CSE, ECE and Mechanical Engineering. Known for affordable fees and proximity to industrial hubs in the Jamshedpur belt."),

    ("Dumka Engineering College",
     "DEC", "Dumka", "Jharkhand", "Government", "B",
     None, 49, None, 90, "1200/2000",
     "₹1.20L", 1.20, "₹8 LPA", "₹2.8 LPA",
     "JCECE", "linear-gradient(135deg,#1a4a3a,#2d7a6a)", 1,
     2010, 1500, 52, "https://www.dumkaenggcollege.ac.in",
     "Dumka Engineering College is a government engineering college in Dumka, Jharkhand catering to students from Santhal Pargana region. It offers AICTE approved B.Tech programs at very affordable fees."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 2 — BIHAR
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Patna",
     "NIT Patna", "Patna", "Bihar", "Government", "A",
     35, 50, None, 42, "1520/2000",
     "₹5.40L", 5.40, "₹38 LPA", "₹8.0 LPA",
     "JEE Main", "linear-gradient(135deg,#5a1a3a,#9a2d6a)", 1,
     1886, 4000, 80, "https://www.nitp.ac.in",
     "NIT Patna is one of the oldest technical institutes in Bihar, originally established in 1886. It is a premier government institute offering B.Tech, M.Tech and PhD programs. Strong in Civil, Electrical and Computer Science Engineering."),

    ("Indian Institute of Technology Patna",
     "IIT Patna", "Bihta, Patna", "Bihar", "Government", "A+",
     29, 51, None, 35, "1600/2000",
     "₹8.00L", 8.00, "₹95 LPA", "₹14.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a5a2a,#2d9a4a)", 1,
     2008, 2500, 85, "https://www.iitp.ac.in",
     "IIT Patna is a new-generation IIT in Bihar offering world-class engineering education. Despite being relatively new, it has quickly built a strong reputation for research and industry placements with top tech and core engineering companies."),

    ("Muzaffarpur Institute of Technology",
     "MIT Muzaffarpur", "Muzaffarpur", "Bihar", "Government", "B+",
     None, 52, None, 85, "1240/2000",
     "₹1.60L", 1.60, "₹10 LPA", "₹3.2 LPA",
     "JEE Main / BCECE", "linear-gradient(135deg,#1a1a5a,#2d2d9a)", 1,
     1954, 2800, 58, "https://www.mitmuzaffarpur.org",
     "Muzaffarpur Institute of Technology is a government engineering college in Muzaffarpur, Bihar. One of the oldest engineering colleges in the state, it offers B.Tech programs at highly affordable fees for students from North Bihar."),

    ("Gaya College of Engineering",
     "GCE Gaya", "Gaya", "Bihar", "Government", "B+",
     None, 53, None, 88, "1220/2000",
     "₹1.40L", 1.40, "₹9 LPA", "₹3.0 LPA",
     "JEE Main / BCECE", "linear-gradient(135deg,#4a1a5a,#7a2d8a)", 1,
     2008, 2000, 55, "https://www.gcegaya.ac.in",
     "Gaya College of Engineering is a government engineering college in Gaya serving students from South Bihar and Jharkhand border areas. It offers AICTE approved B.Tech programs in major engineering disciplines."),

    ("Patna Women's College",
     "PWC Patna", "Patna", "Bihar", "Private", "A+",
     None, 54, None, 60, "1380/2000",
     "₹0.90L", 0.90, "₹12 LPA", "₹4.0 LPA",
     "Entrance Test", "linear-gradient(135deg,#6a1a4a,#aa2d7a)", 1,
     1946, 3500, 65, "https://www.patnawomenscollege.in",
     "Patna Women's College is a premier autonomous college affiliated to Patna University. It is one of the most prestigious women's colleges in Bihar offering science, arts and commerce programs with a strong academic tradition."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 3 — UTTAR PRADESH (additional cities beyond Greater Noida)
    # ════════════════════════════════════════════════════════════════════════

    ("Harcourt Butler Technical University",
     "HBTU", "Kanpur", "Uttar Pradesh", "Government", "A",
     None, 55, None, 45, "1500/2000",
     "₹1.60L", 1.60, "₹32 LPA", "₹6.5 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a4a6a,#2d7aaa)", 1,
     1921, 5000, 75, "https://hbtu.ac.in",
     "Harcourt Butler Technical University Kanpur is one of the oldest and most reputed government technical universities in UP. Formerly HBTI, it is known for its Chemical Engineering, Mechanical and IT programs with strong industry ties in Kanpur's industrial belt."),

    ("Madan Mohan Malaviya University of Technology",
     "MMMUT", "Gorakhpur", "Uttar Pradesh", "Government", "A",
     None, 56, None, 50, "1470/2000",
     "₹1.50L", 1.50, "₹28 LPA", "₹5.8 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#3a1a6a,#6a2daa)", 1,
     1962, 4500, 72, "https://www.mmmut.ac.in",
     "MMMUT Gorakhpur is a prestigious state government technical university in eastern UP. Known for its affordable fees and strong academic programs, it is a top choice for students from Gorakhpur, Varanasi and surrounding districts."),

    ("Bundelkhand Institute of Engineering and Technology",
     "BIET Jhansi", "Jhansi", "Uttar Pradesh", "Government", "A",
     None, 57, None, 55, "1440/2000",
     "₹1.40L", 1.40, "₹22 LPA", "₹5.0 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#6a3a1a,#aa6a2d)", 1,
     1960, 3800, 68, "https://www.bietjhs.ac.in",
     "BIET Jhansi is a government engineering college in Bundelkhand region, one of UP's most established technical institutes. It serves students from Jhansi, Lalitpur, Banda and neighboring districts with affordable quality engineering education."),

    ("Dr. APJ Abdul Kalam Technical University",
     "AKTU", "Lucknow", "Uttar Pradesh", "Government", "A+",
     None, 58, None, 35, "1550/2000",
     "₹0.00L", 0.00, "₹45 LPA", "₹7.0 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a6a1a,#2daa2d)", 1,
     2000, 500000, 70, "https://www.aktu.ac.in",
     "AKTU (formerly UPTU) is the apex technical university in Uttar Pradesh, affiliating over 700 engineering and management colleges across the state. Students searching for UP colleges will find most institutions are AKTU affiliated."),

    ("Institute of Engineering and Technology Lucknow",
     "IET Lucknow", "Lucknow", "Uttar Pradesh", "Government", "A",
     None, 59, None, 48, "1490/2000",
     "₹1.55L", 1.55, "₹30 LPA", "₹6.2 LPA",
     "JEE Main / UPSEE", "linear-gradient(135deg,#1a3a6a,#2d5aaa)", 1,
     1984, 4200, 73, "https://ietlucknow.ac.in",
     "IET Lucknow is one of the most reputed government engineering colleges in UP, situated in the state capital Lucknow. It is affiliated to AKTU and known for its strong academics, active placement cell and alumni across top Indian and global companies."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 4 — WEST BENGAL / KOLKATA
    # ════════════════════════════════════════════════════════════════════════

    ("Jadavpur University",
     "JU", "Jadavpur, Kolkata", "West Bengal", "Government", "A++",
     12, 60, None, 20, "1710/2000",
     "₹0.36L", 0.36, "₹42 LPA", "₹8.0 LPA",
     "WBJEE", "linear-gradient(135deg,#1a6b5a,#2dab8a)", 1,
     1955, 8500, 84, "https://jadavpuruniversity.in",
     "Jadavpur University Kolkata is consistently ranked among the top universities in India. Its Faculty of Engineering is one of the best in the country, offering programs at extremely affordable fees. Strong alumni base in FAANG companies and research institutions globally."),

    ("Indian Institute of Engineering Science and Technology Shibpur",
     "IIEST Shibpur", "Howrah, Kolkata", "West Bengal", "Government", "A",
     25, 61, None, 28, "1620/2000",
     "₹3.20L", 3.20, "₹38 LPA", "₹7.5 LPA",
     "JEE Main / WBJEE", "linear-gradient(135deg,#4a1a6a,#7a2daa)", 1,
     1856, 5500, 80, "https://www.iiest.ac.in",
     "IIEST Shibpur is one of the oldest technical institutes in Asia, established in 1856. Located in Howrah near Kolkata, it is a premier government institute offering strong programs in Civil, Mechanical and Electrical Engineering."),

    ("Heritage Institute of Technology Kolkata",
     "Heritage Tech", "Anandapur, Kolkata", "West Bengal", "Private", "A+",
     None, 62, None, 55, "1420/2000",
     "₹5.80L", 5.80, "₹32 LPA", "₹6.5 LPA",
     "WBJEE / JEE Main", "linear-gradient(135deg,#6a1a1a,#aa2d2d)", 1,
     1999, 5000, 76, "https://www.heritageit.edu",
     "Heritage Institute of Technology is a top private engineering college in Kolkata affiliated to Maulana Abul Kalam Azad University of Technology (MAKAUT). Known for its CSE, ECE and IT programs with strong placement record in Kolkata's IT sector."),

    ("Calcutta Institute of Engineering and Management",
     "CIEM", "Tollygunge, Kolkata", "West Bengal", "Private", "A",
     None, 63, None, 65, "1380/2000",
     "₹4.80L", 4.80, "₹24 LPA", "₹5.2 LPA",
     "WBJEE / JEE Main", "linear-gradient(135deg,#1a4a5a,#2d7a8a)", 1,
     2000, 4200, 72, "https://www.ciem.ac.in",
     "CIEM Kolkata is a reputed private engineering college in South Kolkata offering B.Tech programs in Computer Science, IT, ECE and Mechanical Engineering. It is affiliated to MAKAUT and known for its active industry interface and placement support."),

    ("Techno India University",
     "Techno India", "EM Bypass, Kolkata", "West Bengal", "Private", "A",
     None, 64, None, 60, "1390/2000",
     "₹5.20L", 5.20, "₹28 LPA", "₹5.5 LPA",
     "WBJEE / JEE Main", "linear-gradient(135deg,#1a1a6a,#2d2daa)", 1,
     2012, 8000, 74, "https://www.technoindiauniversity.ac.in",
     "Techno India University is a private university in Kolkata offering engineering, management and science programs. Located on the EM Bypass, it is well-connected to Kolkata's IT hub and has strong placement ties with companies in Sector V, Salt Lake."),

    ("Meghnad Saha Institute of Technology",
     "MSIT", "Uchhepota, Kolkata", "West Bengal", "Private", "A",
     None, 65, None, 62, "1370/2000",
     "₹5.00L", 5.00, "₹26 LPA", "₹5.0 LPA",
     "WBJEE / JEE Main", "linear-gradient(135deg,#3a5a1a,#6a9a2d)", 1,
     2001, 3800, 71, "https://www.msit.edu.in",
     "Meghnad Saha Institute of Technology is a reputed private engineering college in Kolkata affiliated to MAKAUT. Named after the famous physicist Meghnad Saha, it offers strong programs in CSE, ECE and Electrical Engineering with good placement support."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 5 — RAJASTHAN
    # ════════════════════════════════════════════════════════════════════════

    ("Malaviya National Institute of Technology",
     "MNIT Jaipur", "Jaipur", "Rajasthan", "Government", "A+",
     38, 66, None, 32, "1600/2000",
     "₹5.50L", 5.50, "₹55 LPA", "₹10.5 LPA",
     "JEE Main", "linear-gradient(135deg,#6a3a1a,#aa6a2d)", 1,
     1963, 5500, 83, "https://www.mnit.ac.in",
     "MNIT Jaipur is one of the top NITs in India located in the Pink City. Known for its strong Computer Science, Electrical and Mechanical Engineering programs. Excellent placement record with top IT and core companies. The campus is modern and well-equipped."),

    ("Rajasthan Technical University",
     "RTU", "Kota", "Rajasthan", "Government", "A",
     None, 67, None, 50, "1460/2000",
     "₹1.20L", 1.20, "₹22 LPA", "₹4.5 LPA",
     "JEE Main / REAP", "linear-gradient(135deg,#1a4a6a,#2d7aaa)", 1,
     2006, 12000, 65, "https://www.rtu.ac.in",
     "Rajasthan Technical University Kota is the state technical university affiliating over 200 engineering colleges in Rajasthan. Kota is famous as India's coaching hub and RTU provides quality engineering education to students in this academic city."),

    ("College of Engineering and Technology Bikaner",
     "CET Bikaner", "Bikaner", "Rajasthan", "Government", "B+",
     None, 68, None, 75, "1280/2000",
     "₹1.10L", 1.10, "₹14 LPA", "₹3.5 LPA",
     "JEE Main / REAP", "linear-gradient(135deg,#6a5a1a,#aaaa2d)", 1,
     2006, 2500, 60, "https://www.cetbikaner.ac.in",
     "CET Bikaner is a government engineering college in the desert city of Bikaner, Rajasthan. It offers affordable B.Tech programs and serves students from Bikaner, Jodhpur and surrounding districts of western Rajasthan."),

    ("Poornima College of Engineering",
     "Poornima CE", "Jaipur", "Rajasthan", "Private", "A",
     None, 69, None, 58, "1380/2000",
     "₹5.80L", 5.80, "₹28 LPA", "₹5.5 LPA",
     "JEE Main / REAP", "linear-gradient(135deg,#5a1a5a,#9a2d9a)", 1,
     2000, 5500, 72, "https://www.poornima.org",
     "Poornima College of Engineering is one of Jaipur's top private engineering colleges. Part of the Poornima Group of Colleges, it is known for its modern infrastructure, industry-ready curriculum and strong placement record with IT companies in Jaipur's growing tech sector."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 6 — MADHYA PRADESH
    # ════════════════════════════════════════════════════════════════════════

    ("Indian Institute of Technology Indore",
     "IIT Indore", "Simrol, Indore", "Madhya Pradesh", "Government", "A++",
     10, 70, None, 22, "1780/2000",
     "₹8.20L", 8.20, "₹1.10 CR", "₹17.5 LPA",
     "JEE Advanced", "linear-gradient(135deg,#1a3a6a,#2d5aaa)", 1,
     2009, 3200, 88, "https://www.iiti.ac.in",
     "IIT Indore is a top-ranked IIT in Madhya Pradesh, known for its cutting-edge research in science and engineering. Despite being a newer IIT, it has quickly risen in rankings and commands excellent placements with top global tech companies."),

    ("National Institute of Technology Bhopal",
     "MANIT Bhopal", "Bhopal", "Madhya Pradesh", "Government", "A",
     31, 71, None, 38, "1560/2000",
     "₹5.30L", 5.30, "₹42 LPA", "₹8.5 LPA",
     "JEE Main", "linear-gradient(135deg,#3a1a5a,#6a2d9a)", 1,
     1960, 5000, 80, "https://www.manit.ac.in",
     "MANIT Bhopal (Maulana Azad National Institute of Technology) is a premier NIT in Madhya Pradesh. Located in the state capital Bhopal, it is known for strong programs in Civil, Mechanical, Electrical and Computer Science Engineering."),

    ("Shri Govindram Seksaria Institute of Technology and Science",
     "SGSITS Indore", "Indore", "Madhya Pradesh", "Government", "A",
     None, 72, None, 52, "1450/2000",
     "₹1.80L", 1.80, "₹30 LPA", "₹6.0 LPA",
     "JEE Main / MP PET", "linear-gradient(135deg,#1a5a3a,#2d9a6a)", 1,
     1952, 4500, 74, "https://www.sgsits.ac.in",
     "SGSITS Indore is one of the oldest and most prestigious government engineering colleges in MP. Located in the commercial capital of MP, Indore, it offers excellent B.Tech programs with strong placement support from companies in Indore's growing IT and manufacturing sector."),

    ("Lakshmi Narain College of Technology",
     "LNCT Bhopal", "Bhopal", "Madhya Pradesh", "Private", "A",
     None, 73, None, 60, "1380/2000",
     "₹4.60L", 4.60, "₹22 LPA", "₹4.8 LPA",
     "JEE Main / MP PET", "linear-gradient(135deg,#6a1a3a,#aa2d5a)", 1,
     1994, 12000, 70, "https://www.lnct.ac.in",
     "LNCT Bhopal is one of MP's largest private engineering colleges, part of the LNCT Group. It offers B.Tech programs across multiple branches and is known for its affordable fees, large campus and extensive placement support in Bhopal and surrounding regions."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 7 — GUJARAT
    # ════════════════════════════════════════════════════════════════════════

    ("Indian Institute of Technology Gandhinagar",
     "IIT Gandhinagar", "Palaj, Gandhinagar", "Gujarat", "Government", "A++",
     13, 74, None, 24, "1750/2000",
     "₹8.15L", 8.15, "₹1.05 CR", "₹16.8 LPA",
     "JEE Advanced", "linear-gradient(135deg,#5a3a1a,#9a6a2d)", 1,
     2008, 2800, 87, "https://www.iitgn.ac.in",
     "IIT Gandhinagar is one of the newer IITs known for its innovative teaching approach, design thinking curriculum and strong research culture. Located near Ahmedabad, it benefits from Gujarat's thriving industrial and startup ecosystem."),

    ("Nirma University",
     "Nirma", "Ahmedabad", "Gujarat", "Deemed", "A+",
     50, 75, None, 40, "1500/2000",
     "₹11.50L", 11.50, "₹44 LPA", "₹8.2 LPA",
     "JEE Main / GUJCET", "linear-gradient(135deg,#1a5a5a,#2d9a9a)", 1,
     2003, 9000, 81, "https://www.nirmauni.ac.in",
     "Nirma University Ahmedabad is a top-ranked deemed university in Gujarat offering engineering, pharmacy, management and law programs. Known for its modern campus, industry-oriented curriculum and strong placement record with companies in Ahmedabad's industrial corridor."),

    ("Dharmsinh Desai University",
     "DDU Nadiad", "Nadiad", "Gujarat", "Deemed", "A",
     None, 76, None, 48, "1470/2000",
     "₹8.80L", 8.80, "₹35 LPA", "₹7.0 LPA",
     "JEE Main / GUJCET", "linear-gradient(135deg,#3a1a6a,#6a2daa)", 1,
     1968, 4000, 78, "https://www.ddu.ac.in",
     "DDU Nadiad is a premier deemed university in Gujarat known for its excellent Computer Science, IT and Electronics programs. It has strong ties with pharma and IT industries in Gujarat and consistently produces job-ready graduates."),

    ("L.D. College of Engineering",
     "LDCE", "Ahmedabad", "Gujarat", "Government", "A+",
     None, 77, None, 42, "1510/2000",
     "₹0.60L", 0.60, "₹38 LPA", "₹7.2 LPA",
     "JEE Main / GUJCET", "linear-gradient(135deg,#1a3a1a,#2d6a2d)", 1,
     1948, 6500, 79, "https://ldce.ac.in",
     "LD College of Engineering Ahmedabad is one of Gujarat's oldest and most prestigious government engineering colleges. Known for its very affordable fees and strong academic tradition, it is highly sought after by students across Gujarat for its CSE and Mechanical programs."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 8 — ANDHRA PRADESH
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Warangal",
     "NIT Warangal", "Warangal", "Andhra Pradesh", "Government", "A+",
     23, 78, None, 15, "1790/2000",
     "₹4.90L", 4.90, "₹65 LPA", "₹11.8 LPA",
     "JEE Main", "linear-gradient(135deg,#3a1a5a,#6a2d9a)", 1,
     1959, 6200, 88, "https://www.nitw.ac.in",
     "NIT Warangal is one of the top NITs in India, now in Telangana but historically from the combined AP. Highly regarded for CSE, ECE and Mechanical Engineering. Consistently strong placements with top MNCs and product companies globally."),

    ("Andhra University College of Engineering",
     "AU Engineering", "Visakhapatnam", "Andhra Pradesh", "Government", "A+",
     None, 79, None, 45, "1480/2000",
     "₹0.80L", 0.80, "₹28 LPA", "₹5.5 LPA",
     "AP EAMCET", "linear-gradient(135deg,#1a5a6a,#2d8aaa)", 1,
     1935, 7000, 72, "https://www.andhrauniversity.edu.in",
     "Andhra University College of Engineering in Visakhapatnam is one of the oldest engineering colleges in South India. Known for its strong academics, affordable fees and alumni network across India and abroad, especially in the US tech industry."),

    ("Jawaharlal Nehru Technological University Anantapur",
     "JNTU Anantapur", "Anantapur", "Andhra Pradesh", "Government", "A",
     None, 80, None, 52, "1440/2000",
     "₹1.10L", 1.10, "₹20 LPA", "₹4.2 LPA",
     "AP EAMCET", "linear-gradient(135deg,#6a4a1a,#aa7a2d)", 1,
     2008, 8000, 66, "https://www.jntua.ac.in",
     "JNTU Anantapur is the state technical university for the Rayalaseema region of Andhra Pradesh. It affiliates hundreds of engineering colleges and directly offers B.Tech programs at its main campus, catering to students from districts like Kurnool, Kadapa and Chittoor."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 9 — TELANGANA
    # ════════════════════════════════════════════════════════════════════════

    ("Osmania University College of Engineering",
     "OUCE", "Hyderabad", "Telangana", "Government", "A+",
     None, 81, None, 38, "1530/2000",
     "₹0.70L", 0.70, "₹32 LPA", "₹6.5 LPA",
     "TS EAMCET", "linear-gradient(135deg,#5a1a4a,#9a2d7a)", 1,
     1929, 5000, 74, "https://www.osmania.ac.in",
     "Osmania University College of Engineering Hyderabad is one of the oldest engineering colleges in South India. Part of the prestigious Osmania University, it offers quality engineering education at very affordable fees with strong alumni in Hyderabad's massive IT industry."),

    ("Chaitanya Bharathi Institute of Technology",
     "CBIT", "Gandipet, Hyderabad", "Telangana", "Private", "A+",
     None, 82, None, 42, "1510/2000",
     "₹5.50L", 5.50, "₹38 LPA", "₹7.8 LPA",
     "TS EAMCET / JEE Main", "linear-gradient(135deg,#1a3a5a,#2d6a9a)", 1,
     1979, 5500, 80, "https://www.cbit.ac.in",
     "CBIT Hyderabad is one of Telangana's top private engineering colleges, known for its strong CSE, ECE and IT programs. Located near Hyderabad's HITEC City, it has excellent industry connections with companies like TCS, Infosys, Wipro and many product startups."),

    ("Vasavi College of Engineering",
     "Vasavi CE", "Ibrahimbagh, Hyderabad", "Telangana", "Private", "A+",
     None, 83, None, 44, "1500/2000",
     "₹5.20L", 5.20, "₹36 LPA", "₹7.5 LPA",
     "TS EAMCET / JEE Main", "linear-gradient(135deg,#3a5a1a,#6a9a2d)", 1,
     1981, 4800, 79, "https://www.vasaviengg.ac.in",
     "Vasavi College of Engineering is a reputed autonomous private college in Hyderabad affiliated to Osmania University. It is known for its high academic standards, active industry linkages and strong placement record with Hyderabad's booming IT sector."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 10 — KERALA
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Calicut",
     "NIT Calicut", "Kozhikode", "Kerala", "Government", "A+",
     21, 84, None, 18, "1720/2000",
     "₹5.20L", 5.20, "₹48 LPA", "₹9.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a5a3a,#2d9a6a)", 1,
     1961, 5800, 85, "https://nitc.ac.in",
     "NIT Calicut is one of the top NITs in India located in Kerala. Highly regarded for its Computer Science, Electrical and Civil Engineering programs. Strong placement record with IT and core companies. Known for its beautiful campus and disciplined academic environment."),

    ("College of Engineering Trivandrum",
     "CET TVM", "Thiruvananthapuram", "Kerala", "Government", "A+",
     None, 85, None, 40, "1510/2000",
     "₹0.55L", 0.55, "₹36 LPA", "₹7.0 LPA",
     "KEAM", "linear-gradient(135deg,#1a1a5a,#2d2d9a)", 1,
     1939, 3500, 78, "https://www.cet.ac.in",
     "College of Engineering Trivandrum is Kerala's oldest and most prestigious government engineering college. Known for its extremely affordable fees and high academic standards, it produces graduates who excel in ISRO, DRDO and top IT companies globally."),

    ("Model Engineering College Kochi",
     "MEC Kochi", "Thrikkakara, Kochi", "Kerala", "Government", "A",
     None, 86, None, 48, "1470/2000",
     "₹0.50L", 0.50, "₹32 LPA", "₹6.5 LPA",
     "KEAM", "linear-gradient(135deg,#5a3a1a,#9a6a2d)", 1,
     1989, 2800, 76, "https://www.mec.ac.in",
     "Model Engineering College Kochi is a prestigious government engineering college in Kerala's commercial capital. Known for its strong CSE and IT programs, it benefits from Kochi's growing IT sector and strong alumni network in the Middle East and Silicon Valley."),

    ("Amrita Vishwa Vidyapeetham",
     "Amrita", "Coimbatore / Kochi", "Kerala", "Deemed", "A++",
     22, 87, None, 30, "1680/2000",
     "₹9.80L", 9.80, "₹48 LPA", "₹8.5 LPA",
     "JEE Main / AEEE", "linear-gradient(135deg,#6a1a5a,#aa2d9a)", 1,
     1994, 20000, 82, "https://www.amrita.edu",
     "Amrita Vishwa Vidyapeetham is a top-ranked deemed university with campuses in Kerala, Tamil Nadu and Karnataka. NAAC A++ accredited and highly regarded for its CSE, ECE and Biomedical Engineering programs. Strong international collaborations and research output."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 11 — ODISHA
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Rourkela",
     "NIT Rourkela", "Rourkela", "Odisha", "Government", "A+",
     19, 88, None, 22, "1700/2000",
     "₹5.50L", 5.50, "₹52 LPA", "₹10.2 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a3a,#2d7a6a)", 1,
     1961, 6000, 84, "https://www.nitrkl.ac.in",
     "NIT Rourkela is one of the top NITs in India located in Odisha. Highly ranked for its Metallurgical, Mechanical and Computer Science Engineering programs. Benefits from proximity to Rourkela Steel Plant and major industries in the steel belt."),

    ("College of Engineering and Technology Bhubaneswar",
     "CET Bhubaneswar", "Bhubaneswar", "Odisha", "Government", "A",
     None, 89, None, 55, "1420/2000",
     "₹1.30L", 1.30, "₹22 LPA", "₹4.5 LPA",
     "JEE Main / OJEE", "linear-gradient(135deg,#3a1a3a,#6a2d6a)", 1,
     1981, 4000, 68, "https://www.cet.edu.in",
     "CET Bhubaneswar is Odisha's top government engineering college after NIT Rourkela. Located in the state capital, it offers affordable B.Tech programs with strong placements in Bhubaneswar's growing IT sector and government engineering departments."),

    ("Silicon Institute of Technology",
     "Silicon Bhubaneswar", "Bhubaneswar", "Odisha", "Private", "A",
     None, 90, None, 62, "1380/2000",
     "₹4.20L", 4.20, "₹20 LPA", "₹4.2 LPA",
     "JEE Main / OJEE", "linear-gradient(135deg,#1a3a5a,#2d6a9a)", 1,
     2001, 3500, 70, "https://www.silicon.ac.in",
     "Silicon Institute of Technology Bhubaneswar is one of Odisha's top private engineering colleges. NAAC A accredited and affiliated to BPUT, it is known for its CSE and Electronics programs and strong placements in IT companies operating in Bhubaneswar's Infocity."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 12 — PUNJAB & HARYANA
    # ════════════════════════════════════════════════════════════════════════

    ("Punjab Engineering College",
     "PEC Chandigarh", "Chandigarh", "Punjab", "Deemed", "A+",
     53, 91, None, 35, "1540/2000",
     "₹4.80L", 4.80, "₹55 LPA", "₹10.0 LPA",
     "JEE Main", "linear-gradient(135deg,#5a1a6a,#9a2daa)", 1,
     1947, 4500, 82, "https://pec.ac.in",
     "Punjab Engineering College Chandigarh is one of India's oldest engineering institutions. A deemed university, it is located in the Union Territory of Chandigarh and known for its excellent Aerospace, Mechanical and Computer Science Engineering programs."),

    ("National Institute of Technology Kurukshetra",
     "NIT Kurukshetra", "Kurukshetra", "Haryana", "Government", "A",
     27, 92, None, 30, "1620/2000",
     "₹5.40L", 5.40, "₹45 LPA", "₹9.2 LPA",
     "JEE Main", "linear-gradient(135deg,#6a4a1a,#aa7a2d)", 1,
     1963, 5200, 81, "https://nitkkr.ac.in",
     "NIT Kurukshetra is a premier NIT in Haryana, located near the historic city of Kurukshetra. Known for its strong Electrical, Mechanical and Computer Science programs. Good placement record with IT and core companies from NCR and beyond."),

    ("Guru Nanak Dev Engineering College",
     "GNDEC", "Ludhiana", "Punjab", "Government", "A+",
     None, 93, None, 50, "1460/2000",
     "₹1.50L", 1.50, "₹28 LPA", "₹5.5 LPA",
     "JEE Main / PMET", "linear-gradient(135deg,#1a5a2a,#2d9a4a)", 1,
     1956, 4000, 73, "https://www.gndec.ac.in",
     "GNDEC Ludhiana is one of Punjab's most reputed government engineering colleges. Located in Punjab's industrial capital Ludhiana, it has strong connections with the city's manufacturing and textile industry alongside growing IT placements."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 13 — ASSAM & NORTH EAST
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Silchar",
     "NIT Silchar", "Silchar", "Assam", "Government", "A",
     36, 94, None, 45, "1510/2000",
     "₹5.30L", 5.30, "₹40 LPA", "₹8.2 LPA",
     "JEE Main", "linear-gradient(135deg,#1a3a6a,#2d5aaa)", 1,
     1967, 4500, 79, "https://nits.ac.in",
     "NIT Silchar is the premier government engineering institute for Northeast India. Located in Silchar, Assam, it offers strong B.Tech and M.Tech programs. Known for its diverse student community from all NE states and strong placements in IT and core sectors."),

    ("Assam Engineering College",
     "AEC Guwahati", "Guwahati", "Assam", "Government", "A",
     None, 95, None, 58, "1420/2000",
     "₹0.80L", 0.80, "₹18 LPA", "₹4.0 LPA",
     "JEE Main / ASTU", "linear-gradient(135deg,#3a5a1a,#6a9a2d)", 1,
     1955, 3500, 66, "https://aec.ac.in",
     "Assam Engineering College Guwahati is the oldest and most prestigious government engineering college in Assam. Affiliated to Assam Science and Technology University, it offers quality B.Tech programs at very affordable fees to students from across Northeast India."),

    ("Tezpur University",
     "Tezpur University", "Tezpur", "Assam", "Government", "A+",
     61, 96, None, 42, "1490/2000",
     "₹2.50L", 2.50, "₹22 LPA", "₹5.0 LPA",
     "JEE Main / University Exam", "linear-gradient(135deg,#5a3a1a,#9a6a2d)", 1,
     1994, 5000, 71, "https://www.tezu.ernet.in",
     "Tezpur University is a central university in Assam offering engineering, science and humanities programs. Known for its peaceful riverside campus, strong research output and good placement support for students from the Northeast region."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 14 — HIMACHAL PRADESH & UTTARAKHAND
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Hamirpur",
     "NIT Hamirpur", "Hamirpur", "Himachal Pradesh", "Government", "A",
     43, 97, None, 48, "1490/2000",
     "₹5.20L", 5.20, "₹38 LPA", "₹8.0 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a5a,#2d7a8a)", 1,
     1986, 4200, 78, "https://nith.ac.in",
     "NIT Hamirpur is a premier NIT nestled in the hills of Himachal Pradesh. Known for its scenic campus, strong Computer Science and Electrical programs and good placement record with IT companies. Popular among students from HP, J&K and Punjab."),

    ("Graphic Era University",
     "Graphic Era", "Dehradun", "Uttarakhand", "Deemed", "A+",
     None, 98, None, 52, "1460/2000",
     "₹7.20L", 7.20, "₹32 LPA", "₹6.0 LPA",
     "JEE Main / GEU Entrance", "linear-gradient(135deg,#6a1a3a,#aa2d5a)", 1,
     1993, 15000, 74, "https://www.geu.ac.in",
     "Graphic Era University Dehradun is one of Uttarakhand's top private deemed universities. Located in the scenic Doon Valley, it offers engineering, management and science programs with strong placement support. Popular with students from UP, Delhi, Punjab and HP."),

    ("Uttarakhand Technical University",
     "UTU", "Dehradun", "Uttarakhand", "Government", "A",
     None, 99, None, 60, "1400/2000",
     "₹1.30L", 1.30, "₹20 LPA", "₹4.2 LPA",
     "JEE Main / UKSEE", "linear-gradient(135deg,#1a6a4a,#2daa7a)", 1,
     2005, 8000, 65, "https://www.uktech.ac.in",
     "Uttarakhand Technical University is the state technical university affiliating engineering colleges across Uttarakhand. It offers B.Tech programs in Dehradun and through affiliated colleges in Haridwar, Roorkee and other cities across the state."),

    # ════════════════════════════════════════════════════════════════════════
    # STATE 15 — GOA & MAHARASHTRA (additional)
    # ════════════════════════════════════════════════════════════════════════

    ("National Institute of Technology Goa",
     "NIT Goa", "Farmagudi, Goa", "Goa", "Government", "A",
     None, 100, None, 55, "1440/2000",
     "₹5.10L", 5.10, "₹35 LPA", "₹7.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a5a6a,#2d8aaa)", 1,
     2010, 2500, 76, "https://www.nitgoa.ac.in",
     "NIT Goa is one of the newer NITs located in India's smallest state. Despite being new, it has quickly developed strong academic programs in CSE, ECE and Mechanical Engineering. Benefits from Goa's growing IT and tourism industry ecosystem."),

    ("Goa College of Engineering",
     "GCE Goa", "Farmagudi, Ponda", "Goa", "Government", "A+",
     None, 101, None, 50, "1460/2000",
     "₹0.70L", 0.70, "₹28 LPA", "₹5.8 LPA",
     "JEE Main / GCET", "linear-gradient(135deg,#1a6a1a,#2daa2d)", 1,
     1965, 3000, 75, "https://www.gec.ac.in",
     "Goa College of Engineering is Goa's premier government engineering college. Known for its extremely affordable fees and high-quality education, it attracts students from across Goa and neighboring Karnataka and Maharashtra for its CSE and Civil Engineering programs."),

    ("Visvesvaraya National Institute of Technology",
     "VNIT Nagpur", "Nagpur", "Maharashtra", "Government", "A+",
     22, 102, None, 25, "1670/2000",
     "₹5.40L", 5.40, "₹50 LPA", "₹9.8 LPA",
     "JEE Main", "linear-gradient(135deg,#6a1a1a,#aa2d2d)", 1,
     1960, 5800, 83, "https://vnit.ac.in",
     "VNIT Nagpur is one of Maharashtra's top NITs, located in the Orange City of Nagpur. Known for its strong Mechanical, Civil and Computer Science programs. Excellent placement record with IT and core engineering companies, especially from central India."),

    ("College of Engineering Pune",
     "COEP", "Shivajinagar, Pune", "Maharashtra", "Government", "A+",
     None, 103, None, 32, "1600/2000",
     "₹1.80L", 1.80, "₹45 LPA", "₹8.5 LPA",
     "JEE Main / MHT CET", "linear-gradient(135deg,#4a1a5a,#7a2d9a)", 1,
     1854, 5000, 82, "https://www.coep.org.in",
     "College of Engineering Pune (COEP) is one of the oldest engineering colleges in Asia, established in 1854. A premier government autonomous institute, it offers excellent programs in Mechanical, Civil, Electrical and Computer Engineering at highly affordable fees."),

    # ── MORE MAHARASHTRA COLLEGES ─────────────────────────────────────────────
    ("Visvesvaraya National Institute of Technology",
     "VNIT Nagpur", "Nagpur", "Maharashtra", "Government", "A+",
     41, 42, None, 15, "1580/2000",
     "₹8.20L", 8.20, "₹42 LPA", "₹12.5 LPA",
     "JEE Main", "linear-gradient(135deg,#2a4a1a,#4a8a2d)", 1,
     1960, 4500, 85, "https://www.vnit.ac.in",
     "VNIT Nagpur is a premier engineering institute offering undergraduate and postgraduate programs in various engineering disciplines. Known for its strong industry connections and research facilities."),

    ("Sardar Patel College of Engineering",
     "SPCE Mumbai", "Andheri, Mumbai", "Maharashtra", "Government", "A",
     None, 85, None, None, "1450/2000",
     "₹8.15L", 8.15, "₹38 LPA", "₹10.2 LPA",
     "JEE Main / MHT CET", "linear-gradient(135deg,#1a2a4a,#2d4a8a)", 1,
     1962, 3200, 78, "https://www.spce.ac.in",
     "SPCE Mumbai is a government-aided engineering college offering quality education in various engineering branches with good placement records."),

    ("Dr. Babasaheb Ambedkar Technological University",
     "DBATU Lonere", "Lonere, Raigad", "Maharashtra", "Government", "A",
     None, 95, None, None, "1420/2000",
     "₹8.25L", 8.25, "₹35 LPA", "₹9.8 LPA",
     "JEE Main / MHT CET", "linear-gradient(135deg,#4a2a1a,#8a4a2d)", 1,
     1989, 2800, 75, "https://dbatu.ac.in",
     "DBATU is a prominent technical university in Maharashtra offering engineering programs with focus on innovation and entrepreneurship."),

    ("Veermata Jijabai Technological Institute",
     "VJTI Mumbai", "Matunga, Mumbai", "Maharashtra", "Government", "A+",
     None, 78, None, 28, "1480/2000",
     "₹8.10L", 8.10, "₹40 LPA", "₹11.5 LPA",
     "JEE Main / MHT CET", "linear-gradient(135deg,#1a4a4a,#2d8a8a)", 1,
     1887, 3800, 80, "https://www.vjti.ac.in",
     "VJTI Mumbai is one of the oldest engineering colleges in Asia, known for its strong foundation in technical education and research."),

    # ── MORE TAMIL NADU COLLEGES ─────────────────────────────────────────────
    ("National Institute of Technology Tiruchirappalli",
     "NIT Trichy", "Tiruchirappalli", "Tamil Nadu", "Government", "A+",
     8, 8, None, 10, "1820/2000",
     "₹7.60L", 7.60, "₹1.60 CR", "₹14.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a5a30,#2d9a55)", 1,
     1964, 5200, 88, "https://www.nitt.edu",
     "NIT Trichy is a premier engineering institute known for its academic excellence, research output, and strong industry partnerships."),

    ("Anna University",
     "Anna University", "Chennai", "Tamil Nadu", "Government", "A+",
     14, 12, None, 8, "1780/2000",
     "₹7.55L", 7.55, "₹48 LPA", "₹13.2 LPA",
     "TNEA / JEE Main", "linear-gradient(135deg,#5a1a2a,#9a2d4a)", 1,
     1978, 35000, 82, "https://www.annauniv.edu",
     "Anna University is a premier technical university in Tamil Nadu offering a wide range of engineering and technology programs."),

    ("PSG College of Technology",
     "PSG Tech", "Coimbatore", "Tamil Nadu", "Government", "A+",
     23, 18, None, 12, "1720/2000",
     "₹7.50L", 7.50, "₹52 LPA", "₹12.8 LPA",
     "TNEA", "linear-gradient(135deg,#2a1a5a,#4a2d9a)", 1,
     1951, 8500, 85, "https://www.psgtech.edu",
     "PSG College of Technology is a government-aided autonomous institution known for its excellence in engineering education and research."),

    ("Thiagarajar College of Engineering",
     "TCE Madurai", "Madurai", "Tamil Nadu", "Government", "A+",
     None, 35, None, 18, "1650/2000",
     "₹7.65L", 7.65, "₹45 LPA", "₹11.8 LPA",
     "TNEA", "linear-gradient(135deg,#5a4a1a,#9a8a2d)", 1,
     1957, 4200, 83, "https://www.tce.edu",
     "TCE Madurai is a premier engineering college in Tamil Nadu known for its academic rigor and strong industry connections."),

    # ── MORE UTTAR PRADESH COLLEGES ──────────────────────────────────────────
    ("Indian Institute of Technology BHU",
     "IIT BHU", "Varanasi", "Uttar Pradesh", "Government", "A++",
     6, 6, 70, 5, "1880/2000",
     "₹5.90L", 5.90, "₹1.25 CR", "₹18.2 LPA",
     "JEE Advanced", "linear-gradient(135deg,#4a1a1a,#8a2d2d)", 1,
     1919, 6800, 90, "https://www.iitbhu.ac.in",
     "IIT BHU is one of the oldest engineering institutes in India, located in the historic city of Varanasi. Known for its strong research culture and diverse academic programs."),

    ("Motilal Nehru National Institute of Technology",
     "MNNIT Allahabad", "Allahabad", "Uttar Pradesh", "Government", "A+",
     42, 38, None, 16, "1560/2000",
     "₹5.85L", 5.85, "₹38 LPA", "₹11.2 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a5a,#2d8a9a)", 1,
     1961, 4800, 84, "https://www.mnnit.ac.in",
     "MNNIT Allahabad is a leading technical institute offering undergraduate and postgraduate programs in various engineering disciplines."),

    ("Dr. A.P.J. Abdul Kalam Technical University",
     "AKTU Lucknow", "Lucknow", "Uttar Pradesh", "Government", "A+",
     None, 45, None, 20, "1520/2000",
     "₹5.95L", 5.95, "₹42 LPA", "₹10.8 LPA",
     "UPSEE / JEE Main", "linear-gradient(135deg,#5a1a4a,#9a2d8a)", 1,
     2000, 15000, 78, "https://aktu.ac.in",
     "AKTU is a prominent technical university in Uttar Pradesh offering engineering programs through its affiliated colleges and institutes."),

    ("Harcourt Butler Technical University",
     "HBTU Kanpur", "Kanpur", "Uttar Pradesh", "Government", "A",
     None, 52, None, 25, "1480/2000",
     "₹5.80L", 5.80, "₹35 LPA", "₹9.5 LPA",
     "UPSEE / JEE Main", "linear-gradient(135deg,#2a5a1a,#4a9a2d)", 1,
     1921, 5500, 76, "https://hbtu.ac.in",
     "HBTU Kanpur is one of the oldest engineering colleges in India, known for its strong foundation in technical education."),

    # ── MORE KARNATAKA COLLEGES ──────────────────────────────────────────────
    ("National Institute of Technology Karnataka",
     "NITK Surathkal", "Surathkal, Mangalore", "Karnataka", "Government", "A+",
     12, 15, None, 9, "1750/2000",
     "₹5.40L", 5.40, "₹55 LPA", "₹15.8 LPA",
     "JEE Main", "linear-gradient(135deg,#1a5a2a,#2d9a4a)", 1,
     1960, 5800, 87, "https://www.nitk.ac.in",
     "NITK Surathkal is a premier engineering institute located on the picturesque coast of Karnataka, known for its excellent academic environment and research facilities."),

    ("Manipal Institute of Technology",
     "MIT Manipal", "Manipal", "Karnataka", "Private", "A+",
     45, 28, 180, 22, "1520/2000",
     "₹15.80L", 15.80, "₹1.20 CR", "₹19.2 LPA",
     "MET / JEE Main", "linear-gradient(135deg,#5a2a1a,#9a4a2d)", 1,
     1957, 4200, 85, "https://www.manipal.edu/mit",
     "MIT Manipal is a leading private engineering institute offering world-class education with excellent infrastructure and global exposure."),

    ("R.V. College of Engineering",
     "RVCE Bangalore", "Bangalore", "Karnataka", "Private", "A++",
     58, 32, None, 14, "1480/2000",
     "₹8.50L", 8.50, "₹52 LPA", "₹12.5 LPA",
     "CET / COMEDK", "linear-gradient(135deg,#1a2a5a,#2d4a9a)", 1,
     1963, 6800, 82, "https://www.rvce.edu.in",
     "RVCE Bangalore is a premier engineering college known for its academic excellence and strong industry partnerships."),

    ("BMS College of Engineering",
     "BMSCE Bangalore", "Basavanagudi, Bangalore", "Karnataka", "Private", "A+",
     62, 36, None, 17, "1450/2000",
     "₹5.35L", 5.35, "₹48 LPA", "₹11.8 LPA",
     "CET / COMEDK", "linear-gradient(135deg,#5a1a5a,#9a2d9a)", 1,
     1946, 5200, 80, "https://www.bmsce.ac.in",
     "BMSCE Bangalore is one of the oldest engineering colleges in Karnataka, known for its strong academic foundation and research contributions."),

    # ── MORE DELHI NCR COLLEGES ─────────────────────────────────────────────
    ("Netaji Subhas University of Technology",
     "NSUT Delhi", "Dwarka, New Delhi", "Delhi", "Government", "A+",
     None, 48, None, 21, "1500/2000",
     "₹6.80L", 6.80, "₹45 LPA", "₹13.2 LPA",
     "JEE Main", "linear-gradient(135deg,#4a4a1a,#8a8a2d)", 1,
     2018, 3800, 78, "https://www.nsut.ac.in",
     "NSUT Delhi is a state university offering quality engineering education with modern facilities and strong industry connections."),

    ("Delhi Technological University",
     "DTU Delhi", "Rohini, New Delhi", "Delhi", "Government", "A+",
     29, 25, None, 11, "1680/2000",
     "₹7.20L", 7.20, "₹1.20 CR", "₹16.5 LPA",
     "JEE Main", "linear-gradient(135deg,#1a4a4a,#2d8a8a)", 1,
     1941, 9200, 86, "https://www.dtu.ac.in",
     "DTU Delhi (formerly Delhi College of Engineering) is a premier engineering university known for its academic excellence and research output."),

    ("Indraprastha Institute of Information Technology",
     "IIIT Delhi", "Okhla, New Delhi", "Delhi", "Government", "A+",
     None, 55, 200, 30, "1420/2000",
     "₹8.50L", 8.50, "₹1.80 CR", "₹18.8 LPA",
     "JEE Main", "linear-gradient(135deg,#2a2a5a,#4a4a9a)", 1,
     2008, 2200, 88, "https://www.iiitd.ac.in",
     "IIIT Delhi is a research-oriented university focusing on information technology and interdisciplinary research programs."),

    ("Jamia Millia Islamia",
     "JMI Delhi", "Jamia Nagar, New Delhi", "Delhi", "Government", "A+",
     None, 65, None, 35, "1380/2000",
     "₹5.20L", 5.20, "₹38 LPA", "₹9.8 LPA",
     "JEE Main / JMI Entrance", "linear-gradient(135deg,#5a1a1a,#9a2d2d)", 1,
     1920, 18000, 75, "https://www.jmi.ac.in",
     "JMI Delhi is a central university offering engineering and technology programs with a focus on inclusive education."),

    # ── GREATER NOIDA COLLEGES (as requested) ───────────────────────────────
    ("Galgotias University",
     "Galgotias", "Greater Noida", "Uttar Pradesh", "Private", "A+",
     None, 72, None, 40, "1350/2000",
     "₹6.50L", 6.50, "₹42 LPA", "₹8.5 LPA",
     "CUET / JEE Main", "linear-gradient(135deg,#1a5a5a,#2d9a9a)", 1,
     2011, 8500, 78, "https://www.galgotiasuniversity.edu.in",
     "Galgotias University is a leading private university in Greater Noida offering comprehensive engineering and technology programs."),

    ("Noida Institute of Engineering and Technology",
     "NIET Greater Noida", "Greater Noida", "Uttar Pradesh", "Private", "A",
     None, 88, None, 55, "1280/2000",
     "₹5.80L", 5.80, "₹35 LPA", "₹7.2 LPA",
     "UPSEE / JEE Main", "linear-gradient(135deg,#5a5a1a,#9a9a2d)", 1,
     2001, 4200, 72, "https://www.niet.co.in",
     "NIET Greater Noida is a prominent engineering college known for its industry-oriented education and strong placement support."),

    ("Gautam Buddha University",
     "GBU Greater Noida", "Greater Noida", "Uttar Pradesh", "Government", "A",
     None, 95, None, 60, "1250/2000",
     "₹4.50L", 4.50, "₹28 LPA", "₹6.8 LPA",
     "GBTU Entrance", "linear-gradient(135deg,#2a5a2a,#4a9a4a)", 1,
     2008, 3200, 68, "https://www.gbu.ac.in",
     "GBU is a government university in Greater Noida offering engineering programs with focus on innovation and research."),

]
    conn.commit()
    print(f"✅ Inserted {len(COLLEGES)} colleges into the database.")


# ── 4. RUN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    seed(conn)
    conn.close()
    print("\n🎉 Done! Your colleges.db is ready.")
    print(f"   Location: {DB_PATH}")
    print("   Now run: python app.py")
