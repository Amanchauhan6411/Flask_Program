from datetime import datetime
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="***********",
    database="mgroom"
)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS booked_slots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_name VARCHAR(100),
                    date DATE,
                    start_time TIME,
                    end_time TIME
                 )''')
conn.commit()


def insert_booked_slot(date, start_time, end_time, user_name):
    sql = '''INSERT INTO booked_slots (date, start_time, end_time, user_name)
             VALUES (%s, %s, %s, %s)'''
    values = (date, start_time, end_time, user_name)
    cursor.execute(sql, values)
    conn.commit()


def check_overlapping_slots(date, start_time, end_time):
    sql = '''SELECT * FROM booked_slots
             WHERE date = %s AND %s < end_time AND %s > start_time'''
    values = (date, start_time, end_time)
    cursor.execute(sql, values)
    return cursor.fetchall()


def print_booked_slots():
    cursor.execute('''SELECT * FROM booked_slots''')
    rows = cursor.fetchall()
    print("Booked slots:")
    for row in rows:
        print(f"Date: {row[1]} - Start time: {row[2]}, End time: {row[3]}, User: {row[4]}")


def meeting_slot(date, start_time, end_time, user_name):
    s_time = datetime.strptime(start_time, '%H:%M').time()
    e_time = datetime.strptime(end_time, '%H:%M').time()

    if e_time <= s_time:
        return False, "End time must be after start time"

    if (datetime.combine(datetime.min, e_time) - datetime.combine(datetime.min, s_time)).total_seconds() < 3600:
        return False, "Meeting duration must be more than 1 hour"

    meeting_start = datetime.strptime('07:00', '%H:%M').time()
    meeting_end = datetime.strptime('22:00', '%H:%M').time()
    if s_time < meeting_start or e_time > meeting_end:
        return False, "Meeting hours are from 7am to 10pm"

    overlapping_slots = check_overlapping_slots(date, start_time, end_time)
    if overlapping_slots:
        return False, "Overlapping meeting slot with other slots"

    insert_booked_slot(date, start_time, end_time, user_name)
    print_booked_slots()
    return True, "Meeting slot is booked"


while True:
    user_name = input("Enter your full name: ")
    date = input("Enter date (YYYY-MM-DD): ")
    start_time = input("Enter start time (HH:MM): ")
    end_time = input("Enter end time (HH:MM): ")
    

    valid, message = meeting_slot(date, start_time, end_time, user_name)
    if valid:
        print("Meeting slot is booked")
    else:
        print("Invalid meeting slot:", message)

    check = input("Do you want to continue (yes/no)? ").lower()
    if check != 'yes':
        break

conn.close()
