from essl import get_connection

with open("essl_dummy_devices.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# Split SQL Server batches by GO
batches = [b.strip() for b in sql.split("\nGO") if b.strip()]

with get_connection() as conn:
    cursor = conn.cursor()

    for i, batch in enumerate(batches, 1):
        print(f"Executing batch {i}/{len(batches)}...")
        cursor.execute(batch)

print("SQL script executed successfully.")