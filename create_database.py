import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ----------- PHC TABLE -----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS phc(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    password TEXT
)
""")

# ----------- STAFF TABLE -----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS staff(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phc_name TEXT,
    subcenter_name TEXT,
    mobile TEXT,
    password TEXT
)
""")

# ----------- CHILDREN TABLE -----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS children(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id TEXT,
    name TEXT,
    dob TEXT,
    parent_name TEXT,
    parent_mobile TEXT,
    address TEXT,
    subcenter TEXT,
    created_date TEXT
)
""")

# ----------- VACCINATION SCHEDULE -----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS vaccination_schedule(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER,
    vaccine_name TEXT,
    due_date TEXT,
    status TEXT,
    vacc_date TEXT
)
""")

# ----------- VACCINATION RECORDS -----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS vaccination_records(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER,
    vaccine_name TEXT,
    vacc_date TEXT,
    given_by TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vaccines_master(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    purpose TEXT,
    side_effects TEXT,
    care TEXT,
    availability TEXT
)
""")

cursor.executemany("""
INSERT INTO vaccines_master (name, purpose, side_effects, care, availability)
VALUES (?, ?, ?, ?, ?)
""", [
('BCG','TB Protection','Swelling, mild fever','No treatment needed','Government'),
('Hep-B0','Liver Protection','Mild fever','Rest','Government + Private'),
('OPV-0','Polio Prevention','Rare fever','Fluids','Government'),
('Vitamin K','Bleeding Prevention','Injection pain','Normal care','Government + Private'),
('Hep-B1','Liver Protection','Mild fever','Rest','Government + Private'),
('OPV-1','Polio Prevention','Rare fever','Fluids','Government'),

('DPT-1','3 Disease Protection','Fever, swelling','Cold compress','Government'),
('IPV-1','Polio Injection','Pain','Rest','Government'),
('Hib-1','Brain Infection Protection','Mild fever','Fluids','Government + Private'),
('Rotavirus-1','Diarrhea Prevention','Loose motion','ORS','Private / Govt'),
('PCV-1','Pneumonia Protection','Fever','Rest','Private / Govt'),
('Hep-B2','Liver Protection','Mild fever','Rest','Government'),

('DPT-2','3 Disease Protection','Fever','Paracetamol','Government'),
('IPV-2','Polio Injection','Pain','Rest','Government'),
('Hib-2','Infection Protection','Fever','Fluids','Government'),
('Rotavirus-2','Diarrhea Prevention','Mild upset','ORS','Private'),
('PCV-2','Pneumonia','Fever','Rest','Private'),
('Hep-B3','Liver Protection','Mild fever','Rest','Government'),

('DPT-3','Full Protection','Fever','Rest','Government'),
('IPV-3','Polio','Pain','Fluids','Government'),
('Hib-3','Meningitis Protection','Fever','Care','Government'),
('Rotavirus-3','Diarrhea','Mild symptoms','ORS','Private'),
('PCV-3','Pneumonia','Fever','Rest','Private'),
('Influenza-1','Flu Protection','Fever, body pain','Fluids','Private'),

('MMR-1','Measles Protection','Fever, rash','Rest','Government'),
('JE-1','Brain Infection','Mild fever','Care','Government'),
('Typhoid','Typhoid Protection','Headache, fever','Fluids','Private'),
('Hep-A-1','Liver Protection','Mild fever','Rest','Private'),
('PCV Booster','Pneumonia','Mild fever','Care','Private'),
('Varicella','Chickenpox','Rash, fever','Isolation','Private'),

('DPT Booster','Immunity Boost','Fever','Paracetamol','Government'),
('OPV Booster','Polio Booster','None','Fluids','Government'),
('MMR-2','Immunity Boost','Mild fever','Rest','Government'),
('Hep-A-2','Liver Protection','Mild fever','Care','Private'),
('Typhoid Booster','Protection','Headache','Rest','Private'),
('Influenza Booster','Flu','Fever','Fluids','Private')
])

conn.commit()
conn.close()

print("Database created successfully")

