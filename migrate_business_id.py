import sqlite3

DB_PATH = "chatbot.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = [
    "customers",
    "messages",
    "memories",
    "issues",
    "leads",
    "meetings",
]

for table in tables:
    columns = [
        row[1]
        for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()
    ]

    if "business_id" not in columns:
        cursor.execute(
            f"ALTER TABLE {table} "
            "ADD COLUMN business_id INTEGER"
        )
        print(f"Added business_id to {table}")
    else:
        print(f"business_id already exists in {table}")

conn.commit()
conn.close()

print("Migration completed successfully.")