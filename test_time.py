# import asyncio
# from facenet_pytorch import MTCNN, InceptionResnetV1
# import torch
# import cv2
# import time
# from PIL import Image
# import numpy as np
# import datetime


# # Import aiosqlite for asynchronous database operations
# import aiosqlite

# # Initialize MTCNN and InceptionResnetV1
# mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
# resnet = InceptionResnetV1(pretrained='vggface2').eval()

# # Function to compare face embeddings
# async def face_match(emb, threshold=0.6):
#     async with aiosqlite.connect('Faces.db') as db:
#         async with db.execute("SELECT name, embedding FROM faces") as cursor:
#             rows = await cursor.fetchall()

#     dist_list = []
    
#     for row in rows:
#         name, emb_db_bytes = row
#         emb_db = torch.from_numpy(np.frombuffer(emb_db_bytes, dtype=np.float32).copy()).unsqueeze(0)
#         dist = torch.dist(emb, emb_db).item()
#         dist_list.append((name, dist))
    
#     min_dist_name, min_dist = min(dist_list, key=lambda x: x[1])
    
#     if min_dist <= threshold:
#         return min_dist_name, min_dist
#     else:
#         return "No match found", min_dist

# # Function to capture images and perform face detection during class time
# async def capture_images(class_start_time_str, camera_index, teacher_name):
#     class_duration = datetime.timedelta(minutes=10)  # 10 minutes
#     start_time = datetime.datetime.now()
#     class_start_time = datetime.datetime.strptime(class_start_time_str, "%I:%M %p").replace(second=0, microsecond=0)
#     detected_class = False
    
#     while datetime.datetime.now() - start_time < class_duration:
#         current_time = datetime.datetime.now().replace(second=0, microsecond=0)
#         print("Current Time: ", current_time.strftime("%I:%M %p"))
#         print("Class Start Time: ", class_start_time.strftime("%I:%M %p"))
        
#         # Check if there's any class scheduled at the current time
#         if current_time.hour == class_start_time.hour and current_time.minute == class_start_time.minute:
#             print("Class start time: ", class_start_time.strftime("%I:%M %p"))
#             detected_class = True
#             break
        
#         await asyncio.sleep(1)  # Check every second for class schedule
        
#     if detected_class:
#         async with aiosqlite.connect('Faces.db') as db:
#             async with db.execute("SELECT embedding FROM faces WHERE name=?", (teacher_name,)) as cursor:
#                 result = await cursor.fetchone()
        
#         if result:
#             teacher_embedding = torch.from_numpy(np.frombuffer(result[0], dtype=np.float32).copy()).unsqueeze(0)
            
#             cap = cv2.VideoCapture(camera_index)  # Initialize camera capture
#             print("Starting cam: ", camera_index)
#             while datetime.datetime.now() - start_time < class_duration:
#                 ret, frame = cap.read()  # Capture frame
                
#                 if ret:
#                     # Display the captured frame
#                     cv2.imshow('Captured Image', frame)
#                     cv2.waitKey(1)  # Minimal delay
                    
#                     # Convert frame to PIL Image and detect face
#                     frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#                     face, prob = mtcnn(frame_pil, return_prob=True)
                    
#                     if face is not None and prob > 0.90:  # If face detected and probability > 90%
#                         emb = resnet(face.unsqueeze(0)).detach()  # Extract face embedding
                        
#                         # Compare face embedding with the embedding of the specific teacher
#                         start_matching_time = time.time()
#                         dist = torch.dist(teacher_embedding, emb).item()
#                         end_matching_time = time.time()
                        
#                         if dist <= 0.6:  # If face matches with the specific teacher
#                             print("Face matched with:", teacher_name)
#                             print("Time taken for matching:", end_matching_time - start_matching_time, "seconds")
                            
#                             # Mark attendance in the database
#                             await mark_attendance(teacher_name, class_start_time_str)
#                             break  # Shut down operations on detection
            
#             cap.release()  # Release camera
#             cv2.destroyAllWindows()  # Close windows

# # Function to mark attendance in the database
# async def mark_attendance(teacher_name, class_start_time):
#     async with aiosqlite.connect('Faces.db') as db:
#         await db.execute("INSERT INTO attendance (teacher_name, class_start_time, date, class_room, attendance_status, attendance_time) VALUES (?, ?, ?, ?, 'P', ?)",
#                          (teacher_name, class_start_time, time.strftime("%Y-%m-%d"), await get_class_room(teacher_name), time.strftime("%H:%M:%S")))
#         await db.commit()

# # Function to get class room based on teacher name
# async def get_class_room(teacher_name):
#     async with aiosqlite.connect('Faces.db') as db:
#         async with db.execute("SELECT class_room FROM class_routine WHERE teacher_name=?", (teacher_name,)) as cursor:
#             result = await cursor.fetchone()
#     if result:
#         return result[0]
#     else:
#         return None

# # Function to get class routine
# async def get_class_routine():
#     async with aiosqlite.connect('Faces.db') as db:
#         async with db.execute("SELECT class_start_time, camera_index, teacher_name FROM class_routine") as cursor:
#             return await cursor.fetchall()

# # Main function to start processing class routines asynchronously
# async def main():
#     class_routines = await get_class_routine()
#     print("Fetched class routines:", class_routines)
#     tasks = [asyncio.create_task(capture_images(class_start_time, camera_index, teacher_name)) for class_start_time, camera_index, teacher_name in class_routines]
#     await asyncio.gather(*tasks)

