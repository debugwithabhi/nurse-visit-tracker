import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(layout="wide")

# =============================
# PROFESSIONAL UI STYLING
# =============================
st.markdown("""
<style>

/* =========================
   PAGE BACKGROUND
========================= */
.main {
    background-color: #f4f6f9;
}

/* =========================
   HEADINGS
========================= */
h1, h2, h3, h4, h5, h6 {
    color: #00F5E9 !important;
}

/* =========================
   LABELS
========================= */
label {
    color: #00F5E9 !important;
    font-weight: 500;
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: #00F5E9 !important;
}

/* Radio Buttons */
.stRadio label {
    color: #00F5E9 !important;
}

/* Selectbox Label */
.stSelectbox label {
    color: #00F5E9 !important;
}

/* Date & Time Labels */
.stDateInput label,
.stTimeInput label {
    color: #00F5E9 !important;
}

/* Number Input Label */
.stNumberInput label {
    color: #00F5E9 !important;
}

/* =========================
   CUSTOM PAGE TITLE
========================= */
.page-title {
    font-size: 35px;
    font-weight: 700;
    padding: 10px 0px;
    margin-bottom: 25px;
    border-bottom: 3px solid #00F5E9;
    color: #00F5E9;
}

/* =========================
   BUTTONS
========================= */
.stButton>button {
    background-color: #00F5E9;
    color: #0F172A;
    border-radius: 8px;
    height: 42px;
    font-weight: 600;
    border: none;
    box-shadow: 0px 3px 8px rgba(0, 245, 233, 0.3);
    transition: all 0.2s ease-in-out;
}

.stButton>button:hover {
    background-color: #00d9cf;
    color:#0F172A;
    box-shadow: 0px 4px 12px rgba(0, 245, 233, 0.5);
    transform: translateY(-1px);
}

/* =========================
   INPUT FIELDS
========================= */

/* Rounded Corners */
input, 
.stSelectbox, 
.stDateInput, 
.stTimeInput,
.stNumberInput {
    border-radius: 8px !important;
}

/* Input Text Color */
input {
    color: #1e293b !important;   /* Dark Slate */
}

/* Selectbox Selected Text */
.stSelectbox div[data-baseweb="select"] {
    color: #1e293b !important;
}

/* Placeholder Text */
input::placeholder {
    color: #64748b !important;
}

/* =========================
   TABLE STYLING
========================= */

/* Table Container */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #cbd5e1;
}

/* Table Cell Text */
[data-testid="stDataFrame"] td {
    color: #1e293b !important;
    font-size: 14px;
}

/* Table Header */
[data-testid="stDataFrame"] th {
    color: #00F5E9 !important;
    font-weight: 600;
    background-color: #e6fffc !important;
}

/* Table Row Hover Effect */
[data-testid="stDataFrame"] tbody tr:hover {
    background-color: #f1f5f9 !important;
}

/* =========================
   FOOTER
========================= */
.footer {
    text-align: center;
    padding: 25px 10px 10px 10px;
    font-size: 14px;
    color: #00F5E9;
    margin-top: 50px;
    border-top: 1px solid #00F5E9;
}

</style>
""", unsafe_allow_html=True)# =============================
# DATABASE CONNECTION
# =============================
conn = sqlite3.connect("nurse_tracker.db", check_same_thread=False)
c = conn.cursor()

