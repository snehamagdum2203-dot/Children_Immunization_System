import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'children_immunization_secret_2024')

# Twilio credentials
TWILIO_SID   = "AC5cc9c31aa89c01c7d7667b08109bc88c"
TWILIO_TOKEN = "7296c30f58bf3280849735a7a4b89148"
TWILIO_FROM  = "whatsapp:+14155238886"

# ---------------- DB HELPER ----------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- TWILIO ----------------
def send_whatsapp(number, message):
    try:
        number = str(number).strip().replace(" ", "")
        if number.startswith("+"):
            number = number[1:]
        if not number.startswith("91") and len(number) == 10:
            number = "91" + number
        to_number = "whatsapp:+" + number
        from twilio.rest import Client
        Client(TWILIO_SID, TWILIO_TOKEN).messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=to_number
        )
        print(f"WhatsApp sent to {to_number}")
    except Exception as e:
        print("WhatsApp Error:", e)

# ==================== HOME ====================
@app.route('/')
def home():
    return render_template('home.html')

# ==================== STAFF AUTH ====================
@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        subcenter = request.form.get('subcenter', '').strip()
        mobile    = request.form.get('mobile', '').strip()
        password  = request.form.get('password', '')

        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff WHERE subcenter_name=? AND mobile=?", (subcenter, mobile))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['staff_id']   = user['id']
            session['staff_name'] = user['name']
            session['subcenter']  = user['subcenter_name']
            session['phc_name']   = user['phc_name']
            return redirect('/staff_dashboard')
        flash('Invalid credentials. Please check your subcenter, mobile, and password.', 'error')

    return render_template('staff_login.html')


@app.route('/staff_signup', methods=['GET', 'POST'])
def staff_signup():
    if request.method == 'POST':
        name      = request.form['name'].strip()
        phc       = request.form['phc_name'].strip()
        subcenter = request.form['subcenter'].strip()
        mobile    = request.form['mobile'].strip()
        password  = generate_password_hash(request.form['password'])

        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO staff (name, phc_name, subcenter_name, mobile, password) VALUES (?,?,?,?,?)",
            (name, phc, subcenter, mobile, password)
        )
        conn.commit()
        conn.close()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('staff_login'))

    return render_template('staff_signup.html')


# ==================== STAFF DASHBOARD ====================
@app.route('/staff_dashboard')
def staff_dashboard():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    conn   = get_db()
    cursor = conn.cursor()
    subcenter = session['subcenter']

    cursor.execute("SELECT COUNT(*) FROM children WHERE subcenter=?", (subcenter,))
    total_children = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM vaccination_records vr
        JOIN children c ON c.id = vr.child_id
        WHERE c.subcenter=?
    """, (subcenter,))
    total_vaccines = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) FROM vaccination_schedule vs
        JOIN children c ON c.id = vs.child_id
        WHERE c.subcenter=? AND vs.due_date=? AND vs.status='pending'
    """, (subcenter, today))
    due_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM vaccination_schedule vs
        JOIN children c ON c.id = vs.child_id
        WHERE c.subcenter=? AND vs.due_date < ? AND vs.status='pending'
    """, (subcenter, today))
    overdue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT name, child_id, dob, created_date FROM children
        WHERE subcenter=? ORDER BY id DESC LIMIT 5
    """, (subcenter,))
    recent_children = cursor.fetchall()

    conn.close()

    return render_template('staff_dashboard.html',
        staff_name=session['staff_name'],
        subcenter=subcenter,
        total_children=total_children,
        total_vaccines=total_vaccines,
        due_today=due_today,
        overdue=overdue,
        recent_children=recent_children
    )


