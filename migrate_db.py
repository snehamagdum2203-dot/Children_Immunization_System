"""
Run this ONCE to update your existing database.db with new columns.
Place this file next to your database.db and run: python migrate_db.py
"""
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Add 'aefi' column to vaccines_master if not exists
try:
    c.execute("ALTER TABLE vaccines_master ADD COLUMN aefi TEXT")
    print("Added 'aefi' column to vaccines_master")
except Exception as e:
    print(f"aefi column: {e}")

# Add 'care' column to vaccines_master if not exists
try:
    c.execute("ALTER TABLE vaccines_master ADD COLUMN care TEXT")
    print("Added 'care' column to vaccines_master")
except Exception as e:
    print(f"care column: {e}")

# Add 'age_due' column to vaccines if not exists
try:
    c.execute("ALTER TABLE vaccines ADD COLUMN age_due TEXT")
    print("Added 'age_due' column to vaccines")
except Exception as e:
    print(f"age_due column: {e}")

# Add child_id column to vaccination_records if not exists (it should already be there)
# Populate vaccines_master with all 36 vaccines including AEFI and care
vaccines_data = [
    ("BCG", "At birth", "Government",
     "Prevents Tuberculosis (TB) - especially TB meningitis and miliary TB in children",
     "Mild fever, small red lump at injection site (normal), local abscess (rare)",
     "Keep injection site clean and dry. Do not apply any cream. Lump will heal on its own in 2-3 months."),

    ("OPV-0", "At birth", "Government",
     "Oral Polio Vaccine - prevents Poliomyelitis (Polio)",
     "Extremely rare - vaccine-associated paralytic polio (VAPP) in very rare cases",
     "No special care needed. Baby can eat/drink normally after 30 minutes."),

    ("Hepatitis B-1", "At birth", "Government",
     "Prevents Hepatitis B liver infection and liver cancer",
     "Mild soreness at injection site, low-grade fever",
     "Apply cold compress if site is sore. Monitor for fever - give paracetamol if advised by doctor."),

    ("DTwP-1", "6 weeks", "Government",
     "Prevents Diphtheria, Tetanus (lockjaw), and Whooping Cough (Pertussis)",
     "Fever (very common), pain/swelling/redness at site, irritability, rarely febrile seizures",
     "Give paracetamol as prescribed for fever. Cold compress on injection site. Extra fluids. Comfort baby."),

    ("IPV-1", "6 weeks", "Government",
     "Inactivated Polio Vaccine - prevents all 3 types of Poliovirus",
     "Mild soreness at injection site, low-grade fever",
     "Cold compress on site. Paracetamol for fever if needed."),

    ("Hib-1", "6 weeks", "Government",
     "Prevents Haemophilus influenzae type b - meningitis, pneumonia, epiglottitis",
     "Mild fever, redness/swelling at site",
     "Paracetamol for fever. Cold compress on site."),

    ("Rotavirus-1", "6 weeks", "Government",
     "Prevents Rotavirus diarrhoea - leading cause of severe diarrhoea in children under 5",
     "Mild irritability, temporary diarrhoea, vomiting",
     "Ensure adequate hydration (ORS if diarrhoea). No special restriction needed."),

    ("PCV-1", "6 weeks", "Government",
     "Pneumococcal Conjugate Vaccine - prevents pneumonia, meningitis, ear infections",
     "Fever, injection site pain/swelling, irritability, decreased appetite",
     "Paracetamol for fever. Cold compress. Extra breastfeeding/fluids."),

    ("OPV-1", "6 weeks", "Government",
     "Oral Polio Vaccine - 2nd dose, boosts immunity against Polio",
     "Very rarely loose stools",
     "No special care needed."),

    ("DTwP-2", "10 weeks", "Government",
     "2nd dose - Diphtheria, Tetanus, Pertussis protection",
     "Fever, site soreness, crying, irritability",
     "Paracetamol for fever. Cold compress. Comfort baby."),

    ("IPV-2", "10 weeks", "Government",
     "2nd dose Inactivated Polio Vaccine",
     "Mild site reaction, low fever",
     "Cold compress on site."),

    ("Hib-2", "10 weeks", "Government",
     "2nd dose - Haemophilus influenzae b protection",
     "Mild fever, site reaction",
     "Paracetamol if fever. Cold compress."),

    ("Rotavirus-2", "10 weeks", "Government",
     "2nd dose Rotavirus - enhanced diarrhoea protection",
     "Mild diarrhoea, vomiting, irritability",
     "ORS if diarrhoea. Keep hydrated."),

    ("PCV-2", "10 weeks", "Government",
     "2nd dose Pneumococcal vaccine",
     "Fever, site swelling, irritability",
     "Paracetamol for fever. Extra fluids."),

    ("OPV-2", "10 weeks", "Government",
     "3rd dose Oral Polio Vaccine",
     "Rarely loose stools",
     "No special care needed."),

    ("DTwP-3", "14 weeks", "Government",
     "3rd dose - Diphtheria, Tetanus, Pertussis - completes primary series",
     "Fever, site pain, irritability, hard lump at site (can last weeks)",
     "Do not massage the lump - it will absorb on its own. Paracetamol for fever."),

    ("IPV-3", "14 weeks", "Government",
     "3rd dose Inactivated Polio - completes primary series",
     "Mild site reaction",
     "Cold compress if needed."),

    ("Hib-3", "14 weeks", "Government",
     "3rd dose Hib - completes primary series",
     "Mild fever, site reaction",
     "Paracetamol if fever."),

    ("Rotavirus-3", "14 weeks", "Government",
     "3rd dose Rotavirus - completes primary series",
     "Mild loose stools, irritability",
     "ORS if needed. Keep hydrated."),

    ("PCV-3", "14 weeks", "Government",
     "3rd dose PCV - completes primary series",
     "Fever, site swelling, irritability",
     "Paracetamol and cold compress."),

    ("OPV-3", "14 weeks", "Government",
     "4th dose Oral Polio - completes primary OPV series",
     "Very rarely loose stools",
     "No special care needed."),

    ("Hepatitis B-3", "6 months", "Government",
     "3rd dose Hepatitis B - completes primary series, provides long-term protection",
     "Mild site soreness, low fever",
     "Cold compress on site. Paracetamol if fever."),

    ("MMR-1", "9 months", "Government",
     "Measles, Mumps, Rubella vaccine - prevents all three viral infections",
     "Fever 7-12 days after vaccination (very common), mild rash, swollen glands",
     "Paracetamol for fever after 7 days. Fever appearing immediately is unrelated to MMR. Rash is harmless."),

    ("Typhoid", "9 months", "Government",
     "Prevents Typhoid fever caused by Salmonella Typhi",
     "Fever, headache, site pain, nausea",
     "Paracetamol for fever. Rest. Adequate fluids."),

    ("Hepatitis A-1", "12 months", "Private",
     "Prevents Hepatitis A liver infection spread through contaminated food/water",
     "Site pain, mild fever, fatigue",
     "Rest after vaccination. Cold compress on site."),

    ("MMR-2", "15 months", "Government",
     "2nd dose MMR - booster for lifelong protection against Measles, Mumps, Rubella",
     "Fever, mild rash, joint pain (especially in older children)",
     "Paracetamol for fever. Rash is not contagious."),

    ("Varicella-1", "15 months", "Private",
     "Prevents Chickenpox (Varicella) - highly contagious viral infection",
     "Mild fever, small chickenpox-like rash at 1-4 weeks (rare), site soreness",
     "Keep rash area clean. Do not scratch. Paracetamol for fever (NOT aspirin)."),

    ("PCV Booster", "15 months", "Government",
     "Pneumococcal booster - sustained protection against pneumonia and meningitis",
     "Fever, site swelling, irritability",
     "Paracetamol and cold compress."),

    ("DTwP Booster-1", "18 months", "Government",
     "DTP booster - reinforces protection against Diphtheria, Tetanus, Pertussis",
     "Fever, site redness/swelling, hard lump, irritability",
     "Lump is normal - do not massage. Paracetamol for fever. Cold compress on site."),

    ("IPV Booster", "18 months", "Government",
     "Polio booster - ensures complete and lasting protection against Polio",
     "Mild site reaction, low fever",
     "Cold compress. Paracetamol if needed."),
]

for vname, age_due, availability, purpose, aefi, care in vaccines_data:
    # Update vaccines_master
    c.execute("""
        UPDATE vaccines_master SET aefi=?, care=?, purpose=?, availability=?
        WHERE name=?
    """, (aefi, care, purpose, availability, vname))
    if c.rowcount == 0:
        c.execute("""
            INSERT INTO vaccines_master (name, age_due, availability, purpose, aefi, care)
            VALUES (?,?,?,?,?,?)
        """, (vname, age_due, availability, purpose, aefi, care))

    # Update vaccines table age_due
    c.execute("UPDATE vaccines SET age_due=? WHERE vaccine_name=?", (age_due, vname))
    if c.rowcount == 0:
        c.execute("INSERT OR IGNORE INTO vaccines (vaccine_name, age_due) VALUES (?,?)", (vname, age_due))

conn.commit()
conn.close()
print("\n✅ Migration complete! vaccines_master updated with AEFI and Care info for all 30 vaccines.")
