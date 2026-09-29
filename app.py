from flask import Flask, render_template_string, request, jsonify
import csv, os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "attendance.csv"
STUDENT_FILE = "students.csv"

# Create files if not exist
if not os.path.exists(STUDENT_FILE):
    with open(STUDENT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["roll","name"])
        writer.writerows([["101","Aarav Sharma"],["102","Priya Patel"],["103","Rahul Verma"]])

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        csv.writer(f).writerow(["roll","name","date","time","status"])

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>AttendSmart - AI Attendance</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:Segoe UI}
body{background:#f0f4ff}
.navbar{background:#4f46e5;color:white;padding:18px 30px;display:flex;justify-content:space-between}
.main{max-width:1100px;margin:20px auto;padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{background:white;padding:20px;border-radius:16px;box-shadow:0 8px 25px rgba(0,0,0,.08)}
#video{width:100%;height:280px;background:#000;border-radius:12px;object-fit:cover}
.btn{padding:12px;border:none;border-radius:10px;font-weight:600;cursor:pointer;width:100%;margin-top:10px}
.primary{background:#4f46e5;color:white}
input,select{width:100%;padding:11px;border:1px solid #ddd;border-radius:8px;margin:6px 0}
table{width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:10px;border-bottom:1px solid #eee;font-size:14px}
.badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700}
.present{background:#dcfce7;color:#166534}
.late{background:#fef9c3;color:#854d0e}
@media(max-width:800px){.main{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="navbar"><h1>🎓 AttendSmart AI</h1><span id="clock"></span></div>
<div class="main">
<div class="card">
<h2>📸 Live Scanner</h2>
<video id="video" autoplay muted playsinline></video>
<select id="select"></select>
<button class="btn primary" onclick="mark()">Mark Present</button>
<p id="msg" style="text-align:center;margin-top:10px;color:green;font-weight:600"></p>
<hr style="margin:20px 0">
<h3>Add Student</h3>
<input id="name" placeholder="Name"><input id="roll" placeholder="Roll No">
<button class="btn primary" onclick="addStudent()">Add Student</button>
</div>
<div class="card">
<h2>Today's Attendance</h2>
<table><thead><tr><th>Roll</th><th>Name</th><th>Time</th><th>Status</th></tr></thead><tbody id="table"></tbody></table>
</div>
</div>
<script>
let clock=setInterval(()=>document.getElementById('clock').innerText=new Date().toLocaleString(),1000);
navigator.mediaDevices.getUserMedia({video:true}).then(s=>video.srcObject=s);

async function loadStudents(){
 let res=await fetch('/get_students'); let data=await res.json();
 select.innerHTML=""; data.forEach(s=>{
  let o=document.createElement('option'); o.value=s.roll; o.text=s.roll+" - "+s.name; select.appendChild(o);
 });
}
async function loadAttendance(){
 let res=await fetch('/get_attendance'); let data=await res.json();
 let tbody=document.getElementById('table'); tbody.innerHTML="";
 data.forEach(a=>{
  tbody.innerHTML+=`<tr><td>${a.roll}</td><td>${a.name}</td><td>${a.time}</td><td><span class="badge ${a.status.toLowerCase()}">${a.status}</span></td></tr>`;
 });
}
async function addStudent(){
 let name=document.getElementById('name').value, roll=document.getElementById('roll').value;
 if(!name||!roll) return alert("Enter both");
 await fetch('/add_student',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,roll})});
 document.getElementById('name').value=""; document.getElementById('roll').value=""; loadStudents();
}
async function mark(){
 document.getElementById('msg').innerText="Scanning Face...";
 let roll=document.getElementById('select').value;
 let res=await fetch('/mark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({roll})});
 let d=await res.json();
 document.getElementById('msg').innerText=d.message;
 loadAttendance();
}
loadStudents(); loadAttendance();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/get_students')
def get_students():
    students=[]
    with open(STUDENT_FILE) as f:
        reader=csv.DictReader(f)
        for r in reader: students.append(r)
    return jsonify(students)

@app.route('/add_student', methods=['POST'])
def add_student():
    data=request.json
    with open(STUDENT_FILE, 'a', newline='') as f:
        csv.writer(f).writerow([data['roll'], data['name']])
    return jsonify({"ok":True})

@app.route('/get_attendance')
def get_attendance():
    today=datetime.now().strftime("%d/%m/%Y")
    rows=[]
    with open(DATA_FILE) as f:
        reader=csv.DictReader(f)
        for r in reader:
            if r['date']==today: rows.append(r)
    return jsonify(rows[::-1])

@app.route('/mark', methods=['POST'])
def mark():
    roll=request.json['roll']
    name="Unknown"
    with open(STUDENT_FILE) as f:
        for r in csv.DictReader(f):
            if r['roll']==roll: name=r['name']
    
    now=datetime.now()
    date=now.strftime("%d/%m/%Y")
    time=now.strftime("%I:%M:%S %p")
    status="Late" if now.hour>=10 else "Present"

    # Check duplicate
    with open(DATA_FILE) as f:
        for r in csv.DictReader(f):
            if r['roll']==roll and r['date']==date:
                return jsonify({"message": f"⚠️ {name} already marked today!"})

    with open(DATA_FILE, 'a', newline='') as f:
        csv.writer(f).writerow([roll,name,date,time,status])

    return jsonify({"message": f"✅ Attendance Marked: {name} at {time}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