# ==================== CHILD REGISTER ====================
@app.route('/child_register', methods=['GET', 'POST'])
def child_register():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    if request.method == 'POST':
        child_id      = request.form['child_id'].strip()
        name          = request.form['name'].strip()
        dob           = request.form['dob']
        parent_name   = request.form['parent_name'].strip()
        parent_mobile = request.form['parent_mobile'].strip()
        address       = request.form['address'].strip()
        subcenter     = session.get('subcenter')
        created_date  = datetime.now().strftime("%Y-%m-%d")

        conn   = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM children WHERE child_id=?", (child_id,))
        if cursor.fetchone():
            conn.close()
            flash(f'Child ID "{child_id}" already exists.', 'error')
            return render_template('child_register.html')

        cursor.execute("""
            INSERT INTO children (child_id, name, dob, parent_name, parent_mobile, address, subcenter, created_date)
            VALUES (?,?,?,?,?,?,?,?)
        """, (child_id, name, dob, parent_name, parent_mobile, address, subcenter, created_date))

        child_db_id = cursor.lastrowid
        dob_dt = datetime.strptime(dob, "%Y-%m-%d")

        schedule = [
            ("BCG",          0),   ("OPV-0",       0),   ("Hepatitis B-1", 0),
            ("DTwP-1",      42),   ("IPV-1",       42),  ("Hib-1",        42),
            ("Rotavirus-1", 42),   ("PCV-1",       42),  ("OPV-1",        42),
            ("DTwP-2",      70),   ("IPV-2",       70),  ("Hib-2",        70),
            ("Rotavirus-2", 70),   ("PCV-2",       70),  ("OPV-2",        70),
            ("DTwP-3",      98),   ("IPV-3",       98),  ("Hib-3",        98),
            ("Rotavirus-3", 98),   ("PCV-3",       98),  ("OPV-3",        98),
            ("Hepatitis B-3",180), ("MMR-1",      270),  ("Typhoid",     270),
            ("Hepatitis A-1",365), ("MMR-2",      450),  ("Varicella-1", 450),
            ("PCV Booster", 450),  ("DTwP Booster-1",510),("IPV Booster",510),
        ]

        for vaccine_name, days_after_birth in schedule:
            due_date = (dob_dt + timedelta(days=days_after_birth)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO vaccination_schedule (child_id, vaccine_name, due_date, status)
                VALUES (?,?,?,'pending')
            """, (child_db_id, vaccine_name, due_date))

        conn.commit()
        conn.close()

        flash(f'Child "{name}" registered successfully with auto-generated vaccination schedule!', 'success')
        return redirect('/staff_dashboard')

    return render_template('child_register.html')


# ==================== UPDATE VACCINE ====================
# FIX: vaccine_name[] arrays handle correctly; other_vaccine is optional
@app.route('/update_vaccine', methods=['GET', 'POST'])
def update_vaccine():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT vaccine_name, age_due FROM vaccines ORDER BY vaccine_name")
    vaccines = cursor.fetchall()

    if request.method == 'POST':
        child_id_text   = request.form.get('child_id', '').strip()
        vaccine_names   = request.form.getlist('vaccine_name[]')
        other_vaccines  = request.form.getlist('other_vaccine[]')
        vacc_dates      = request.form.getlist('vacc_date[]')
        due_dates       = request.form.getlist('due_date[]')

        if not child_id_text:
            flash('Please enter Child ID.', 'error')
            conn.close()
            return render_template('update_vaccine.html', vaccines=vaccines)

        cursor.execute("SELECT id FROM children WHERE child_id=?", (child_id_text,))
        child_row = cursor.fetchone()
        if not child_row:
            flash(f'Child ID "{child_id_text}" not found.', 'error')
            conn.close()
            return render_template('update_vaccine.html', vaccines=vaccines)

        child_db_id = child_row['id']
        saved_count = 0

        for i in range(len(vacc_dates)):
            vacc_date = vacc_dates[i].strip() if i < len(vacc_dates) else ''
            if not vacc_date:
                continue

            # Use dropdown value; if empty or "Other", use text field
            v_name = vaccine_names[i].strip() if i < len(vaccine_names) else ''
            o_name = other_vaccines[i].strip() if i < len(other_vaccines) else ''
            final_vaccine = v_name if v_name else o_name

            if not final_vaccine:
                continue  # skip rows with no vaccine name

            due_date = due_dates[i].strip() if i < len(due_dates) else ''

            cursor.execute("""
                INSERT INTO vaccination_records (child_id, vaccine_name, vacc_date, given_by)
                VALUES (?,?,?,?)
            """, (child_db_id, final_vaccine, vacc_date, session.get('staff_name', '')))

            # Mark schedule as done if exists
            cursor.execute("""
                UPDATE vaccination_schedule
                SET status='done', vacc_date=?
                WHERE child_id=? AND vaccine_name=? AND status='pending'
            """, (vacc_date, child_db_id, final_vaccine))

            # If due_date provided, update or insert schedule
            if due_date:
                cursor.execute("""
                    SELECT id FROM vaccination_schedule
                    WHERE child_id=? AND vaccine_name=? AND status='pending'
                """, (child_db_id, final_vaccine))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO vaccination_schedule (child_id, vaccine_name, due_date, status)
                        VALUES (?,?,?,'pending')
                    """, (child_db_id, final_vaccine + ' (next)', due_date))

            saved_count += 1

        conn.commit()
        conn.close()

        if saved_count > 0:
            flash(f'{saved_count} vaccine record(s) saved for child {child_id_text}!', 'success')
            return redirect('/staff_dashboard')
        else:
            flash('No valid vaccine records found. Please fill vaccine name and date.', 'error')
            return render_template('update_vaccine.html', vaccines=vaccines)

    conn.close()
    return render_template('update_vaccine.html', vaccines=vaccines)


