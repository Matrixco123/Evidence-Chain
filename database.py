import sqlite3

def init_db():
    conn = sqlite3.connect("evidence.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        sha256 TEXT,
        signature TEXT,
        filepath TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Add filepath column to existing tables that lack it
    try:
        cursor.execute("ALTER TABLE evidence ADD COLUMN filepath TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists

    conn.commit()
    conn.close()


def insert_record(filename, sha256, signature="", filepath=""):
    conn = sqlite3.connect("evidence.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO evidence (filename, sha256, signature, filepath)
    VALUES (?, ?, ?, ?)
    """, (filename, sha256, signature, filepath))

    record_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return record_id
    
def get_record_by_hash(hash_val):
    conn = sqlite3.connect("evidence.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM evidence WHERE sha256 = ?
    """, (hash_val,))

    result = cursor.fetchone()
    conn.close()

    return result

def get_record_by_id(evidence_id):
    conn = sqlite3.connect("evidence.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
    result = cursor.fetchone()

    conn.close()
    return result

def update_filepath(evidence_id, filepath):
    conn = sqlite3.connect("evidence.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE evidence SET filepath = ? WHERE id = ?", (filepath, evidence_id))
    conn.commit()
    conn.close()