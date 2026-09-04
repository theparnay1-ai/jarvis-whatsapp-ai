import sqlite3

DB_PATH = "chatbot.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Starting customer table migration...")

# 1. Create the new customers table
cursor.execute("""
CREATE TABLE customers_new (
    id INTEGER PRIMARY KEY,
    sender VARCHAR,
    name VARCHAR,
    email VARCHAR,
    created_at DATETIME,
    last_interaction DATETIME,
    business_id INTEGER,
    CONSTRAINT uq_customer_business_sender
        UNIQUE (business_id, sender)
)
""")

# 2. Copy existing customer data
cursor.execute("""
INSERT INTO customers_new (
    id,
    sender,
    name,
    email,
    created_at,
    last_interaction,
    business_id
)
SELECT
    id,
    sender,
    name,
    email,
    created_at,
    last_interaction,
    business_id
FROM customers
""")

# 3. Remove old table
cursor.execute("DROP TABLE customers")

# 4. Rename new table
cursor.execute("""
ALTER TABLE customers_new
RENAME TO customers
""")

# 5. Recreate indexes
cursor.execute("""
CREATE INDEX ix_customers_sender
ON customers (sender)
""")

cursor.execute("""
CREATE INDEX ix_customers_id
ON customers (id)
""")

conn.commit()

print("Customer table migration completed successfully.")

# Verification
print("\nVerification:")
print("Columns:")
print(cursor.execute("PRAGMA table_info(customers)").fetchall())

print("\nIndexes:")
print(cursor.execute("PRAGMA index_list(customers)").fetchall())

conn.close()