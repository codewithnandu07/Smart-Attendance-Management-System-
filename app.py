import streamlit as st
import cv2
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

# Try to import face_recognition, if not available use simple version
try:
    import face_recognition
    FACE_LIB = True
except:
    FACE_LIB = False

st.set_page_config(page_title="AttendSmart AI", layout="wide")
st.title("🎓 AttendSmart - REAL Face Recognition")

DB_PATH = "face_db.pkl"
ATTEND_FILE = "attendance.csv"

if not os.path.exists(ATTEND_FILE):
    pd.DataFrame(columns=["roll","name","date","time","status"]).to_csv(ATTEND_FILE, index=False)
if not os.path.exists(DB_PATH):
    with open(DB_PATH, 'wb') as f: pickle.dump({}, f)

def load_db():
    with open(DB_PATH, 'rb') as f: return pickle.load(f)
def save_db(db):
    with open(DB_PATH, 'wb') as f: pickle.dump(db, f)

menu = st.sidebar.selectbox("Menu", ["Mark Attendance - AUTO", "Register New Student", "View Sheet"])

# 1. REGISTER
if menu == "Register New Student":
    st.header("➕ Register Face")
    roll = st.text_input("Roll No")
    name = st.text_input("Name")
    img_file = st.camera_input("Take Photo to Register Face")

    if img_file and roll and name:
        if st.button("Save Face"):
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if FACE_LIB:
                enc = face_recognition.face_encodings(rgb)
                if len(enc)==0:
                    st.error("No Face Found! Try again.")
                else:
                    db = load_db()
                    db[roll] = {"name": name, "encoding": enc[0]}
                    save_db(db)
                    st.success(f"✅ Face Registered for {name}")
            else:
                # Fallback: save image path for simple matching (demo)
                cv2.imwrite(f"{roll}_{name}.jpg", img)
                db = load_db()
                db[roll] = {"name": name, "encoding": "simple"}
                save_db(db)
                st.success(f"✅ Registered {name} (Simple Mode)")

# 2. AUTO MARK
elif menu == "Mark Attendance - AUTO":
    st.header("📸 Auto Face Scanner - Just Come in Front of Camera")
    st.info("System will automatically recognize your face and mark attendance. No clicking on names.")

    run = st.checkbox("Start Camera")
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)

    db = load_db()
    if not db:
        st.warning("No students registered yet. Go to Register.")

    while run:
        ret, frame = camera.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        if FACE_LIB and db:
            face_locs = face_recognition.face_locations(rgb_small)
            face_encs = face_recognition.face_encodings(rgb_small, face_locs)

            for enc, loc in zip(face_encs, face_locs):
                matches = face_recognition.compare_faces([v["encoding"] for v in db.values()], enc, tolerance=0.5)
                if True in matches:
                    idx = matches.index(True)
                    roll = list(db.keys())[idx]
                    name = db[roll]["name"]

                    # Mark attendance
                    now = datetime.now()
                    date = now.strftime("%d/%m/%Y")
                    time = now.strftime("%I:%M:%S %p")
                    df = pd.read_csv(ATTEND_FILE)
                    if not ((df["roll"].astype(str)==str(roll)) & (df["date"]==date)).any():
                        pd.DataFrame([[roll,name,date,time,"Present"]], columns=["roll","name","date","time","status"]).to_csv(ATTEND_FILE, mode='a', header=False, index=False)
                        st.toast(f"✅ Marked: {name}")

                    # Draw box
                    y1,x2,y2,x1 = loc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                    cv2.putText(frame, name, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        FRAME_WINDOW.image(frame, channels="BGR")

    camera.release()

# 3. VIEW
else:
    st.header("📋 Attendance Sheet")
    df = pd.read_csv(ATTEND_FILE)
    st.dataframe(df.iloc[::-1], use_container_width=True)
    st.download_button("Export CSV", df.to_csv(index=False), "attendance.csv")