# ==================== SEARCH CHILD ====================
# FIX: Now shows complete vaccine history per child
@app.route('/search_child', methods=['GET', 'POST'])
def search_child():
    results    = []
    search_key = ''

    if request.method == 'POST':
        search_key = request.form.get('keyword', '').strip()
        conn   = get_db()
        cursor = conn.cursor()
        like   = f'%{search_key}%'

        cursor.execute("""
            SELECT c.id, c.child_id, c.name, c.parent_name, c.parent_mobile,
                   c.dob, c.address, c.subcenter
            FROM children c
            WHERE c.name LIKE ? OR c.child_id LIKE ? OR c.parent_mobile LIKE ?
        """, (like, like, like))
        children = cursor.fetchall()

        for child in children:
            cursor.execute("""
                SELECT vaccine_name, vacc_date FROM vaccination_records
                WHERE child_id=? ORDER BY vacc_date DESC
            """, (child['id'],))
            vaccinations = cursor.fetchall()

            cursor.execute("""
                SELECT vaccine_name, due_date FROM vaccination_schedule
                WHERE child_id=? AND status='pending' ORDER BY due_date ASC LIMIT 5
            """, (child['id'],))
            upcoming = cursor.fetchall()

            results.append({
                'child': dict(child),
                'vaccinations': [dict(v) for v in vaccinations],
                'upcoming': [dict(u) for u in upcoming]
            })

        conn.close()

    return render_template('search_child.html', results=results, search_key=search_key)


# ==================== REMINDER ENGINE ====================
@app.route('/reminder')
def reminder():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))
    return render_template('reminder.html')


