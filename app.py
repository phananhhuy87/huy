# ======================================
# WEBSITE ĐIỂM DANH (Flask + MySQL + Bootstrap)
# ======================================

from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='diemdanh'
    )

# ================= LOGIN =================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user
            return redirect('/classes')

    return render_template('login.html')

# ================= CLASSES =================
@app.route('/classes')
def classes():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT class_name FROM students")
    classes = [c[0] for c in cursor.fetchall()]
    return render_template('classes.html', classes=classes)

# ================= ĐIỂM DANH =================
@app.route('/class/<class_name>', methods=['GET', 'POST'])
def attendance(class_name):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        date = request.form['date']
        absent = request.form.getlist('absent')

        cursor.execute("SELECT * FROM students WHERE class_name=%s", (class_name,))
        students = cursor.fetchall()

        for s in students:
            status = 'Vắng' if str(s['stt']) in absent else 'Có mặt'
            cursor.execute("INSERT INTO attendance(student_id, date, status) VALUES(%s,%s,%s)", (s['id'], date, status))

        db.commit()

    cursor.execute("SELECT * FROM students WHERE class_name=%s", (class_name,))
    students = cursor.fetchall()

    return render_template('class.html', class_name=class_name, students=students)

# ================= REPORT =================
@app.route('/report')
def report():
    db = get_db()
    df = pd.read_sql("SELECT s.class_name, s.name, a.date, a.status FROM attendance a JOIN students s ON a.student_id=s.id WHERE a.status='Vắng'", db)
    return render_template('report.html', tables=df.to_dict('records'))

# ================= EXPORT =================
@app.route('/export')
def export():
    db = get_db()
    df = pd.read_sql("SELECT s.class_name, s.name, a.date, a.status FROM attendance a JOIN students s ON a.student_id=s.id", db)
    df.to_excel('report.xlsx', index=False)
    return "Đã xuất file report.xlsx"

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)






# ======================================
# templates/report.html
# ======================================
"""
<!DOCTYPE html>
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-4">
<h3>Báo cáo học sinh vắng</h3>
<table class="table table-striped">
<tr><th>Lớp</th><th>Tên</th><th>Ngày</th><th>Trạng thái</th></tr>
{% for r in tables %}
<tr>
<td>{{r.class_name}}</td>
<td>{{r.name}}</td>
<td>{{r.date}}</td>
<td>{{r.status}}</td>
</tr>
{% endfor %}
</table>
<a href="/export" class="btn btn-success">Xuất Excel</a>
</div>
</body>
</html>
"""
