import sqlite3


conn = sqlite3.connect("emails.db")

cursor = conn.cursor()


columns = [

    ("username", "VARCHAR"),
    ("avatar", "VARCHAR"),
    ("phone", "VARCHAR"),
    ("country", "VARCHAR"),
    ("city", "VARCHAR"),
    ("timezone", "VARCHAR"),
    ("preferred_language", "VARCHAR"),
    ("preferred_tone", "VARCHAR"),
    ("preferred_length", "VARCHAR"),
    ("created_at", "DATETIME"),
    ("updated_at", "DATETIME"),
    ("last_login", "DATETIME"),

]


for name, dtype in columns:

    try:

        cursor.execute(
            f"ALTER TABLE users ADD COLUMN {name} {dtype}"
        )

        print(
            f"Added {name}"
        )


    except Exception:

        print(
            f"{name} already exists"
        )



conn.commit()

conn.close()


print("Migration finished")