# =============================
# CREATE TABLES
# =============================
c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    charge INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS nurses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
# SIDEBAR NAVIGATION
# =============================
st.sidebar.markdown("## 🧭 Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio("Go To", ["Dashboard", "Visits", "Earnings"])
st.sidebar.markdown("---")
st.sidebar.caption("Nurse Visit Management System")

# =============================
# LOAD DATA
# =============================
patients = c.execute("SELECT name FROM patients").fetchall()
patient_list = [p[0] for p in patients]

nurses = c.execute("SELECT name FROM nurses").fetchall()
nurse_list = [n[0] for n in nurses]

# =============================
# DASHBOARD PAGE
# =============================
if page == "Dashboard":

    st.markdown('<div class="page-title">🏥 Nurse Visit Tracker</div>', unsafe_allow_html=True)

    st.markdown("### 👩‍⚕️ Nurse Management")
    new_nurse = st.text_input("Nurse Name")
    if st.button("Add Nurse"):
        if new_nurse:
            try:
                c.execute("INSERT INTO nurses (name) VALUES (?)", (new_nurse,))
                conn.commit()
                st.success("Nurse Added")
                st.rerun()
            except:
                st.warning("Nurse already exists")

    if nurse_list:
        delete_nurse = st.selectbox("Select Nurse to Delete", nurse_list)
        if st.button("Delete Nurse"):
            c.execute("DELETE FROM nurses WHERE name=?", (delete_nurse,))
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
                c.execute(
                    "INSERT INTO patients (name, charge) VALUES (?,?)",
                    (new_patient, charge)
                )
                conn.commit()
                st.success("Patient Added")
                st.rerun()
            except:
                st.warning("Patient already exists")

    if patient_list:
        delete_patient = st.selectbox("Select Patient to Delete", patient_list)
        if st.button("Delete Patient"):
            c.execute("DELETE FROM patients WHERE name=?", (delete_patient,))
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
            paid_status = st.selectbox("Payment Status", ["Unpaid", "Paid"])

        if st.button("Save Visit"):
            patient_id = c.execute(
                "SELECT id FROM patients WHERE name=?",
                (selected_patient,)
            ).fetchone()[0]

            c.execute("""
            INSERT INTO visits (patient_id, nurse_name, visit_date, visit_time, paid)
            VALUES (?,?,?,?,?)
            """, (
                patient_id,
                selected_nurse,
                str(visit_date),
                visit_time.strftime("%H:%M"),
                paid_status
            ))

            conn.commit()
            st.success("Visit Saved")
            st.rerun()

# =============================
# VISITS PAGE
# =============================
elif page == "Visits":

    st.markdown('<div class="page-title">📋 Visit History</div>', unsafe_allow_html=True)
    st.markdown("### 🔎 Filters")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        filter_nurse = st.selectbox("Filter Nurse", ["All"] + nurse_list)

    with col2:
        filter_patient = st.selectbox("Filter Patient", ["All"] + patient_list)

    with col3:
        filter_payment = st.selectbox("Payment", ["All", "Paid", "Unpaid"])

    with col4:
        from_date = st.date_input("From Date")

    with col5:
        to_date = st.date_input("To Date")

    query = """
    SELECT visits.id, patients.name, visits.nurse_name,
           visits.visit_date, visits.visit_time,
           visits.paid, patients.charge
    FROM visits
    JOIN patients ON visits.patient_id = patients.id
    WHERE 1=1
    """

    params = []

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
        df = pd.DataFrame(data, columns=[
            "Visit ID","Patient","Nurse","Date",
            "Time","Payment Status","Charge"
        ])
        # Dynamic table height (max 10 rows visible)
        row_count = len(df)
        rows_to_show = min(row_count, 10)

        # Approximate row height calculation
        dynamic_height = rows_to_show * 38 + 45

        st.dataframe(df,use_container_width=True,height=dynamic_height)

        st.markdown("---")
        st.markdown("### ⚙️ Manage Selected Visit")

        visit_ids = df["Visit ID"].tolist()
        selected_visit = st.selectbox("Select Visit ID", visit_ids)

        colA, colB = st.columns(2)

        with colA:
            new_status = st.selectbox("Change Payment Status",["Paid","Unpaid"])
            if st.button("Update Payment"):
                c.execute("UPDATE visits SET paid=? WHERE id=?",
                          (new_status, selected_visit))
                conn.commit()
                st.success("Payment Updated")
                st.rerun()

        with colB:
            if st.button("Delete Visit"):
                c.execute("DELETE FROM visits WHERE id=?",(selected_visit,))
                conn.commit()
                st.success("Visit Deleted")
                st.rerun()
    else:
        st.info("No Visits Found")

# =============================
# EARNINGS PAGE
# =============================
elif page == "Earnings":

    st.markdown('<div class="page-title">💰 Complete Earnings</div>', unsafe_allow_html=True)

    selected_nurse = st.selectbox("Select Nurse", ["All"] + nurse_list)

    query = """
    SELECT patients.name, visits.nurse_name,
           visits.visit_date, visits.visit_time,
           visits.paid, patients.charge
    FROM visits
    JOIN patients ON visits.patient_id = patients.id
    WHERE 1=1
    """

    params = []

    if selected_nurse != "All":
        query += " AND visits.nurse_name=?"
        params.append(selected_nurse)

    query += " ORDER BY visits.visit_date DESC"

    data = c.execute(query, tuple(params)).fetchall()

    if data:
        df = pd.DataFrame(data, columns=[
            "Patient","Nurse","Date",
            "Time","Payment Status","Charge"
        ])
        # Dynamic table height (max 10 rows visible)
        row_count = len(df)
        rows_to_show = min(row_count, 10)

        dynamic_height = rows_to_show * 38 + 45

        st.dataframe(df,use_container_width=True,height=dynamic_height)

        total = df["Charge"].sum()
        paid_total = df[df["Payment Status"] == "Paid"]["Charge"].sum()
        unpaid_total = df[df["Payment Status"] == "Unpaid"]["Charge"].sum()

        st.markdown("---")
        st.subheader("Summary")
        st.write(f"Total Earnings: ₹ {total}")
        st.write(f"Paid: ₹ {paid_total}")
        st.write(f"Unpaid: ₹ {unpaid_total}")
    else:
        st.info("No Data Available")

# =============================
# FOOTER
# =============================
st.markdown(
    '<div class="footer">Developed by <b>Abhishek Lalzare</b> © 2026</div>',
    unsafe_allow_html=True
)
