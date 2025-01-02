# streamlit_app.py

import streamlit as st
import sqlite3
#from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
from tkinter import filedialog, Tk
import base64


# Function to view all teachers
def view_all_teachers():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Query the database to fetch all teachers' names
    c.execute("SELECT DISTINCT name FROM faces")
    teachers = c.fetchall()

    # Display the list of teachers
    if not teachers:
        st.write("No teachers found.")
    else:
        st.write("Existing teachers:")
        for teacher in teachers:
            st.write("- ", teacher[0])

# Function to add a single teacher embedding
def add_single_teacher_embedding():
    from facenet_pytorch import MTCNN, InceptionResnetV1
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Add a Single Teacher Data")

    # Initialize MTCNN and InceptionResnetV1
    mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
    resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion

    # Get the name of the person
    name = st.text_input("Enter the name of the person:")

    # Create file uploader for image selection
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Read image
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Detect face in the image
        face, prob = mtcnn(img, return_prob=True)

        if face is not None and prob >= 0.90:
            # Extract embedding
            emb = resnet(face.unsqueeze(0)).detach()
            emb_bytes = emb.numpy().tobytes()

            # Insert embedding and name into the table
            c.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, emb_bytes))
            conn.commit()
            st.success(f"Embedding added successfully for {name}.")
        else:
            st.error("No face detected in the image or confidence level is below 90%.")



# Function to add teachers embeddings in bulk
def add_bulk_teacher_embeddings():
    
    import os
    from facenet_pytorch import MTCNN, InceptionResnetV1
    
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Add Teachers Data in Bulk")

    # Initialize MTCNN and InceptionResnetV1
    mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
    resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion

    # Create folder uploader for selecting the folder containing teacher images
    folder_path = st.text_input("Enter the folder path:")
    if st.button("Select Folder"):
        if not os.path.exists(folder_path):
            st.error("Folder path does not exist.")
            return

        sub_folders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
        if not sub_folders:
            st.warning("No sub-folders found.")
            return

        for sub_folder in sub_folders:
            name = os.path.basename(sub_folder)
            img_paths = [os.path.join(sub_folder, img_name) for img_name in os.listdir(sub_folder) if img_name.endswith(('.png', '.jpg', '.jpeg'))]

            if not img_paths:
                st.warning(f"No image found in '{name}' sub-folder. Skipping.")
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
        st.success("Embeddings added successfully.")
        
# Function to delete a specific entry from the database
def delete_teacher_embedding():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Delete Teacher's Data")

    # Get the name of the person to delete
    name = st.text_input("Enter the name of the Teacher to delete:")

    # Create a button to trigger the deletion process
    if st.button("Delete"):
        # Delete entry from the table
        c.execute("DELETE FROM faces WHERE name=?", (name,))
        conn.commit()
        st.success("Embedding deleted successfully.")

# Function to view attendance record for a specific teacher
def view_teacher_attendance():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("View Teacher Attendance")

    # Get the name of the teacher
    teacher_name = st.text_input("Enter the name of the teacher:")

    # Execute SQL query to fetch attendance records for the specified teacher
    c.execute("SELECT * FROM attendance WHERE teacher_name=?", (teacher_name,))
    teacher_attendance = c.fetchall()

    # Display attendance records in a Streamlit component
    if teacher_attendance:
        st.write("Teacher Attendance Record:")
        for record in teacher_attendance:
            st.write("- Date:", record[3])
            st.write("- Class Start Time:", record[2])
            st.write("- Class Room:", record[4])
            st.write("- Attendance Status:", record[5])
            st.write("- Attendance Time:", record[6])
            st.write("\n")
            st.write("-----------------------------")
            st.write("\n")
    else:
        st.warning("No attendance record found for this teacher.")

# Function to view all class routines
def view_classes_routine():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("View Class Routine")

    # Execute SQL query to fetch all class routines
    c.execute("SELECT * FROM class_routine")
    class_routines = c.fetchall()

    # Display class routines in a Streamlit component
    if not class_routines:
        st.warning("No class routines found.")
    else:
        st.write("Class routines:")
        for routine in class_routines:
            st.write("- Teacher:", routine[1])
            st.write("  Class start time:", routine[2])
            st.write("  Class end time:", routine[3])
            st.write("  Class room:", routine[4])
            st.write("  Camera index:", routine[5])
            st.write("\n")
            st.write("-----------------------------")
            st.write("\n")

