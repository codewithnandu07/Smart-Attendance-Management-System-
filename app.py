import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="AttendSmart AI", page_icon="🎓", layout="wide")

STUDENT_FILE = "students.csv"
ATTEND_FILE = "attendance.csv"

# Create files first time
if not os.path.exists(STUDENT_FILE):
    pd.DataFrame(
        [["101","Aarav Sharma"],["102","Priya Patel"],["103","Rahul Verma"]],
        columns=["roll","name"]
    ).to_csv(STUDENT_FILE, index=False)

if not os.path.exists(ATTEND_FILE):
    pd.DataFrame(columns=["roll","name","date","time","status"]).to_csv(ATTEND_FILE, index=False)

# Custom CSS
st.markdown("""
<style>
.stButton>button{background:#4f46e5;color:white;border-radius:10px;font-weight:600;height:45px}
div[data-testid="metric"]{background:white;padding:15px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.05)}
</style>
""", unsafe_allow_html=True)

st.title("🎓 AttendSmart - AI Based Smart Attendance")
st.caption(f"📅 {datetime.now().strftime('%d %B %Y, %I:%M %p')}")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📸 Live Attendance Scanner")
    st.camera_input("Scan Face", key="camera")

    students = pd.read_csv(STUDENT_FILE)
    option = st.selectbox("Select Student ID", students["roll"].astype(str) + " - " + students["name"])
    roll = option.split(" - ")[0]
    name = option.split(" - ")[1]

    if st.button("Mark Present", use_container_width=True):
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%I:%M:%S %p")
        status = "Late" if now.hour >= 10 else "Present"

        df = pd.read_csv(ATTEND_FILE)
        already = ((df["roll"].astype(str)==str(roll)) & (df["date"]==date)).any()

        if already:
            st.warning(f"⚠️ {name} already marked today!")
        else:
            pd.DataFrame([[roll,name,date,time,status]], columns=["roll","name","date","time","status"]).to_csv(ATTEND_FILE, mode='a', header=False, index=False)
            st.success(f"✅ {name} Marked as {status} at {time}")
            st.balloons()

    st.divider()
    st.subheader("➕ Add New Student")
    with st.form("add"):
        new_roll = st.text_input("Roll No")
        new_name = st.text_input("Student Name")
        submitted = st.form_submit_button("Add Student")
        if submitted:
            if new_roll and new_name:
                pd.DataFrame([[new_roll,new_name]], columns=["roll","name"]).to_csv(STUDENT_FILE, mode='a', header=False, index=False)
                st.success("Student Added Successfully!")
                st.rerun()
            else:
                st.error("Enter both fields")

with col2:
    st.subheader("📋 Today's Attendance Sheet")
    df = pd.read_csv(ATTEND_FILE)
    today = datetime.now().strftime("%d/%m/%Y")
    today_df = df[df["date"]==today].sort_index(ascending=False)

    m1,m2,m3 = st.columns(3)
    m1.metric("Total Students", len(students))
    m2.metric("Present Today", len(today_df))
    rate = int(len(today_df)/len(students)*100) if len(students)>0 else 0
    m3.metric("Attendance Rate", f"{rate}%")

    st.dataframe(today_df, use_container_width=True, hide_index=True)

    c1,c2 = st.columns(2)
    c1.download_button("📥 Export CSV", today_df.to_csv(index=False), "attendance.csv", "text/csv", use_container_width=True)
    if c2.button("🗑️ Clear Today", use_container_width=True):
        df = df[df["date"]!=today]
        df.to_csv(ATTEND_FILE, index=False)
        st.rerun()