# # Run the main function using asyncio's event loop
# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import cv2
import time
from PIL import Image
import numpy as np
import datetime

# Import aiosqlite for asynchronous database operations
import aiosqlite

# Initialize MTCNN and InceptionResnetV1
mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Function to compare face embeddings
async def face_match(emb, threshold=0.6):
    async with aiosqlite.connect('Faces.db') as db:
        async with db.execute("SELECT name, embedding FROM faces") as cursor:
            rows = await cursor.fetchall()

    dist_list = []
    
    for row in rows:
        name, emb_db_bytes = row
        emb_db = torch.from_numpy(np.frombuffer(emb_db_bytes, dtype=np.float32).copy()).unsqueeze(0)
        dist = torch.dist(emb, emb_db).item()
        dist_list.append((name, dist))
    
    min_dist_name, min_dist = min(dist_list, key=lambda x: x[1])
    
    if min_dist <= threshold:
        return min_dist_name, min_dist
    else:
        return "No match found", min_dist

# Function to capture images and perform face detection during class time
async def capture_images(class_start_time_str, camera_index, teacher_name):
    class_duration = datetime.timedelta(minutes=10)  # 10 minutes
    start_time = datetime.datetime.now()
    class_start_time = datetime.datetime.strptime(class_start_time_str, "%I:%M %p").replace(second=0, microsecond=0)
    detected_class = False
    
    while datetime.datetime.now() - start_time < class_duration:
        current_time = datetime.datetime.now().replace(second=0, microsecond=0)
        print("Current Time: ", current_time.strftime("%I:%M %p"))
        print("Class Start Time: ", class_start_time.strftime("%I:%M %p"))
        
        # Check if there's any class scheduled at the current time
        if current_time.hour == class_start_time.hour and current_time.minute == class_start_time.minute:
            print("Class start time: ", class_start_time.strftime("%I:%M %p"))
            detected_class = True
            break
        
        await asyncio.sleep(1)  # Check every second for class schedule
        
    if detected_class:
        async with aiosqlite.connect('Faces.db') as db:
            async with db.execute("SELECT embedding FROM faces WHERE name=?", (teacher_name,)) as cursor:
                result = await cursor.fetchone()
        
        if result:
            teacher_embedding = torch.from_numpy(np.frombuffer(result[0], dtype=np.float32).copy()).unsqueeze(0)
            
            cap = cv2.VideoCapture(camera_index)  # Initialize camera capture
            print("Starting cam: ", camera_index)
            while datetime.datetime.now() - start_time < class_duration:
                ret, frame = cap.read()  # Capture frame
                
                if ret:
                    # Display the captured frame
                    cv2.imshow('Captured Image', frame)
                    cv2.waitKey(1)  # Minimal delay
                    
                    # Convert frame to PIL Image and detect face
                    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    face, prob = mtcnn(frame_pil, return_prob=True)
                    
                    if face is not None and prob > 0.90:  # If face detected and probability > 90%
                        emb = resnet(face.unsqueeze(0)).detach()  # Extract face embedding
                        
                        # Compare face embedding with the embedding of the specific teacher
                        start_matching_time = time.time()
                        dist = torch.dist(teacher_embedding, emb).item()
                        end_matching_time = time.time()
                        
                        if dist <= 0.6:  # If face matches with the specific teacher
                            print("Face matched with:", teacher_name)
                            print("Time taken for matching:", end_matching_time - start_matching_time, "seconds")
                            
                            # Mark attendance in the database
                            await mark_attendance(teacher_name, class_start_time_str)
                            break  # Shut down operations on detection
            
            cap.release()  # Release camera
            cv2.destroyAllWindows()  # Close windows

# Function to mark attendance in the database
async def mark_attendance(teacher_name, class_start_time):
    async with aiosqlite.connect('Faces.db') as db:
        await db.execute("INSERT INTO attendance (teacher_name, class_start_time, date, class_room, attendance_status, attendance_time) VALUES (?, ?, ?, ?, 'P', ?)",
                         (teacher_name, class_start_time, time.strftime("%Y-%m-%d"), await get_class_room(teacher_name), time.strftime("%H:%M:%S")))
        await db.commit()

# Function to get class room based on teacher name
async def get_class_room(teacher_name):
    async with aiosqlite.connect('Faces.db') as db:
        async with db.execute("SELECT class_room FROM class_routine WHERE teacher_name=?", (teacher_name,)) as cursor:
            result = await cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# Function to get class routine
async def get_class_routine():
    async with aiosqlite.connect('Faces.db') as db:
        async with db.execute("SELECT class_start_time, camera_index, teacher_name FROM class_routine") as cursor:
            return await cursor.fetchall()

# Main function to start processing class routines asynchronously
async def main():
    while True:
        try:
            class_routines = await get_class_routine()
            print("Fetched class routines:", class_routines)
            tasks = [asyncio.create_task(capture_images(class_start_time, camera_index, teacher_name)) for class_start_time, camera_index, teacher_name in class_routines]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Delay between iterations
        await asyncio.sleep(60)  # Check every minute for class schedule

# Run the main function using asyncio's event loop
if __name__ == "__main__":
    asyncio.run(main())
