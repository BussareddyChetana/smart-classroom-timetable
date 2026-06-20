CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    teacher_name VARCHAR(150) NOT NULL,
    department VARCHAR(100),
    specialization VARCHAR(150),
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_hours_per_week INTEGER DEFAULT 16,
    availability_status VARCHAR(50) DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id SERIAL PRIMARY KEY,
    room_no VARCHAR(50) UNIQUE NOT NULL,
    building VARCHAR(100),
    floor_no INTEGER,
    capacity INTEGER,
    room_type VARCHAR(100),
    equipment VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(150) NOT NULL,
    subject_type VARCHAR(100),
    faculty_name VARCHAR(150),
    semester VARCHAR(50),
    hours_per_week INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sections (
    section_id SERIAL PRIMARY KEY,
    semester VARCHAR(50) NOT NULL,
    section_name VARCHAR(50) NOT NULL,
    student_count INTEGER DEFAULT 0,
    room_no VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS students (
    roll_number VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    section_id INTEGER NOT NULL REFERENCES sections(section_id)
);

CREATE TABLE IF NOT EXISTS timetable (
    id SERIAL PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES sections(section_id),
    day VARCHAR(20) NOT NULL,
    period VARCHAR(20) NOT NULL,
    subject_name VARCHAR(150) NOT NULL,
    faculty_name VARCHAR(150) NOT NULL,
    room_no VARCHAR(50) NOT NULL,
    subject_type VARCHAR(100),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    target_role VARCHAR(50),
    target_section_id INTEGER REFERENCES sections(section_id),
    created_by INTEGER REFERENCES admins(admin_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Room Booking Table
CREATE TABLE IF NOT EXISTS room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(room_id),
    faculty_id INTEGER NOT NULL REFERENCES teachers(teacher_id),
    booking_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    purpose VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Academic Calendar Table
CREATE TABLE IF NOT EXISTS academic_calendar (
    id SERIAL PRIMARY KEY,
    semester VARCHAR(50) NOT NULL,
    event_type VARCHAR(100),
    event_name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    description TEXT,
    is_holiday BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leave Requests Table
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(teacher_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    reviewed_by INTEGER REFERENCES admins(admin_id),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- User Notifications (Track Read Status)
CREATE TABLE IF NOT EXISTS user_notifications (
    id SERIAL PRIMARY KEY,
    notification_id INTEGER NOT NULL REFERENCES notifications(id),
    user_type VARCHAR(50),
    user_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP
);

INSERT INTO admins (username, password)
VALUES ('admin', 'admin123')
ON CONFLICT (username) DO NOTHING;

INSERT INTO sections (section_id, semester, section_name, student_count, room_no)
VALUES
    (1, 'SEM-VI', 'CSE-A', 64, 'B-402'),
    (2, 'SEM-VI', 'CSE-B', 63, 'B-403'),
    (3, 'SEM-VI', 'CSE-C', 65, 'B-404')
ON CONFLICT (section_id) DO UPDATE
SET student_count = EXCLUDED.student_count,
    room_no = EXCLUDED.room_no;

INSERT INTO teachers (employee_id, teacher_name, department, specialization, password, is_active, max_hours_per_week, availability_status)
VALUES
    ('EMP1', 'Ms. Aiman Shahid', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP2', 'Mrs. M. Swathi Sree', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP3', 'Dr. Shivani Yadao', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP4', 'Mrs. K. Srilatha', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP5', 'Dr. D. Radhika', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP6', 'Ms. P. Vasavi Reddy', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP7', 'Mrs. B. Sree Saranya', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP8', 'Mrs. B. Manisha', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP9', 'Mrs. M. Sowmya', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP10', 'Mr. M. Sai Ramakrishna', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP11', 'Mr. Abhisek Goud', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP12', 'Mrs. M. Thejaswee Reddy', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available'),
    ('EMP13', 'Mrs. B. Gnana Prasuna', 'CSE', 'Faculty', 'scrypt:32768:8:1$QAJofxJdX9GLTyJR$c517f6a38b3d08b4e283cefcb585495588eaa78f589afae4a6dc40b569bb353f948731241921fbe97dd9045596658dc281eaac10798644d748084c913dbedddf', TRUE, 16, 'Available')
ON CONFLICT (employee_id) DO UPDATE
SET max_hours_per_week = 16,
    availability_status = EXCLUDED.availability_status;

UPDATE teachers
SET employee_id = 'EMP' || (RIGHT(employee_id, 2)::INTEGER)::TEXT,
    max_hours_per_week = 16
WHERE employee_id LIKE 'EMP1__'
  AND NOT EXISTS (
      SELECT 1
      FROM teachers t2
      WHERE t2.employee_id = 'EMP' || (RIGHT(teachers.employee_id, 2)::INTEGER)::TEXT
  );

UPDATE teachers
SET is_active = FALSE
WHERE employee_id LIKE 'EMP1__';

INSERT INTO students (roll_number, password, section_id)
SELECT '160623733' || LPAD(gs::text, 3, '0'), 'scrypt:32768:8:1$cYhxYbEV20f7LEfO$175b93e12a60eaeac4d1d6885627125a682a64b426d75e77d43d9c1ed29afbb87f90eb4e4c797bbd12e7976ed9514b4f4c6a63875f49d0c761b5454f0ec244a9', 1
FROM generate_series(1, 64) AS gs
ON CONFLICT (roll_number) DO UPDATE SET section_id = EXCLUDED.section_id;

INSERT INTO students (roll_number, password, section_id)
SELECT '160623733' || LPAD(gs::text, 3, '0'), 'scrypt:32768:8:1$cYhxYbEV20f7LEfO$175b93e12a60eaeac4d1d6885627125a682a64b426d75e77d43d9c1ed29afbb87f90eb4e4c797bbd12e7976ed9514b4f4c6a63875f49d0c761b5454f0ec244a9', 2
FROM generate_series(65, 127) AS gs
ON CONFLICT (roll_number) DO UPDATE SET section_id = EXCLUDED.section_id;

INSERT INTO students (roll_number, password, section_id)
SELECT '160623733' || LPAD(gs::text, 3, '0'), 'scrypt:32768:8:1$cYhxYbEV20f7LEfO$175b93e12a60eaeac4d1d6885627125a682a64b426d75e77d43d9c1ed29afbb87f90eb4e4c797bbd12e7976ed9514b4f4c6a63875f49d0c761b5454f0ec244a9', 3
FROM generate_series(128, 192) AS gs
ON CONFLICT (roll_number) DO UPDATE SET section_id = EXCLUDED.section_id;

-- Insert Room Data
INSERT INTO rooms (room_no, building, floor_no, capacity, room_type, equipment, is_active)
VALUES
    ('B-402', 'Building B', 4, 70, 'Theory', 'Projector,Smart Board,AC', TRUE),
    ('B-403', 'Building B', 4, 70, 'Theory', 'Projector,Smart Board,AC', TRUE),
    ('B-404', 'Building B', 4, 70, 'Theory', 'Projector,Smart Board,AC', TRUE),
    ('LAB-1', 'Lab Block', 1, 40, 'Lab', 'Computers,Projector,AC', TRUE),
    ('LAB-2', 'Lab Block', 1, 40, 'Lab', 'Computers,Projector,AC', TRUE),
    ('LAB-3', 'Lab Block', 1, 40, 'Lab', 'Computers,Networking Equipment,AC', TRUE)
ON CONFLICT (room_no) DO UPDATE
SET building = EXCLUDED.building,
    floor_no = EXCLUDED.floor_no,
    capacity = EXCLUDED.capacity,
    room_type = EXCLUDED.room_type,
    equipment = EXCLUDED.equipment,
    is_active = TRUE;

UPDATE rooms SET room_no = 'B-402', building = 'Building B', floor_no = 4, capacity = 70 WHERE room_no = 'A101' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'B-402');
UPDATE rooms SET room_no = 'B-403', building = 'Building B', floor_no = 4, capacity = 70 WHERE room_no = 'A102' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'B-403');
UPDATE rooms SET room_no = 'B-404', building = 'Building B', floor_no = 4, capacity = 70 WHERE room_no = 'A103' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'B-404');
UPDATE rooms SET room_no = 'LAB-1', building = 'Lab Block', floor_no = 1 WHERE room_no = 'A201' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'LAB-1');
UPDATE rooms SET room_no = 'LAB-2', building = 'Lab Block', floor_no = 1 WHERE room_no = 'A202' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'LAB-2');
UPDATE rooms SET room_no = 'LAB-3', building = 'Lab Block', floor_no = 1 WHERE room_no = 'A203' AND NOT EXISTS (SELECT 1 FROM rooms WHERE room_no = 'LAB-3');
UPDATE rooms SET is_active = FALSE WHERE room_no IN ('A101', 'A102', 'A103', 'A201', 'A202', 'A203');