# Function to add a single class routine to the timetable
def add_class_routine():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Add Class Routine")

    # Get details of the class routine from the admin
    name = st.text_input("Enter the name of the teacher:")
    class_start_time = st.text_input("Enter the class start time (HH:MM AM/PM):")
    class_end_time = st.text_input("Enter the class end time (HH:MM AM/PM):")
    class_room = st.text_input("Enter the class room:")
    camera_index = st.text_input("Enter the camera index:")

    # Create a button to add the class routine with a unique key
    if st.button("Add Class Routine", key="add_class_routine_button"):
        # Execute SQL query to insert class routine into the table
        c.execute("INSERT INTO class_routine (teacher_name, class_start_time, class_end_time, class_room, camera_index) VALUES (?, ?, ?, ?, ?)",
                  (name, class_start_time, class_end_time, class_room, camera_index))
        conn.commit()
        st.success("Class routine added successfully.")

# Function to change a class routine entry in the timetable
def change_class_routine():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Change Class Routine")

    # Get the name of the teacher whose class routine is to be changed
    name = st.text_input("Enter the name of the teacher whose class routine you want to change:")

    # Check if the teacher exists in the class routine
    c.execute("SELECT * FROM class_routine WHERE teacher_name=?", (name,))
    existing_entry = c.fetchone()

    if existing_entry:
        # Display existing details
        st.write("Existing details:")
        st.write("- Teacher:", existing_entry[1])
        st.write("- Class start time:", existing_entry[2])
        st.write("- Class end time:", existing_entry[3])
        st.write("- Class room:", existing_entry[4])
        st.write("- Camera index:", existing_entry[5])

        # Get new values from the admin
        class_start_time = st.text_input("Enter the new class start time (HH:MM AM/PM) or leave blank to keep unchanged:", value=existing_entry[2])
        class_end_time = st.text_input("Enter the new class end time (HH:MM AM/PM) or leave blank to keep unchanged:", value=existing_entry[3])
        class_room = st.text_input("Enter the new class room or leave blank to keep unchanged:", value=existing_entry[4])
        camera_index = st.text_input("Enter the new camera index or leave blank to keep unchanged:", value=existing_entry[5])

        # Create a button to update the class routine
        if st.button("Update Class Routine"):
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
            st.success("Class routine updated successfully.")
    else:
        st.warning("Teacher not found in the class routine.")


# Function to delete a class routine entry from the timetable
def delete_class_routine():
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    # Set page title and header
    st.title("Delete Class Routine")

    # Get the name of the teacher whose class routine is to be deleted
    name = st.text_input("Enter the name of the teacher whose class routine you want to delete:")

    # Create a button to delete the class routine entry with a unique key
    if st.button("Delete Class Routine", key="delete_class_routine_button"):
        # Execute SQL query to delete the class routine entry
        c.execute("DELETE FROM class_routine WHERE teacher_name=?", (name,))
        conn.commit()
        st.success("Class routine deleted successfully.")


# Define a function to switch between pages
def navigate():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Welcome'
    return st.session_state['page']

# Define a function to set the current page
def set_page(page_name):
    st.session_state['page'] = page_name
    st.experimental_rerun()

# Functions for different pages
def welcome():
    st.title("Welcome")
    st.write("""
    As an admin, you can perform the following operations:
    1. View all teachers
    2. Add a single teacher embedding
    3. Add teachers embeddings in bulk
    4. Delete an existing teacher embedding
    5. View teacher's attendance record
    6. View class routines
    7. Add a class routine
    8. Change a class routine
    9. Delete a class routine
    """)

st.markdown("""
    <div style="display: flex; align-items: center;">
        <img src="https://www.pngitem.com/pimgs/m/523-5233379_employee-management-system-logo-hd-png-download.png" width="50" height="50" alt="Icon" style="margin-right: 10px;">
        <h1>Teacher Management System</h1>
    </div>
    """, unsafe_allow_html=True)

menu_options = {
    "Welcome": welcome,
    "View all Teachers": view_all_teachers,
    "Add a Single Teacher": add_single_teacher_embedding,
    "Add Teachers in bulk": add_bulk_teacher_embeddings,
    "Delete an Existing Teacher": delete_teacher_embedding,
    "View Teacher's Attendance Record": view_teacher_attendance,
    "View Classes Routine": view_classes_routine,
    "Add Class Routine": add_class_routine,
    "Change Class Routine": change_class_routine,
    "Delete Class Routine": delete_class_routine
}

# Create buttons in the sidebar for navigation
st.sidebar.header("Navigation")
for page in menu_options.keys():
    if st.sidebar.button(page):
        set_page(page)

# Get the current page and call the corresponding function
current_page = navigate()
menu_options[current_page]()