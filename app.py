from collections import Counter
from datetime import date, datetime, time
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import query, close_db

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.teardown_appcontext(close_db)

with app.app_context():
    from database import init_db
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print("Database initialization error:", e)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
PERIODS = ['P1', 'P2', 'BREAK', 'P3', 'P4', 'LUNCH', 'P5', 'P6']
ACADEMIC_PERIODS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']

SUBJECT_DISTRIBUTION = {
    1: {
        'Software Engineering': 4,
        'Compiler Design': 4,
        'Information Security': 4,
        'DevOps': 4,
        'Startup and Entrepreneurship': 3,
        'Technical Seminar': 2,
        'Library': 1,
        'Sports': 1,
        'Self Learning': 1,
        'Mentoring': 1,
        'CRT': 5,
        'Software Engineering Lab': 2,
        'Information Security Lab': 2,
        'Compiler Design Lab': 2
    },
    2: {
        'Software Engineering': 4,
        'Compiler Design': 4,
        'Information Security': 4,
        'DevOps': 4,
        'Startup and Entrepreneurship': 3,
        'Technical Seminar': 2,
        'Library': 1,
        'Sports': 1,
        'Self Learning': 1,
        'Mentoring': 1,
        'CRT': 5,
        'Software Engineering Lab': 2,
        'Information Security Lab': 2,
        'Compiler Design Lab': 2
    },
    3: {
        'Software Engineering': 4,
        'Compiler Design': 4,
        'Information Security': 4,
        'Cloud Computing': 4,
        'Startup and Entrepreneurship': 3,
        'Technical Seminar': 2,
        'Library': 1,
        'Sports': 1,
        'Self Learning': 1,
        'Mentoring': 1,
        'CRT': 5,
        'Software Engineering Lab': 2,
        'Information Security Lab': 2,
        'Compiler Design Lab': 2
    }
}


LAB_SUBJECTS = ['Software Engineering Lab', 'Information Security Lab', 'Compiler Design Lab']
HIDE_FACULTY_SUBJECTS = [
    'CRT',
    'Library',
    'Sports',
    'Self Learning',
    'Mentoring',
    'BREAK',
    'LUNCH'
]
LAB_CONSECUTIVE = [('P1','P2'), ('P3','P4'), ('P5','P6')]
THEORY_ROOMS = ['A101', 'A102', 'A103']
LAB_ROOMS = ['LAB-1', 'LAB-2', 'LAB-3']
PERIOD_TIMES = {
    'P1': (time(9, 30), time(10, 20)),
    'P2': (time(10, 20), time(11, 10)),
    'P3': (time(11, 25), time(12, 15)),
    'P4': (time(12, 15), time(13, 5)),
    'P5': (time(13, 50), time(14, 40)),
    'P6': (time(14, 40), time(15, 30)),
}
DAY_INDEX = {day: index for index, day in enumerate(DAYS)}


def current_day_name():
    today = date.today().strftime('%A')
    return today if today in DAYS else 'Monday'
    


def build_timetable_grid(entries):
    timetable = {day: {period: None for period in PERIODS} for day in DAYS}
    for day in DAYS:
        timetable[day]['BREAK'] = {'subject_name': 'BREAK', 'faculty_name': '', 'room_no': '', 'subject_type': 'Break'}
        timetable[day]['LUNCH'] = {'subject_name': 'LUNCH', 'faculty_name': '', 'room_no': '', 'subject_type': 'Break'}
    for entry in entries:
        if entry['day'] in timetable and entry['period'] in timetable[entry['day']]:
            timetable[entry['day']][entry['period']] = entry
    return timetable


def current_and_next_class(entries, today_name):
    now = datetime.now().time()
    today_entries = sorted(
        [entry for entry in entries if entry['day'] == today_name],
        key=lambda item: ACADEMIC_PERIODS.index(item['period']) if item['period'] in ACADEMIC_PERIODS else 99
    )
    current_class = None
    next_class = None
    for entry in today_entries:
        start, end = PERIOD_TIMES.get(entry['period'], (None, None))
        if start and end and start <= now <= end:
            current_class = entry
        elif start and start > now and next_class is None:
            next_class = entry
    if next_class is None:
        upcoming = sorted(
            [entry for entry in entries if DAY_INDEX.get(entry['day'], 99) > DAY_INDEX.get(today_name, 99)],
            key=lambda item: (DAY_INDEX.get(item['day'], 99), ACADEMIC_PERIODS.index(item['period']))
        )
        next_class = upcoming[0] if upcoming else None
    return current_class, next_class