-- Insert Subject Data
INSERT INTO subjects (subject_name, subject_type, faculty_name, semester, hours_per_week)
VALUES
    ('Software Engineering', 'Theory', 'Ms. Aiman Shahid', 'SEM-VI', 4),
    ('Compiler Design', 'Theory', 'Mrs. M. Swathi Sree', 'SEM-VI', 4),
    ('Information Security', 'Theory', 'Dr. Shivani Yadao', 'SEM-VI', 4),
    ('DevOps', 'Theory', 'Mrs. K. Srilatha', 'SEM-VI', 4),
    ('Startup and Entrepreneurship', 'Theory', 'Dr. D. Radhika', 'SEM-VI', 3),
    ('Technical Seminar', 'Theory', 'Ms. P. Vasavi Reddy', 'SEM-VI', 2),
    ('Library', 'Theory', 'Mrs. B. Sree Saranya', 'SEM-VI', 1),
    ('Sports', 'Theory', 'Mrs. B. Manisha', 'SEM-VI', 1),
    ('Self Learning', 'Theory', 'Mrs. M. Sowmya', 'SEM-VI', 1),
    ('Mentoring', 'Theory', 'Mr. M. Sai Ramakrishna', 'SEM-VI', 1),
    ('CRT', 'Theory', 'Mr. Abhisek Goud', 'SEM-VI', 5),
    ('Software Engineering Lab', 'Lab', 'Mrs. M. Thejaswee Reddy', 'SEM-VI', 2),
    ('Information Security Lab', 'Lab', 'Mrs. B. Gnana Prasuna', 'SEM-VI', 2),
    ('Compiler Design Lab', 'Lab', 'Ms. Aiman Shahid', 'SEM-VI', 2),
    ('Cloud Computing', 'Theory', 'Mrs. K. Srilatha', 'SEM-VI', 4)
ON CONFLICT DO NOTHING;
