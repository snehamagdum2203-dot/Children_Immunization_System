import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# optional: old data delete (clean start)
cursor.execute("DELETE FROM vaccines")

# full vaccine list
cursor.executemany("""
INSERT INTO vaccines (vaccine_name, age_due) VALUES (?, ?)
""", [

# AT BIRTH
("BCG", "At Birth"),
("OPV-0", "At Birth"),
("Hepatitis B-1", "At Birth"),

# 6 WEEKS
("DTwP-1", "6 Weeks"),
("IPV-1", "6 Weeks"),
("Hib-1", "6 Weeks"),
("Rotavirus-1", "6 Weeks"),
("PCV-1", "6 Weeks"),
("OPV-1", "6 Weeks"),

# 10 WEEKS
("DTwP-2", "10 Weeks"),
("IPV-2", "10 Weeks"),
("Hib-2", "10 Weeks"),
("Rotavirus-2", "10 Weeks"),
("PCV-2", "10 Weeks"),
("OPV-2", "10 Weeks"),

# 14 WEEKS
("DTwP-3", "14 Weeks"),
("IPV-3", "14 Weeks"),
("Hib-3", "14 Weeks"),
("Rotavirus-3", "14 Weeks"),
("PCV-3", "14 Weeks"),
("OPV-3", "14 Weeks"),

# 6 MONTHS
("Hepatitis B-3", "6 Months"),

# 9 MONTHS
("MMR-1", "9 Months"),
("Measles-Rubella", "9 Months"),
("Typhoid Conjugate", "9 Months"),

# 12 MONTHS
("Hepatitis A-1", "12 Months"),

# 15 MONTHS
("MMR-2", "15 Months"),
("Varicella-1", "15 Months"),
("PCV Booster", "15 Months"),

# 16-18 MONTHS
("DTwP Booster-1", "16-18 Months"),
("IPV Booster", "16-18 Months"),
("Hib Booster", "16-18 Months"),

# 2 YEARS
("Typhoid Booster", "2 Years"),

# 4-6 YEARS
("DTwP Booster-2", "4-6 Years"),
("OPV Booster", "4-6 Years"),
("Varicella-2", "4-6 Years"),

# 10 YEARS
("Tdap", "10 Years"),

# 16 YEARS
("Td Booster", "16 Years")

])

conn.commit()
conn.close()

print("Full vaccine list inserted!")