@app.route('/reminder_3days_whatsapp')
def reminder_3days_whatsapp():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))
    target = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, c.parent_mobile, s.vaccine_name, s.due_date
        FROM vaccination_schedule s
        JOIN children c ON c.id = s.child_id
        WHERE s.due_date=? AND s.status='pending'
    """, (target,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in data:
        send_whatsapp(row['parent_mobile'],
            f"🔔 Reminder: *{row['name']}* ka *{row['vaccine_name']}* vaccine *3 din baad* ({row['due_date']}) due hai.\n\nKripya apne sub-center par visit karein. Bacche ki sehat hamare haath mein hai! 💉")
    return render_template('reminder_result.html', data=data, reminder_type='3-Day Upcoming')


@app.route('/reminder_today_whatsapp')
def reminder_today_whatsapp():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))
    today  = datetime.now().strftime("%Y-%m-%d")
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, c.parent_mobile, s.vaccine_name, s.due_date
        FROM vaccination_schedule s
        JOIN children c ON c.id = s.child_id
        WHERE s.due_date=? AND s.status='pending'
    """, (today,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in data:
        send_whatsapp(row['parent_mobile'],
            f"🟢 Aaj *{row['name']}* ka *{row['vaccine_name']}* vaccine due hai.\n\nPlease aaj hi sub-center visit karein. 💉 Vaccination zaroori hai!")
    return render_template('reminder_result.html', data=data, reminder_type='Due Today')


@app.route('/reminder_missed_whatsapp')
def reminder_missed_whatsapp():
    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))
    today  = datetime.now().strftime("%Y-%m-%d")
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, c.parent_mobile, s.vaccine_name, s.due_date
        FROM vaccination_schedule s
        JOIN children c ON c.id = s.child_id
        WHERE s.due_date < ? AND s.status='pending'
    """, (today,))
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    for row in data:
        send_whatsapp(row['parent_mobile'],
            f"🔴 Alert: *{row['name']}* ka *{row['vaccine_name']}* vaccine *miss* ho gaya hai!\n\nDue date thi: {row['due_date']}\n\nKripya jaldi se sub-center par aayein aur vaccine dilwayein. Der hone se bachche ko khatara ho sakta hai. 🏥")
    return render_template('reminder_result.html', data=data, reminder_type='Missed Vaccines')


# ==================== REPORT ====================
# FIX: syntax error fixed, sub-center wise reports added
@app.route('/report', methods=['GET', 'POST'])
def report():
    data           = []
    summary        = {}
    selected_month = ''
    subcenter_summary = {}

    if request.method == 'POST':
        selected_month = request.form.get('month', '')
        if selected_month:
            conn   = get_db()
            cursor = conn.cursor()

            # Staff sees only their subcenter
            if 'staff_id' in session:
                subcenter = session.get('subcenter', '')
                cursor.execute("""
                    SELECT c.name, c.child_id, c.subcenter, v.vaccine_name, v.vacc_date
                    FROM vaccination_records v
                    JOIN children c ON c.id = v.child_id
                    WHERE strftime('%Y-%m', v.vacc_date) = ?
                    AND c.subcenter = ?
                    ORDER BY v.vacc_date DESC
                """, (selected_month, subcenter))
            else:
                # PHC sees all sub-centers
                cursor.execute("""
                    SELECT c.name, c.child_id, c.subcenter, v.vaccine_name, v.vacc_date
                    FROM vaccination_records v
                    JOIN children c ON c.id = v.child_id
                    WHERE strftime('%Y-%m', v.vacc_date) = ?
                    ORDER BY c.subcenter, v.vacc_date DESC
                """, (selected_month,))

            rows = cursor.fetchall()
            for row in rows:
                r = dict(row)
                data.append(r)
                summary[r['vaccine_name']] = summary.get(r['vaccine_name'], 0) + 1
                sc = r.get('subcenter', 'Unknown') or 'Unknown'
                if sc not in subcenter_summary:
                    subcenter_summary[sc] = {'total': 0, 'vaccines': {}}
                subcenter_summary[sc]['total'] += 1
                subcenter_summary[sc]['vaccines'][r['vaccine_name']] = subcenter_summary[sc]['vaccines'].get(r['vaccine_name'], 0) + 1

            conn.close()

    return render_template('report.html',
        data=data,
        summary=summary,
        selected_month=selected_month,
        subcenter_summary=subcenter_summary
    )


# ==================== PARENT ====================
@app.route('/parent_login', methods=['GET', 'POST'])
def parent_login():
    if request.method == 'POST':
        child_name = request.form.get('child_name', '').strip()
        mobile     = request.form.get('mobile', '').strip()

        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM children WHERE name=? AND parent_mobile=?", (child_name, mobile))
        child = cursor.fetchone()
        conn.close()

        if child:
            session.clear()
            session['child_db_id'] = child['id']
            session['child_name']  = child['name']
            return redirect('/parent_dashboard')
        flash('No record found. Please check the name and mobile number.', 'error')

    return render_template('parent_login.html')


@app.route('/parent_dashboard')
def parent_dashboard():
    if 'child_db_id' not in session:
        return redirect('/parent_login')

    child_db_id = session['child_db_id']
    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM children WHERE id=?", (child_db_id,))
    child = cursor.fetchone()

    # All given vaccines
    cursor.execute("""
        SELECT vaccine_name, vacc_date FROM vaccination_records
        WHERE child_id=? ORDER BY vacc_date ASC
    """, (child_db_id,))
    given_vaccines = [dict(v) for v in cursor.fetchall()]

    # All pending vaccines from schedule
    cursor.execute("""
        SELECT vaccine_name, due_date FROM vaccination_schedule
        WHERE child_id=? AND status='pending' ORDER BY due_date ASC
    """, (child_db_id,))
    pending_vaccines = [dict(v) for v in cursor.fetchall()]

    # Full vaccine info with AEFI and care from vaccines_master
    cursor.execute("SELECT * FROM vaccines_master ORDER BY name")
    vaccines_info = [dict(v) for v in cursor.fetchall()]

    conn.close()

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template('parent_dashboard.html',
        child=dict(child),
        given_vaccines=given_vaccines,
        pending_vaccines=pending_vaccines,
        vaccines_info=vaccines_info,
        today=today
    )


# ==================== PHC / HOSPITAL ====================
# FIX: PHC login uses staff's PHC name + staff password (any staff of that PHC)
@app.route('/hospital_login', methods=['GET', 'POST'])
def hospital_login():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        password = request.form.get('password', '')

        conn   = get_db()
        cursor = conn.cursor()

        # First try phc table
        cursor.execute("SELECT * FROM phc WHERE name=?", (name,))
        phc = cursor.fetchone()

        if phc and check_password_hash(phc['password'], password):
            session.clear()
            session['phc_name'] = name
            conn.close()
            return redirect('/phc_dashboard')

        # FIX: Also allow login using PHC name + any staff password from that PHC
        cursor.execute("SELECT * FROM staff WHERE phc_name=?", (name,))
        staff_list = cursor.fetchall()
        conn.close()

        authenticated = False
        for staff in staff_list:
            if check_password_hash(staff['password'], password):
                authenticated = True
                break

        if authenticated:
            session.clear()
            session['phc_name'] = name
            return redirect('/phc_dashboard')

        flash('Invalid PHC credentials. Please use your PHC name and staff password.', 'error')

    return render_template('hospital_login.html')


@app.route('/phc_dashboard')
def phc_dashboard():
    if 'phc_name' not in session:
        return redirect('/hospital_login')

    phc_name = session['phc_name']
    conn     = get_db()
    cursor   = conn.cursor()

    # Children under this PHC only (via staff subcenter → phc_name linkage)
    cursor.execute("""
        SELECT COUNT(DISTINCT c.id) FROM children c
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ?
    """, (phc_name,))
    total_children = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT vr.id) FROM vaccination_records vr
        JOIN children c ON c.id = vr.child_id
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ?
    """, (phc_name,))
    total_vaccines = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*) FROM vaccination_schedule vs
        JOIN children c ON c.id = vs.child_id
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ? AND vs.due_date = ? AND vs.status='pending'
    """, (phc_name, today))
    due_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM vaccination_schedule vs
        JOIN children c ON c.id = vs.child_id
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ? AND vs.due_date < ? AND vs.status='pending'
    """, (phc_name, today))
    overdue_count = cursor.fetchone()[0]

    # Sub-center wise children count
    cursor.execute("""
        SELECT c.subcenter, COUNT(DISTINCT c.id) as cnt
        FROM children c
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ?
        GROUP BY c.subcenter
    """, (phc_name,))
    subcenter_data = cursor.fetchall()

    # Recent 10 vaccinations
    cursor.execute("""
        SELECT c.name, c.child_id, c.subcenter, v.vaccine_name, v.vacc_date
        FROM vaccination_records v
        JOIN children c ON c.id = v.child_id
        JOIN staff s ON s.subcenter_name = c.subcenter
        WHERE s.phc_name = ?
        ORDER BY v.vacc_date DESC LIMIT 10
    """, (phc_name,))
    recent = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return render_template('phc_dashboard.html',
        phc_name=phc_name,
        total_children=total_children,
        total_vaccines=total_vaccines,
        due_today=due_today,
        overdue_count=overdue_count,
        subcenter_data=subcenter_data,
        recent=recent
    )


# ==================== LOGOUT ====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
