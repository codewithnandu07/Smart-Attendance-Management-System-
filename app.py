import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="AttendSmart", page_icon="🎓", layout="wide")

FILE = "attendance.csv"
STUDENT_FILE = "students.csv"

if not os.path.exists(STUDENT_FILE):
    pd.DataFrame([["101","Aarav Sharma"],["102","Priya Patel"],["103","Rahul Verma"]], columns=["roll","name"]).to_csv(STUDENT_FILE, index=False)
if not os.path.exists(FILE):
    pd.DataFrame(columns=["roll","name","date","time","status"]).to_csv(FILE, index=False)

st.title("🎓 AttendSmart - Smart Attendance System")
st.caption(datetime.now().strftime("%d %B %Y | %I:%M %p"))

c1, c2 = st.columns([1, 1.4])

with c1:
    st.subheader("📸 Mark Attendance")
    # Camera works fast without face lib
    st.camera_input("Live Camera")

    students = pd.read_csv(STUDENT_FILE)
    choice = st.selectbox("Select Student", students["roll"].astype(str) + " - " + students["name"])
    roll = choice.split(" - ")[0]
    name = choice.split(" - ")[1]

    colA, colB = st.columns(2)
    with colA:
        if st.button("✅ Present", use_container_width=True):
            now = datetime.now()
            date, time = now.strftime("%d/%m/%Y"), now.strftime("%I:%M %p")
            df = pd.read_csv(FILE)
            if ((df["roll"].astype(str)==roll) & (df["date"]==date)).any():
                st.warning(f"{name} already marked!")
            else:
                pd.DataFrame([[roll,name,date,time,"Present"]], columns=["roll","name","date","time","status"]).to_csv(FILE, mode='a', header=False, index=False)
                st.success(f"Marked: {name}"); st.balloons()

    st.divider()
    st.subheader("➕ Add Student")
    with st.form("add", clear_on_submit=True):
        r = st.text_input("Roll No")
        n = st.text_input("Name")
        if st.form_submit_button("Add"):
            if r and n:
                pd.DataFrame([[r,n]], columns=["roll","name"]).to_csv(STUDENT_FILE, mode='a', header=False, index=False)
                st.success("Added!"); st.rerun()

with c2:
    st.subheader("📋 Today's Attendance")
    df = pd.read_csv(FILE)
    today = datetime.now().strftime("%d/%m/%Y")
    today_df = df[df["date"]==today].iloc[::-1]

    m1,m2,m3 = st.columns(3)
    m1.metric("Total Students", len(students))
    m2.metric("Present Today", len(today_df))
    rate = int(len(today_df)/len(students)*100) if len(students) else 0
    m3.metric("Rate", f"{rate}%")

    st.dataframe(today_df, use_container_width=True, hide_index=True)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "attendance.csv", "text/csv", use_container_width=True)
    if st.button("🗑️ Clear Today Data"):
        df = df[df["date"]!=today]
        df.to_csv(FILE, index=False)
        st.rerun()
