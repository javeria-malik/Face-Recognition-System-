import sqlite3
import os
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torchvision import datasets
from torch.utils.data import DataLoader
from PIL import Image
import numpy as np

# Connect to SQLite database
conn = sqlite3.connect('Faces.db')
c = conn.cursor()

# Create table to store embeddings and names
c.execute('''CREATE TABLE IF NOT EXISTS faces
             (name TEXT, embedding BLOB)''')

# Commit changes
conn.commit()

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embedding conversion

dataset = datasets.ImageFolder('photos') # photos folder path 
idx_to_class = {i: c for c, i in dataset.class_to_idx.items()} # accessing names of peoples from folder names

def collate_fn(x):
    return x[0]

loader = DataLoader(dataset, collate_fn=collate_fn)

for img, idx in loader:
    face, prob = mtcnn(img, return_prob=True) 
    if face is not None and prob > 0.90: # if face detected and probability > 90%
        emb = resnet(face.unsqueeze(0)).detach() # passing cropped face into resnet model to get embedding matrix
        emb_bytes = emb.numpy().tobytes()
        name = idx_to_class[idx]
        
        # Insert embedding and name into the table
        c.execute("INSERT INTO faces (name, embedding) VALUES (?, ?)", (name, emb_bytes))

# Commit changes and close connection
conn.commit()
conn.close()

def face_match(img_path, threshold=0.6):
    # Connect to SQLite database
    conn = sqlite3.connect('Faces.db')
    c = conn.cursor()

    img = Image.open(img_path)
    face, prob = mtcnn(img, return_prob=True)
    
    # Return a message if face detection fails or probability is low
    if face is None or prob < 0.90:
        return ("No face detected", None)
    
    emb = resnet(face.unsqueeze(0)).detach()
    
    # Retrieve embeddings and names from the database
    c.execute("SELECT name, embedding FROM faces")
    rows = c.fetchall()
    
    dist_list = []
    
    for row in rows:
        name, emb_db_bytes = row
        emb_db = torch.from_numpy(np.frombuffer(emb_db_bytes, dtype=np.float32)).unsqueeze(0)
        dist = torch.dist(emb, emb_db).item()
        dist_list.append((name, dist))
    
    conn.close()
    
    min_dist_name, min_dist = min(dist_list, key=lambda x: x[1])
    
    if min_dist <= threshold:
        return (min_dist_name, min_dist)
    else:
        return ("No match found", min_dist)

result = face_match('WIN_20240511_14_17_55_Pro.jpg', threshold=0.6)

print('Face matched with:', result[0], 'With distance:', result[1])