def active_announcements(role, section_id=None):
    params = [role]
    section_filter = ''
    if section_id:
        section_filter = ' OR target_section_id = %s'
        params.append(section_id)
    return query(
        f'''SELECT * FROM notifications
            WHERE is_active = TRUE
              AND (target_role IS NULL OR target_role = %s{section_filter})
            ORDER BY created_at DESC
            LIMIT 5''',
        tuple(params),
        fetchall=True
    )


@app.route('/')
def home():
    if session.get('admin_id'):
        return redirect(url_for('admin_dashboard'))
    if session.get('teacher_id'):
        return redirect(url_for('faculty_dashboard'))
    if session.get('student_id'):
        return redirect(url_for('student_dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'admin':
            username = request.form['username']
            password = request.form['password']
            admin = query('SELECT * FROM admins WHERE username = %s', (username,), fetchone=True)
            if admin and admin['password'] == password:
                session['admin_id'] = admin['admin_id']
                session['admin_username'] = admin['username']
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials', 'danger')
        elif user_type == 'faculty':
            employee_id = request.form['employee_id']
            password = request.form['password']
            teacher = query('SELECT * FROM teachers WHERE employee_id = %s', (employee_id,), fetchone=True)
            if teacher and check_password_hash(teacher['password'], password):
                session['teacher_id'] = teacher['teacher_id']
                session['teacher_name'] = teacher['teacher_name']
                return redirect(url_for('faculty_dashboard'))
            flash('Invalid faculty credentials', 'danger')
        else:
            roll_number = request.form['roll_number']
            password = request.form['password']
            student = query('SELECT * FROM students WHERE roll_number = %s', (roll_number,), fetchone=True)
            if student and check_password_hash(student['password'], password):
                session['student_id'] = student['roll_number']
                session['roll_number'] = student['roll_number']
                session['section_id'] = student['section_id']
                return redirect(url_for('student_dashboard'))
            flash('Invalid student credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    teacher_count = query('SELECT COUNT(*) AS count FROM teachers WHERE is_active = TRUE', fetchone=True)['count']
    student_count = query('SELECT COUNT(*) AS count FROM students', fetchone=True)['count']
    room_count = query('SELECT COUNT(*) AS count FROM rooms WHERE is_active = TRUE', fetchone=True)['count']
    subject_count = query('SELECT COUNT(*) AS count FROM subjects', fetchone=True)['count']
    section_count = query('SELECT COUNT(*) AS count FROM sections', fetchone=True)['count']
    section_counts = query('SELECT section_name, student_count FROM sections ORDER BY section_name', fetchall=True)
    return render_template('admin_dashboard.html', teacher_count=teacher_count, student_count=student_count,
                           room_count=room_count, subject_count=subject_count, section_count=section_count,
                           section_counts=section_counts)


@app.route('/faculty')
def faculty_dashboard():
    if not session.get('teacher_id'):
        return redirect(url_for('login'))
    teacher = query('SELECT * FROM teachers WHERE teacher_id = %s', (session['teacher_id'],), fetchone=True)
    workload = query(
        'SELECT COUNT(*) AS count FROM timetable WHERE faculty_name = %s',
        (teacher['teacher_name'],),
        fetchone=True
    )
    # Get timetable entries for the faculty
    my_timetable = query(
        '''SELECT t.*, sec.section_name 
           FROM timetable t 
           JOIN sections sec ON t.section_id = sec.section_id 
           WHERE t.faculty_name = %s 
           ORDER BY t.day, t.period''',
        (teacher['teacher_name'],),
        fetchall=True
    )
    real_today = date.today().strftime('%A')
    today_name = current_day_name()

    if real_today == 'Sunday':
        current_class = None
        today_classes = []

        upcoming = sorted(
            my_timetable,
            key=lambda item: (
                DAY_INDEX.get(item['day'], 99),
                ACADEMIC_PERIODS.index(item['period'])
            )
        )

        next_class = upcoming[0] if upcoming else None

    else:
        current_class, next_class = current_and_next_class(my_timetable, today_name)
        today_classes = [entry for entry in my_timetable if entry['day'] == today_name]

    weekly_timetable = build_timetable_grid(my_timetable)
    announcements = active_announcements('faculty')
    return render_template(
        'faculty_dashboard.html',
        teacher=teacher,
        workload=workload['count'],
        weekly_load=workload['count'],
        my_timetable=my_timetable,
        weekly_timetable=weekly_timetable,
        today_classes=today_classes,
        current_class=current_class,
        next_class=next_class,
        announcements=announcements,
        days=DAYS,
        periods=PERIODS
    )


@app.route('/faculty/update-availability', methods=['POST'])
def update_availability():
    if not session.get('teacher_id'):
        return redirect(url_for('login'))
    status = request.form.get('status')
    if status in ['Available', 'On Leave', 'Unavailable']:
        query(
            'UPDATE teachers SET availability_status = %s WHERE teacher_id = %s',
            (status, session['teacher_id']),
            commit=True
        )
        flash(f'Availability status updated to {status}', 'success')
    else:
        flash('Invalid status', 'danger')
    return redirect(url_for('faculty_dashboard'))


@app.route('/student')
def student_dashboard():
    if not session.get('student_id'):
        return redirect(url_for('login'))
    student = query(
        'SELECT s.*, sec.section_name, sec.semester FROM students s JOIN sections sec ON s.section_id = sec.section_id WHERE s.roll_number = %s',
        (session['roll_number'],),
        fetchone=True
    )
    timetable_entries = query('SELECT * FROM timetable WHERE section_id = %s ORDER BY day, period', (student['section_id'],), fetchall=True)
    timetable = build_timetable_grid(timetable_entries)
    real_today = date.today().strftime('%A')
    today_name = current_day_name()
    if real_today == 'Sunday':
        today_schedule = []
        current_class = None
        next_class = None
    else:
        today_schedule = [entry for entry in timetable_entries if entry['day'] == today_name]
    current_class, next_class = current_and_next_class(timetable_entries, today_name)
    announcements = active_announcements('student', student['section_id'])
    academic_calendar = query(
        'SELECT * FROM academic_calendar WHERE semester = %s ORDER BY start_date LIMIT 6',
        (student.get('semester') or 'SEM-VI',),
        fetchall=True
    )
    return render_template(
        'student_dashboard.html',
        student=student,
        timetable=timetable,
        days=DAYS,
        periods=PERIODS,
        today_schedule=today_schedule,
        current_class=current_class,
        next_class=next_class,
        announcements=announcements,
        academic_calendar=academic_calendar
    )


@app.route('/teachers')
def view_teachers():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    teachers = query('SELECT * FROM teachers ORDER BY employee_id', fetchall=True)
    return render_template('teachers.html', teachers=teachers)


@app.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        teacher_name = request.form['teacher_name']
        department = request.form['department']
        specialization = request.form['specialization']
        password = generate_password_hash(request.form['password'])
        max_hours = int(request.form['max_hours_per_week'])
        availability_status = request.form['availability_status']
        query('INSERT INTO teachers (employee_id, teacher_name, department, specialization, password, max_hours_per_week, availability_status) VALUES (%s, %s, %s, %s, %s, %s, %s)',
              (employee_id, teacher_name, department, specialization, password, max_hours, availability_status), commit=True)
        return redirect(url_for('view_teachers'))
    return render_template('add_teacher.html')


@app.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    teacher = query('SELECT * FROM teachers WHERE teacher_id = %s', (teacher_id,), fetchone=True)
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        teacher_name = request.form['teacher_name']
        department = request.form['department']
        specialization = request.form['specialization']
        max_hours = int(request.form['max_hours_per_week'])
        availability_status = request.form['availability_status']
        if request.form.get('password'):
            password = generate_password_hash(request.form['password'])
            query('UPDATE teachers SET employee_id = %s, teacher_name = %s, department = %s, specialization = %s, password = %s, max_hours_per_week = %s, availability_status = %s WHERE teacher_id = %s',
                  (employee_id, teacher_name, department, specialization, password, max_hours, availability_status, teacher_id), commit=True)
        else:
            query('UPDATE teachers SET employee_id = %s, teacher_name = %s, department = %s, specialization = %s, max_hours_per_week = %s, availability_status = %s WHERE teacher_id = %s',
                  (employee_id, teacher_name, department, specialization, max_hours, availability_status, teacher_id), commit=True)
        return redirect(url_for('view_teachers'))
    return render_template('edit_teacher.html', teacher=teacher)


@app.route('/teachers/delete/<int:teacher_id>')
def delete_teacher(teacher_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    query('DELETE FROM teachers WHERE teacher_id = %s', (teacher_id,), commit=True)
    return redirect(url_for('view_teachers'))


@app.route('/students')
def view_students():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    students = query('SELECT s.*, sec.section_name FROM students s JOIN sections sec ON s.section_id = sec.section_id ORDER BY s.roll_number', fetchall=True)
    sections = query('SELECT * FROM sections ORDER BY section_name', fetchall=True)
    return render_template('students.html', students=students, sections=sections)


@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    sections = query('SELECT * FROM sections ORDER BY section_name', fetchall=True)
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        password = generate_password_hash(request.form['password'])
        section_id = int(request.form['section_id'])
        query('INSERT INTO students (roll_number, password, section_id) VALUES (%s, %s, %s)',
              (roll_number, password, section_id), commit=True)
        return redirect(url_for('view_students'))
    return render_template('add_student.html', sections=sections)


@app.route('/students/edit/<string:roll_number>', methods=['GET', 'POST'])
def edit_student(roll_number):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    student = query('SELECT * FROM students WHERE roll_number = %s', (roll_number,), fetchone=True)
    sections = query('SELECT * FROM sections ORDER BY section_name', fetchall=True)
    if request.method == 'POST':
        section_id = int(request.form['section_id'])
        if request.form.get('password'):
            password = generate_password_hash(request.form['password'])
            query('UPDATE students SET password = %s, section_id = %s WHERE roll_number = %s',
                  (password, section_id, roll_number), commit=True)
        else:
            query('UPDATE students SET section_id = %s WHERE roll_number = %s',
                  (section_id, roll_number), commit=True)
        return redirect(url_for('view_students'))
    return render_template('edit_student.html', student=student, sections=sections)


@app.route('/students/delete/<string:roll_number>')
def delete_student(roll_number):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    query('DELETE FROM students WHERE roll_number = %s', (roll_number,), commit=True)
    return redirect(url_for('view_students'))


@app.route('/rooms')
def view_rooms():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    rooms = query('SELECT * FROM rooms ORDER BY room_no', fetchall=True)
    return render_template('rooms.html', rooms=rooms)


@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        room_no = request.form['room_no']
        building = request.form['building']
        floor_no = int(request.form['floor_no'])
        capacity = int(request.form['capacity'])
        room_type = request.form['room_type']
        equipment = request.form['equipment']
        is_active = request.form.get('is_active') == 'on'
        query('INSERT INTO rooms (room_no, building, floor_no, capacity, room_type, equipment, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s)',
              (room_no, building, floor_no, capacity, room_type, equipment, is_active), commit=True)
        return redirect(url_for('view_rooms'))
    return render_template('add_room.html')


@app.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    room = query('SELECT * FROM rooms WHERE room_id = %s', (room_id,), fetchone=True)
    if request.method == 'POST':
        room_no = request.form['room_no']
        building = request.form['building']
        floor_no = int(request.form['floor_no'])
        capacity = int(request.form['capacity'])
        room_type = request.form['room_type']
        equipment = request.form['equipment']
        is_active = request.form.get('is_active') == 'on'
        query('UPDATE rooms SET room_no = %s, building = %s, floor_no = %s, capacity = %s, room_type = %s, equipment = %s, is_active = %s WHERE room_id = %s',
              (room_no, building, floor_no, capacity, room_type, equipment, is_active, room_id), commit=True)
        return redirect(url_for('view_rooms'))
    return render_template('edit_room.html', room=room)


@app.route('/rooms/delete/<int:room_id>')
def delete_room(room_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    query('DELETE FROM rooms WHERE room_id = %s', (room_id,), commit=True)
    return redirect(url_for('view_rooms'))


@app.route('/subjects')
def view_subjects():
    if not session.get('admin_id'):
        return redirect(url_for('login'))

    subjects = query(
    '''
    SELECT DISTINCT

        ssf.subject_name,
        sub.subject_type,
        ssf.faculty_name,
        sub.semester,
        sec.section_name,
        sub.hours_per_week
    FROM section_subject_faculty ssf
    JOIN sections sec
        ON ssf.section_id = sec.section_id
    JOIN subjects sub
        ON ssf.subject_name = sub.subject_name
    ORDER BY
        CASE
            WHEN ssf.subject_name IN
            ('CRT','Library','Sports','Mentoring','Self Learning')
            THEN 1
            ELSE 0
        END,
        ssf.subject_name,
        sec.section_name
    ''',
    fetchall=True
    )

    teachers = query(
        'SELECT teacher_name FROM teachers ORDER BY teacher_name',
        fetchall=True
    )

    return render_template(
        'subjects.html',
        subjects=subjects,
        teachers=teachers
    )

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    teachers = query('SELECT teacher_name FROM teachers ORDER BY teacher_name', fetchall=True)
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        subject_type = request.form['subject_type']
        faculty_name = request.form['faculty_name']
        semester = request.form['semester']
        hours_per_week = int(request.form['hours_per_week'])
        query('INSERT INTO subjects (subject_name, subject_type, faculty_name, semester, hours_per_week) VALUES (%s, %s, %s, %s, %s)',
              (subject_name, subject_type, faculty_name, semester, hours_per_week), commit=True)
        return redirect(url_for('view_subjects'))
    return render_template('add_subject.html', teachers=teachers)


@app.route('/subjects/edit/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    subject = query('SELECT * FROM subjects WHERE subject_id = %s', (subject_id,), fetchone=True)
    teachers = query('SELECT teacher_name FROM teachers ORDER BY teacher_name', fetchall=True)
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        subject_type = request.form['subject_type']
        faculty_name = request.form['faculty_name']
        semester = request.form['semester']
        hours_per_week = int(request.form['hours_per_week'])
        query('UPDATE subjects SET subject_name = %s, subject_type = %s, faculty_name = %s, semester = %s, hours_per_week = %s WHERE subject_id = %s',
              (subject_name, subject_type, faculty_name, semester, hours_per_week, subject_id), commit=True)
        return redirect(url_for('view_subjects'))
    return render_template('edit_subject.html', subject=subject, teachers=teachers)


@app.route('/subjects/delete/<int:subject_id>')
def delete_subject(subject_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    query('DELETE FROM subjects WHERE subject_id = %s', (subject_id,), commit=True)
    return redirect(url_for('view_subjects'))


@app.route('/timetable/generate', methods=['GET', 'POST'])
def generate_timetable():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    sections = query('SELECT * FROM sections ORDER BY section_name', fetchall=True)
    teachers = query('SELECT * FROM teachers WHERE is_active = TRUE ORDER BY teacher_name', fetchall=True)
    rooms = query('SELECT * FROM rooms WHERE is_active = TRUE ORDER BY room_no', fetchall=True)
    if request.method == 'POST':
        section_id = int(request.form['section_id'])
        populate_timetable_for_section(section_id)
        return redirect(url_for('view_timetable', section_id=section_id))
    return render_template('generate_timetable.html', sections=sections, teachers=teachers, rooms=rooms)


def populate_timetable_for_section(section_id):
    import random

    query('DELETE FROM timetable WHERE section_id = %s', (section_id,), commit=True)
    section = query(
        'SELECT * FROM sections WHERE section_id = %s',
        (section_id,),
        fetchone=True
    )
    subject_counts = SUBJECT_DISTRIBUTION.get(section_id, {}).copy()
    faculty_rows = query(
    '''
    SELECT subject_name, faculty_name
    FROM section_subject_faculty
    WHERE section_id = %s
    ''',
    (section_id,),
    fetchall=True
    )
    subject_teachers = {
        row['subject_name']: row['faculty_name']
        for row in faculty_rows
    }
    subject_teachers['Library'] = ''
    subject_teachers['Sports'] = ''
    subject_teachers['Self Learning'] = ''
    subject_teachers['Mentoring'] = ''
    subject_teachers['CRT'] = ''
    NO_FACULTY_SUBJECTS = {
    'Library',
    'Sports',
    'Self Learning',
    'Mentoring',
    'CRT'
    }

    missing_faculty = [
        subject for subject in subject_counts
        if subject not in NO_FACULTY_SUBJECTS
        and not subject_teachers.get(subject)
    ]
    if missing_faculty:
        flash('Cannot generate timetable. Missing faculty assignment for: ' + ', '.join(missing_faculty), 'danger')
        return

    existing_entries = query(
        'SELECT faculty_name, room_no, day, period FROM timetable WHERE section_id <> %s',
        (section_id,),
        fetchall=True
    )

    assigned_table = None
    for _ in range(250):
        random.seed()
        trial_table = {day: {period: None for period in ACADEMIC_PERIODS} for day in DAYS}
        teacher_assignments = {}
        room_assignments = {}
        subject_slots_per_day = {day: Counter() for day in DAYS}
        for entry in existing_entries:
            teacher_assignments.setdefault(entry['faculty_name'], set()).add((entry['day'], entry['period']))
            room_assignments.setdefault(entry['room_no'], set()).add((entry['day'], entry['period']))

        remaining_counts = subject_counts.copy()
        valid = True

        lab_subjects = [subject for subject in LAB_SUBJECTS if subject in remaining_counts]
        random.shuffle(lab_subjects)
        for subject in lab_subjects:
            faculty = subject_teachers.get(subject, 'Lab Faculty')
            if allocate_lab(subject, remaining_counts[subject], trial_table, teacher_assignments, room_assignments, subject_slots_per_day, faculty):
                del remaining_counts[subject]
            else:
                valid = False
                break

        if valid and 'CRT' in remaining_counts:
            faculty = None
            if allocate_crt(
                remaining_counts['CRT'],
                trial_table,
                teacher_assignments,
                room_assignments,
                subject_slots_per_day,
                faculty
        ):
                del remaining_counts['CRT']
            else:
                valid = False
        regular_subjects = list(remaining_counts.items())
        random.shuffle(regular_subjects)
        for subject, count in regular_subjects:
            faculty = subject_teachers.get(subject)
            if subject in NO_FACULTY_SUBJECTS:
                faculty = f"{subject}_AUTO"
            if not allocate_regular(subject, count, trial_table, teacher_assignments, room_assignments, subject_slots_per_day, faculty, section['room_no']):
                valid = False
                break

        saturday_has_class = any(trial_table['Saturday'][period] for period in ACADEMIC_PERIODS)
        all_slots_filled = all(trial_table[day][period] for day in DAYS for period in ACADEMIC_PERIODS)
        if valid and saturday_has_class:
            assigned_table = trial_table
            break

    if assigned_table is None:
        flash('Unable to generate a valid timetable with the current room/faculty constraints. Please try again.', 'danger')
        return

    for day in DAYS:
        for period in ACADEMIC_PERIODS:
            cell = assigned_table[day][period]
            if cell:
                query('INSERT INTO timetable (section_id, day, period, subject_name, faculty_name, room_no, subject_type) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                      (section_id, day, period, cell['subject_name'], cell['faculty_name'], cell['room_no'], cell.get('subject_type', 'Theory')), commit=True)


def choose_room(room_choices, room_assignments, day, period):
    import random
    rooms = list(room_choices)
    random.shuffle(rooms)
    for room in rooms:
        if (day, period) not in room_assignments.get(room, set()):
            return room
    return None


def can_place(faculty, room, day, periods, assigned_table, teacher_assignments, room_assignments):
    if any(assigned_table[day][period] is not None for period in periods):
        return False
    if faculty and any((day, period) in teacher_assignments.get(faculty, set()) for period in periods):
        return False
    if room and any((day, period) in room_assignments.get(room, set()) for period in periods):
        return False
    return True


def place_periods(subject, faculty, room, day, periods, subject_type, assigned_table, teacher_assignments, room_assignments, subject_slots_per_day):
    if subject == 'CRT':
        faculty_name = 'CRT'
    else:
        faculty_name = faculty or ''

    for period in periods:
        assigned_table[day][period] = {
            'subject_name': subject,
            'faculty_name': faculty_name,
            'room_no': room,
            'subject_type': subject_type
        }
        if faculty_name:
            teacher_assignments.setdefault(
                faculty_name, set()
            ).add((day, period))

        room_assignments.setdefault(
            room, set()
        ).add((day, period))

    subject_slots_per_day[day][subject] += len(periods)
        

def allocate_regular(subject, count, assigned_table, teacher_assignments, room_assignments, subject_slots_per_day, faculty, section_room):
    """Allocate theory subjects with at most two occurrences per day."""
    if not faculty:
        return False

    placed = 0
    import random

    while placed < count:
        candidates = []
        for day in DAYS:
            if subject_slots_per_day[day][subject] >= 2:
                continue
            for period in ACADEMIC_PERIODS:
                room_choices = [section_room] if section_room in THEORY_ROOMS else THEORY_ROOMS
                room = choose_room(room_choices, room_assignments, day, period)
                if room and can_place(faculty, room, day, [period], assigned_table, teacher_assignments, room_assignments):
                    daily_count = subject_slots_per_day[day][subject]
                    candidates.append((daily_count, day, period, room))
        if not candidates:
            return False
        min_daily = min(candidate[0] for candidate in candidates)
        preferred = [candidate for candidate in candidates if candidate[0] == min_daily]
        _, day, period, room = random.choice(preferred)
        place_periods(subject, faculty, room, day, [period], 'Theory', assigned_table, teacher_assignments, room_assignments, subject_slots_per_day)
        placed += 1
    return placed == count


def allocate_lab(subject, count, assigned_table, teacher_assignments, room_assignments, subject_slots_per_day, faculty):
    """Allocate one double-period lab session for every two weekly lab periods."""
    if not faculty:
        return False

    import random
    sessions_needed = max(1, count // 2)
    placed = 0

    while placed < sessions_needed:
        candidates = []
        for day in DAYS:
            if any(entry and entry.get('subject_type') == 'Lab' for entry in assigned_table[day].values()):
                continue
            if subject_slots_per_day[day][subject]:
                continue
            for periods in LAB_CONSECUTIVE:
                room = choose_room(LAB_ROOMS, room_assignments, day, periods[0])
                if room and can_place(faculty, room, day, periods, assigned_table, teacher_assignments, room_assignments):
                    if all((day, period) not in room_assignments.get(room, set()) for period in periods):
                        candidates.append((day, periods, room))
        if not candidates:
            return False
        day, periods, room = random.choice(candidates)
        place_periods(subject, faculty, room, day, periods, 'Lab', assigned_table, teacher_assignments, room_assignments, subject_slots_per_day)
        placed += 1
    return True


def allocate_crt(count, assigned_table, teacher_assignments,
                 room_assignments, subject_slots_per_day, faculty):
    """
    CRT = exactly 5 periods/week
    Day 1 -> 2 consecutive periods
    Day 2 -> 3 consecutive periods
    """

    if count != 5:
        return False

    if not faculty:
        faculty = None

    import random

    two_period_patterns = [
        ('P1', 'P2'),
        ('P2', 'P3'),
        ('P3', 'P4'),
        ('P4', 'P5'),
        ('P5', 'P6')
    ]

    three_period_patterns = [
        ('P1', 'P2', 'P3'),
        ('P2', 'P3', 'P4'),
        ('P3', 'P4', 'P5'),
        ('P4', 'P5', 'P6')
    ]

    days = DAYS[:]
    random.shuffle(days)

    for first_day in days:

        two_candidates = []

        for periods in two_period_patterns:
            room = choose_room(
                THEORY_ROOMS,
                room_assignments,
                first_day,
                periods[0]
            )

            if room and can_place(
                faculty,
                room,
                first_day,
                periods,
                assigned_table,
                teacher_assignments,
                room_assignments
            ):
                two_candidates.append((periods, room))

        if not two_candidates:
            continue

        two_periods, two_room = random.choice(two_candidates)

        snapshot_table = {
            day: assigned_table[day].copy()
            for day in DAYS
        }
        snapshot_teachers = {
            k: v.copy()
            for k, v in teacher_assignments.items()
        }
        snapshot_rooms = {
            k: v.copy()
            for k, v in room_assignments.items()
        }
        snapshot_subjects = {
            day: counts.copy()
            for day, counts in subject_slots_per_day.items()
        }

        place_periods(
            'CRT',
            faculty,
            two_room,
            first_day,
            two_periods,
            'Theory',
            assigned_table,
            teacher_assignments,
            room_assignments,
            subject_slots_per_day
        )

        remaining_days = [d for d in DAYS if d != first_day]
        random.shuffle(remaining_days)

        for second_day in remaining_days:

            three_candidates = []

            for periods in three_period_patterns:
                room = choose_room(
                    THEORY_ROOMS,
                    room_assignments,
                    second_day,
                    periods[0]
                )

                if room and can_place(
                    faculty,
                    room,
                    second_day,
                    periods,
                    assigned_table,
                    teacher_assignments,
                    room_assignments
                ):
                    three_candidates.append((periods, room))

            if three_candidates:

                three_periods, three_room = random.choice(three_candidates)

                place_periods(
                    'CRT',
                    faculty,
                    three_room,
                    second_day,
                    three_periods,
                    'Theory',
                    assigned_table,
                    teacher_assignments,
                    room_assignments,
                    subject_slots_per_day
                )

                return True

        assigned_table.clear()
        assigned_table.update(snapshot_table)

        teacher_assignments.clear()
        teacher_assignments.update(snapshot_teachers)

        room_assignments.clear()
        room_assignments.update(snapshot_rooms)

        subject_slots_per_day.clear()
        subject_slots_per_day.update(snapshot_subjects)

    return False
def room_conflict(room_assignments, day, period):
    """Check if room already assigned to this slot"""
    return (day, period) in room_assignments.get('default_room', [])


@app.route('/timetable/<int:section_id>')
def view_timetable(section_id):
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    timetable_entries = query('SELECT * FROM timetable WHERE section_id = %s ORDER BY day, period', (section_id,), fetchall=True)
    timetable = build_timetable_grid(timetable_entries)
    section = query('SELECT * FROM sections WHERE section_id = %s', (section_id,), fetchone=True)
    return render_template('view_timetable.html', timetable=timetable, days=DAYS, periods=PERIODS, section=section)

@app.route('/timetables')
def all_timetables():

    if not session.get('admin_id'):
        return redirect(url_for('login'))

    sections = query(
        'SELECT * FROM sections ORDER BY section_name',
        fetchall=True
    )

    return render_template(
        'all_timetables.html',
        sections=sections
    )

@app.route('/reports')
def reports():
    if not session.get('admin_id'):
        return redirect(url_for('login'))
    teacher_loads = query(
        '''SELECT faculty_name, COUNT(*) AS assigned_hours
           FROM timetable
           GROUP BY faculty_name
           ORDER BY faculty_name''',
        fetchall=True
    )
    room_usage = query(
        '''SELECT room_no, COUNT(*) AS usage_count
           FROM timetable
           GROUP BY room_no
           ORDER BY room_no''',
        fetchall=True
    )
    subject_coverage = query(
        '''SELECT subject_name, COUNT(*) AS sessions
           FROM timetable
           GROUP BY subject_name
           ORDER BY subject_name''',
        fetchall=True
    )
    student_counts = query(
        '''SELECT sec.section_name, sec.student_count, COUNT(s.roll_number) AS seeded_students
           FROM sections sec
           LEFT JOIN students s ON s.section_id = sec.section_id
           GROUP BY sec.section_id, sec.section_name, sec.student_count
           ORDER BY sec.section_name''',
        fetchall=True
    )
    faculty_count = query('SELECT COUNT(*) AS count FROM teachers WHERE is_active = TRUE', fetchone=True)['count']
    room_conflicts = query(
        '''SELECT day, period, room_no, COUNT(*) AS conflict_count
           FROM timetable
           GROUP BY day, period, room_no
           HAVING COUNT(*) > 1
           ORDER BY day, period, room_no''',
        fetchall=True
    )
    faculty_conflicts = query(
        '''SELECT day, period, faculty_name, COUNT(*) AS conflict_count
           FROM timetable
           GROUP BY day, period, faculty_name
           HAVING COUNT(*) > 1
           ORDER BY day, period, faculty_name''',
        fetchall=True
    )
    section_conflicts = query(
        '''SELECT day, period, section_id, COUNT(*) AS conflict_count
           FROM timetable
           GROUP BY day, period, section_id
           HAVING COUNT(*) > 1
           ORDER BY day, period, section_id''',
        fetchall=True
    )
    return render_template(
        'reports.html',
        teacher_loads=teacher_loads,
        room_usage=room_usage,
        subject_coverage=subject_coverage,
        student_counts=student_counts,
        faculty_count=faculty_count,
        room_conflicts=room_conflicts,
        faculty_conflicts=faculty_conflicts,
        section_conflicts=section_conflicts
    )




if __name__ == '__main__':
    app.run(debug=True)
