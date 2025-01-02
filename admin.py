import sqlite3
import os
import threading
# from facenet_pytorch import MTCNN, InceptionResnetV1
# import torch
from PIL import Image
from tkinter import filedialog, Tk
import asyncio
#import active_detection

# Connect to SQLite database
conn = sqlite3.connect('Faces.db')
c = conn.cursor()

# mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
# resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion


def add_single():
    
    from facenet_pytorch import MTCNN, InceptionResnetV1
    import torch
    mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
    resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion
    
    
    name = input("Enter the name of the person: ")

    root = Tk()
    root.withdraw()  # Hide the root window

    img_path = filedialog.askopenfilename(title="Select Image")
    
    if not img_path:
        print("No image selected.")
        return

    if not os.path.exists(img_path):
        print("Image path does not exist.")
        return
    
    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True)
    
    if face is None or prob < 0.90:
        print("No face detected in the image.")
        return
    
    emb = resnet(face.unsqueeze(0)).detach()
    emb_bytes = emb.numpy().tobytes()
    
    # Insert embedding and name into the table
    c.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, emb_bytes))
    conn.commit()
    print("Embedding added successfully for", name)


def add_bulk():

    from facenet_pytorch import MTCNN, InceptionResnetV1
    mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
    resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion
    
    root = Tk()
    root.withdraw()  # Hide the root window

    folder_path = filedialog.askdirectory()
    if not folder_path:
        print("No folder selected.")
        return

    sub_folders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
    if not sub_folders:
        print("No sub-folders found.")
        return

    for sub_folder in sub_folders:
        name = os.path.basename(sub_folder)
        img_paths = [os.path.join(sub_folder, img_name) for img_name in os.listdir(sub_folder) if img_name.endswith(('.png', '.jpg', '.jpeg'))]

        if not img_paths:
            print(f"No image found in '{name}' sub-folder. Skipping.")
            continue

        for img_path in img_paths:
            img = Image.open(img_path)
            face, prob = mtcnn(img, return_prob=True)

            if face is not None and prob > 0.90:
                emb = resnet(face.unsqueeze(0)).detach()
                emb_bytes = emb.numpy().tobytes()

                # Insert embedding and name into the table
                c.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, emb_bytes))

    conn.commit()
    print("Embeddings added successfully.")


def delete_entry():
    name = input("Enter the name of the person to delete: ")
    
    # Delete entry from the table
    c.execute("DELETE FROM faces WHERE name=?", (name,))
    conn.commit()
    print("Entry deleted successfully.")

def view_names():
    c.execute("SELECT DISTINCT name FROM faces")
    names = c.fetchall()
    if not names:
        print("No names found.")
    else:
        print("Existing names:")
        for name in names:
            print("- ", name[0])

def view_class_routine():
    c.execute("SELECT * FROM class_routine")
    class_routines = c.fetchall()
    if not class_routines:
        print("No class routines found.")
    else:
        print("Class routines:")
        for routine in class_routines:
            print("- Teacher:", routine[1])
            print("  Class start time:", routine[2])
            print("  Class end time:", routine[3])
            print("  Class room:", routine[4])
            print("  Camera index:", routine[5])
            print()

def view_teacher_attendance():
    teacher_name = input("Enter the name of the teacher: ")
    c.execute("SELECT * FROM attendance WHERE teacher_name=?", (teacher_name,))
    teacher_attendance = c.fetchall()
    if teacher_attendance:
        print("Teacher Attendance Record:")
        for record in teacher_attendance:
            print("- Date:", record[3])
            print("- Class Start Time:", record[2])
            print("- Class Room:", record[4])
            print("- Attendance Status:", record[5])
            print("- Attendance Time:", record[6])
            print()
    else:
        print("No attendance record found for this teacher.")

def add_timetable_single():
    name = input("Enter the name of the teacher: ")
    class_start_time = input("Enter the class start time (HH:MM AM/PM): ")
    class_end_time = input("Enter the class end time (HH:MM AM/PM): ")
    class_room = input("Enter the class room: ")
    camera_index = input("Enter the camera index: ")
    
    c.execute("INSERT INTO class_routine (teacher_name, class_start_time, class_end_time, class_room, camera_index) VALUES (?, ?, ?, ?, ?)", 
              (name, class_start_time, class_end_time, class_room, camera_index))
    conn.commit()
    print("Class routine added successfully.")

def change_timetable_entry():
    name = input("Enter the name of the teacher whose class routine you want to change: ")

    # Check if the teacher exists in the class routine
    c.execute("SELECT * FROM class_routine WHERE teacher_name=?", (name,))
    existing_entry = c.fetchone()
    if not existing_entry:
        print("Teacher not found in the class routine.")
        return

    # Ask for changes
    print("Existing details:")
    print("- Teacher:", existing_entry[1])
    print("- Class start time:", existing_entry[2])
    print("- Class end time:", existing_entry[3])
    print("- Class room:", existing_entry[4])
    print("- Camera index:", existing_entry[5])

    # Ask for new values
    class_start_time = input("Enter the new class start time (HH:MM AM/PM) or press Enter to keep unchanged: ")
    class_end_time = input("Enter the new class end time (HH:MM AM/PM) or press Enter to keep unchanged: ")
    class_room = input("Enter the new class room or press Enter to keep unchanged: ")
    camera_index = input("Enter the new camera index or press Enter to keep unchanged: ")

    # Build the query and parameters
    query = "UPDATE class_routine SET"
    parameters = []

    if class_start_time:
        query += " class_start_time=?,"
        parameters.append(class_start_time)
    if class_end_time:
        query += " class_end_time=?,"
        parameters.append(class_end_time)
    if class_room:
        query += " class_room=?,"
        parameters.append(class_room)
    if camera_index:
        query += " camera_index=?,"
        parameters.append(camera_index)

    # Remove the last comma
    query = query.rstrip(",")

    # Add WHERE clause
    query += " WHERE teacher_name=?"
    parameters.append(name)

    # Execute the update query
    c.execute(query, parameters)
    conn.commit()
    print("Class routine updated successfully.")


def delete_timetable_entry():
    name = input("Enter the name of the teacher whose class routine you want to delete: ")
    c.execute("DELETE FROM class_routine WHERE teacher_name=?", (name,))
    conn.commit()
    print("Class routine deleted successfully.")

# Functionality testing
if __name__ == "__main__":
    while True:
        print("\n1.  View all Teachers")
        print("2.  Add a single Teacher Embedding")
        print("3.  Add Teachers embeddings in bulk")
        print("4.  Delete an existing Teacher Embedding")
        print("5.  View Teacher's Attendence Record")
        print("6.  View Classes Routine")
        print("7.  Add Class Routine")
        print("8.  Change Class Routine")
        print("9.  Delete Class Routine")
        print("0.  Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            view_names()
        elif choice == '2':
            add_single()
        elif choice == '3':
            add_bulk()
        elif choice == '4':
            delete_entry()
        elif choice == '5':
            view_teacher_attendance()
        elif choice == '6':
            view_class_routine()
        elif choice == '7':
            add_timetable_single()
        elif choice == '8':
            change_timetable_entry()
        elif choice == '9':
            delete_timetable_entry()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

# Close connection
conn.close()