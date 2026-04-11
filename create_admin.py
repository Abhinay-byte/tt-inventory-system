from database import get_connection
import hashlib

conn = get_connection()
cursor = conn.cursor()

username = "admin"
password = "admin123"

cursor.execute("""
INSERT INTO admin_users (username, password_hash, created_at)
VALUES (?, ?, datetime('now'))
""", (username, hashlib.sha256(password.encode()).hexdigest()))

conn.commit()
print("Admin created")