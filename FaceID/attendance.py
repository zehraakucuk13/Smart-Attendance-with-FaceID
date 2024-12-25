import cv2
from simple_facerec import SimpleFacerec
from datetime import datetime
from datetime import date
import time
import sqlite3

conn = sqlite3.connect('manual_info.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS attendees
                  (name TEXT, age TEXT, gender TEXT, id TEXT, info TEXT)''')

manual_info = {
    "A Guest": {"Age": "N/A", "Gender": "N/A", "ID": "N/A", "Info": "Attended"},
    "Drew Starkey": {"Age": "30", "Gender": "Male", "ID": "1725312", "Info": "Attended"},
    "Fiona Palomo": {"Age": "24", "Gender": "Female", "ID": "1173721", "Info": "Attended"},
    "Johnny Depp": {"Age": "61", "Gender": "Male", "ID": "1234567", "Info": "Attended"},
    "Madelyn Cline": {"Age": "26", "Gender": "Female", "ID": "1981274", "Info": "Attended"},
    "Madison Bailey": {"Age": "25", "Gender": "Female", "ID": "1957467", "Info": "Attended"},
    "Margot Robbie": {"Age": "34", "Gender": "Female", "ID": "1654321", "Info": "Attended"},
    "Robert Pattinson": {"Age": "38", "Gender": "Male", "ID": "1427497", "Info": "Attended"},
    "Shawn Mendes": {"Age": "26", "Gender": "Male", "ID": "1782735", "Info": "Attended"},
    "Taylor Swift": {"Age": "35", "Gender": "Female", "ID": "1543210", "Info": "Attended"}
}

for name, info in manual_info.items():
    cursor.execute("INSERT INTO attendees (name, age, gender, id, info) VALUES (?, ?, ?, ?, ?)",
                   (name, info["Age"], info["Gender"], info["ID"], info["Info"]))
conn.commit()

cursor.execute("SELECT name FROM attendees")
manual_names = {row[0] for row in cursor.fetchall()}

today = date.today()
day = today.strftime("%b-%d-%Y")
day_str = "attendance-" + day + ".csv"
print(day_str)

with open(day_str, "a") as dosya:
    dosya.write("Name, Age, Gender, ID, Info, Time")

file_open_time = time.time()

def get_manual_info(name):
    cursor.execute("SELECT age, gender, id, info FROM attendees WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return {"Age": row[0], "Gender": row[1], "ID": row[2], "Info": row[3]}
    return None

def writeAttendance(name):
    with open(day_str, 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            if name in manual_names:
                info = get_manual_info(name)
                if info:
                    age = info["Age"]
                    gender = info["Gender"]
                    _ID = info["ID"]
                    _info = info["Info"]
                    f.writelines(f'\n{name},{age},{gender},{_ID},{_info},{dtString}')

sfr = SimpleFacerec()
sfr.load_encoding_images("images/")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        cv2.putText(frame, name,(x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (200, 0, 0), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 0, 0), 4)

        writeAttendance(name)

    current_time = time.time()
    time_diff = current_time - file_open_time

    if time_diff > 180:
        for name in manual_names:
            with open(day_str, 'r+') as f:
                myDataList = f.readlines()
                nameList = [entry.split(',')[0] for entry in myDataList]

                if name not in nameList:
                    info = get_manual_info(name)
                    if info:
                        age = info["Age"]
                        gender = info["Gender"]
                        _ID = info["ID"]
                        _info = "Not Attended"
                        now = datetime.now()
                        dtString = now.strftime('%H:%M:%S')
                        f.writelines(f'\n{name},{age},{gender},{_ID},{_info},{dtString}')

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()

conn.close()
