
import streamlit as st
import pandas as pd, os, pickle, cv2, numpy as np
from datetime import datetime
import face_recognition

st.set_page_config(page_title="AttendSmart AI", layout="wide")
st.title("🎓 AttendSmart - Auto Face Attendance")

DB="face_db.pkl"
FILE="attendance.csv"
if not os.path.exists(FILE): pd.DataFrame(columns=["roll","name","date","time"]).to_csv(FILE,index=False)
if not os.path.exists(DB):
    with open(DB,'wb') as f: pickle.dump({},f)

def load_db():
    with open(DB,'rb') as f: return pickle.load(f)
def save_db(d):
    with open(DB,'wb') as f: pickle.dump(d,f)

tab1, tab2, tab3 = st.tabs(["✅ AUTO ATTENDANCE","➕ REGISTER","📋 SHEET"])

with tab2:
    st.subheader("Register Face Once")
    roll=st.text_input("Roll No", key="r")
    name=st.text_input("Name", key="n")
    pic=st.camera_input("Take Photo")
    if pic and roll and name and st.button("Save Face"):
        bytes_data = pic.getvalue()
        img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        enc = face_recognition.face_encodings(rgb)
        if not enc:
            st.error("No face detected, try again")
        else:
            db=load_db(); db[roll]={"name":name,"enc":enc[0]}; save_db(db)
            st.success(f"Saved {name} - Now go to AUTO tab, it will recognize you automatically")

with tab1:
    st.subheader("Just Show Your Face - No Typing")
    st.info("Take a photo - system will auto-detect who you are and mark attendance")
    snap = st.camera_input("Scan Face for Attendance", key="scan")

    if snap:
        bytes_data = snap.getvalue()
        img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)

        if not encs:
            st.error("No face found")
        else:
            db=load_db()
            if not db: st.warning("No students registered yet")
            else:
                known_encs = [v["enc"] for v in db.values()]
                results = face_recognition.compare_faces(known_encs, encs[0], 0.5)
                if True in results:
                    idx=results.index(True)
                    roll=list(db.keys())[idx]
                    name=db[roll]["name"]
                    now=datetime.now()
                    date=now.strftime("%d/%m/%Y"); time=now.strftime("%I:%M %p")
                    df=pd.read_csv(FILE)
                    if ((df["roll"].astype(str)==str(roll)) & (df["date"]==date)).any():
                        st.warning(f"⚠️ {name} already marked today")
                    else:
                        pd.DataFrame([[roll,name,date,time]], columns=["roll","name","date","time"]).to_csv(FILE,mode='a',header=False,index=False)
                        st.success(f"✅ Auto Marked: {name} ({roll}) at {time}"); st.balloons()
                else:
                    st.error("Face not recognized - Please register first")

with tab3:
    df=pd.read_csv(FILE)
    st.dataframe(df.iloc[::-1], use_container_width=True)
    st.download_button("Export CSV", df.to_csv(index=False), "attendance.csv")
