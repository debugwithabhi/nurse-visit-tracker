import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# =============================
# DATABASE CONNECTION
# =============================
conn = sqlite3.connect("nurse_tracker.db", check_same_thread=False)
c = conn.cursor()

# =============================
# CREATE TABLES
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    pin TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    name TEXT,
    charge INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS nurses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    name TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    patient_id INTEGER,
    nurse_name TEXT,
    visit_date TEXT,
    visit_time TEXT,
    paid TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
""")
conn.commit()

# =============================
# ADMIN CREDENTIALS
# =============================
ADMIN_USER = "admin"
ADMIN_PIN = "2409"

# =============================
# SESSION STATE
# =============================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.is_admin = False

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.authenticated:
    st.markdown("## 🔒 Login Details")
    username_input = st.text_input("Username")
    pin_input = st.text_input("PIN", type="password")

    if st.button("Login"):
        if username_input == ADMIN_USER and pin_input == ADMIN_PIN:
            st.session_state.authenticated = True
            st.session_state.username = username_input
            st.session_state.is_admin = True
            st.rerun()
        else:
            user_record = c.execute(
                "SELECT * FROM users WHERE username=? AND pin=?",
                (username_input, pin_input)
            ).fetchone()
            if user_record:
                st.session_state.authenticated = True
                st.session_state.username = username_input
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("Invalid username or PIN")

    # Footer on login page
    st.markdown('<div class="footer">Developed by <b>Abhishek Lalzare</b> © 2026</div>', unsafe_allow_html=True)
# =============================
# AFTER LOGIN
# =============================
if st.session_state.authenticated:
    current_user = st.session_state.username
    is_admin = st.session_state.is_admin

    st.markdown(f"### 👤 Logged in as: {current_user}")

    # =============================
    # STYLING
    # =============================
    st.markdown("""
    <style>
    .main {background-color: #0f172a;}
    h1,h2,h3,h4,h5,h6 {color: #00F5E9 !important;}
    label {color: #00F5E9 !important; font-weight:500;}
    section[data-testid="stSidebar"] * {color:#00F5E9 !important;}
    .stButton>button {background-color: #00F5E9;color: #0F172A;border-radius: 8px;height: 42px;font-weight: 600;border: none;box-shadow: 0px 3px 8px rgba(0,245,233,0.3);transition: all 0.2s ease-in-out;}
    .stButton>button:hover {background-color: #00d9cf;color:#0F172A;box-shadow: 0px 4px 12px rgba(0,245,233,0.5);transform: translateY(-1px);}
    input, textarea {background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #334155 !important;}
    .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input, .stNumberInput input {background-color: #1e293b !important; color: #ffffff !important;}
    input::placeholder {color:#94a3b8 !important;}
    input, .stSelectbox, .stDateInput, .stTimeInput, .stNumberInput {border-radius:8px !important;}
    .page-title {font-size: 35px; font-weight:700; padding:10px 0; margin-bottom:25px; border-bottom:3px solid #00F5E9; color:#00F5E9;}
    [data-testid="stDataFrame"] {border-radius:10px; overflow:hidden; border:1px solid #cbd5e1;}
    [data-testid="stDataFrame"] td {color:#ffffff !important; font-size:14px;}
    [data-testid="stDataFrame"] th {color:#00F5E9 !important; font-weight:600; background-color:#0f172a !important;}
    [data-testid="stDataFrame"] tbody tr:hover {background-color:#334155 !important;}
    .footer {text-align:center; padding:25px 10px 10px 10px; font-size:14px; color:#00F5E9; margin-top:50px; border-top:1px solid #00F5E9;}
    </style>
    """, unsafe_allow_html=True)

    # =============================
    # ADMIN DASHBOARD
    # =============================
    if is_admin:
        st.markdown('<div class="page-title">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
        st.subheader("Manage Users")

        # Add new user
        new_username = st.text_input("New Username")
        new_pin = st.text_input("New PIN")
        if st.button("Add User"):
            if new_username and new_pin:
                try:
                    c.execute("INSERT INTO users (username,pin) VALUES (?,?)",(new_username,new_pin))
                    conn.commit()
                    st.success(f"User '{new_username}' added")
                    st.rerun()
                except:
                    st.warning("User already exists")

        # Delete user
        existing_users = [u[0] for u in c.execute("SELECT username FROM users").fetchall()]
        if existing_users:
            delete_user = st.selectbox("Select User to Delete", existing_users)
            if st.button("Delete User"):
                c.execute("DELETE FROM users WHERE username=?",(delete_user,))
                conn.commit()
                st.success(f"User '{delete_user}' deleted")
                st.rerun()

        # Logout
        if st.button("Logout 🔒"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()

    # =============================
    # USER DASHBOARD
    # =============================
    else:
        st.markdown('<div class="page-title">🏥 Nurse Visit Tracker</div>', unsafe_allow_html=True)

        # Sidebar Navigation
        st.sidebar.markdown("## 🧭 Navigation")
        st.sidebar.markdown("---")
        page = st.sidebar.radio("Go To", ["Dashboard", "Visits", "Earnings"])
        st.sidebar.markdown("---")
        st.sidebar.caption("Nurse Visit Management System")

        # Load patients/nurses
        patients = c.execute("SELECT name FROM patients WHERE user=?",(current_user,)).fetchall()
        patient_list = [p[0] for p in patients]
        nurses = c.execute("SELECT name FROM nurses WHERE user=?",(current_user,)).fetchall()
        nurse_list = [n[0] for n in nurses]

        # -------------------------
        # FUNCTION TO GET DYNAMIC HEIGHT
        # -------------------------
        def table_height(df):
            # 5 rows max
            rows = min(len(df), 5)
            row_height = 38
            header_height = 45
            return rows*row_height + header_height

        # -------------------------
        # DASHBOARD PAGE
        # -------------------------
        if page == "Dashboard":
            st.markdown("### 👩‍⚕️ Nurse Management")
            new_nurse = st.text_input("Nurse Name")
            if st.button("Add Nurse"):
                if new_nurse:
                    try:
                        c.execute("INSERT INTO nurses (user,name) VALUES (?,?)",(current_user,new_nurse))
                        conn.commit()
                        st.success("Nurse Added")
                        st.rerun()
                    except:
                        st.warning("Nurse already exists")
            if nurse_list:
                delete_nurse = st.selectbox("Select Nurse to Delete", nurse_list)
                if st.button("Delete Nurse"):
                    c.execute("DELETE FROM nurses WHERE name=? AND user=?",(delete_nurse,current_user))
                    conn.commit()
                    st.success("Deleted")
                    st.rerun()

            st.markdown("---")
            st.markdown("### 🧑‍🦳 Patient Management")
            new_patient = st.text_input("Patient Name")
            charge = st.number_input("Charge Per Visit", min_value=0)
            if st.button("Add Patient"):
                if new_patient:
                    try:
                        c.execute("INSERT INTO patients (user,name,charge) VALUES (?,?,?)",(current_user,new_patient,charge))
                        conn.commit()
                        st.success("Patient Added")
                        st.rerun()
                    except:
                        st.warning("Patient already exists")
            if patient_list:
                delete_patient = st.selectbox("Select Patient to Delete", patient_list)
                if st.button("Delete Patient"):
                    c.execute("DELETE FROM patients WHERE name=? AND user=?",(delete_patient,current_user))
                    conn.commit()
                    st.success("Deleted")
                    st.rerun()

            st.markdown("---")
            st.markdown("### ➕ Add Visit Entry")
            if patient_list and nurse_list:
                col1, col2 = st.columns(2)
                with col1:
                    selected_patient = st.selectbox("Patient", patient_list)
                    selected_nurse = st.selectbox("Nurse", nurse_list)
                    visit_date = st.date_input("Visit Date", date.today())
                with col2:
                    visit_time = st.time_input("Visit Time")
                    paid_status = st.selectbox("Payment Status", ["Unpaid","Paid"])
                if st.button("Save Visit"):
                    patient_id = c.execute("SELECT id FROM patients WHERE name=? AND user=?",(selected_patient,current_user)).fetchone()[0]
                    c.execute("""
                    INSERT INTO visits (user,patient_id,nurse_name,visit_date,visit_time,paid)
                    VALUES (?,?,?,?,?,?)
                    """,(current_user,patient_id,selected_nurse,str(visit_date),visit_time.strftime("%H:%M"),paid_status))
                    conn.commit()
                    st.success("Visit Saved")
                    st.rerun()

            if st.button("Logout 🔒"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.is_admin = False
                st.rerun()

        # -------------------------
        # VISITS PAGE
        # -------------------------
        elif page == "Visits":
            st.markdown('<div class="page-title">📋 Visit History</div>', unsafe_allow_html=True)
            st.markdown("### 🔎 Filters")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                filter_nurse = st.selectbox("Filter Nurse", ["All"] + nurse_list)
            with col2:
                filter_patient = st.selectbox("Filter Patient", ["All"] + patient_list)
            with col3:
                filter_payment = st.selectbox("Payment", ["All","Paid","Unpaid"])
            with col4:
                from_date = st.date_input("From Date")
            with col5:
                to_date = st.date_input("To Date")

            query = """
            SELECT visits.id, patients.name, visits.nurse_name, visits.visit_date, visits.visit_time, visits.paid, patients.charge
            FROM visits
            JOIN patients ON visits.patient_id = patients.id
            WHERE visits.user=?
            """
            params = [current_user]

            if filter_nurse != "All":
                query += " AND visits.nurse_name=?"
                params.append(filter_nurse)
            if filter_patient != "All":
                query += " AND patients.name=?"
                params.append(filter_patient)
            if filter_payment != "All":
                query += " AND visits.paid=?"
                params.append(filter_payment)
            if from_date and to_date:
                query += " AND visits.visit_date BETWEEN ? AND ?"
                params.append(str(from_date))
                params.append(str(to_date))

            query += " ORDER BY visits.visit_date DESC, visits.visit_time DESC"
            data = c.execute(query, tuple(params)).fetchall()

            if data:
                df = pd.DataFrame(data, columns=["Visit ID","Patient","Nurse","Date","Time","Payment Status","Charge"])
                st.dataframe(df,use_container_width=True,height=table_height(df))

                st.markdown("---")
                st.markdown("### ⚙️ Manage Selected Visit")
                visit_ids = df["Visit ID"].tolist()
                selected_visit = st.selectbox("Select Visit ID", visit_ids)

                colA, colB = st.columns(2)
                with colA:
                    new_status = st.selectbox("Change Payment Status",["Paid","Unpaid"])
                    if st.button("Update Payment"):
                        c.execute("UPDATE visits SET paid=? WHERE id=? AND user=?",(new_status,selected_visit,current_user))
                        conn.commit()
                        st.success("Payment Updated")
                        st.rerun()
                with colB:
                    if st.button("Delete Visit"):
                        c.execute("DELETE FROM visits WHERE id=? AND user=?",(selected_visit,current_user))
                        conn.commit()
                        st.success("Visit Deleted")
                        st.rerun()
            else:
                st.info("No Visits Found")

            if st.button("Logout 🔒"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.is_admin = False
                st.rerun()

        # -------------------------
        # EARNINGS PAGE
        # -------------------------
        elif page == "Earnings":
            st.markdown('<div class="page-title">💰 Complete Earnings</div>', unsafe_allow_html=True)
            selected_nurse = st.selectbox("Select Nurse", ["All"] + nurse_list)

            query = """
            SELECT patients.name, visits.nurse_name, visits.visit_date, visits.visit_time, visits.paid, patients.charge
            FROM visits
            JOIN patients ON visits.patient_id = patients.id
            WHERE visits.user=?
            """
            params = [current_user]
            if selected_nurse != "All":
                query += " AND visits.nurse_name=?"
                params.append(selected_nurse)
            query += " ORDER BY visits.visit_date DESC"
            data = c.execute(query, tuple(params)).fetchall()
            if data:
                df = pd.DataFrame(data, columns=["Patient","Nurse","Date","Time","Payment Status","Charge"])
                st.dataframe(df,use_container_width=True,height=table_height(df))

                total = df["Charge"].sum()
                paid_total = df[df["Payment Status"]=="Paid"]["Charge"].sum()
                unpaid_total = df[df["Payment Status"]=="Unpaid"]["Charge"].sum()

                st.markdown("---")
                st.subheader("Summary")
                st.write(f"Total Earnings: ₹ {total}")
                st.write(f"Paid: ₹ {paid_total}")
                st.write(f"Unpaid: ₹ {unpaid_total}")
            else:
                st.info("No Data Available")

            if st.button("Logout 🔒"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.is_admin = False
                st.rerun()

        # Footer
        st.markdown('<div class="footer">Developed by <b>Abhishek Lalzare</b> © 2026</div>', unsafe_allow_html=True)
