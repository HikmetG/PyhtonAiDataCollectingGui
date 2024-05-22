import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import threading
import PIL.Image, PIL.ImageTk
import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("_PATH_")
firebase_admin.initialize_app(cred)
db = firestore.client()



file_path = ""
cap = None
current_second = 0.0
def add_traffic_light_toDb():
    #for firebase
    data = {
        "Current Second " : current_second
    }
    doc_ref = db.collection("video_Traffic_Light").document()
    doc_ref.set(data)

    # Connect to SQLite database
    conn = sqlite3.connect('Does_Traffic_Light_Exist.db')
    cursor = conn.cursor()
    # Create a table to store video seconds if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_Traffic_Light (id INTEGER PRIMARY KEY, second REAL)''')
    conn.commit()
    # Save current second to database
    cursor.execute("INSERT INTO video_Traffic_Light (second) VALUES (?)", (current_second,))
    conn.commit()
    conn.close()

def add_not_traffic_light_toDb():
    #for firebase
    data = {
        "Current Second " : current_second
    }
    doc_ref = db.collection("video_not_Traffic_Light").document()
    doc_ref.set(data)

    conn = sqlite3.connect('Does_Traffic_Light_Exist.db')
    cursor = conn.cursor()
    # Create a table to store video seconds if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS video_not_Traffic_Light (id INTEGER PRIMARY KEY, second REAL)''')
    conn.commit()
    # Save current second to database
    cursor.execute("INSERT INTO video_not_Traffic_Light (second) VALUES (?)", (current_second,))
    conn.commit()
    conn.close()
def select_video():
    global file_path
    file_path = filedialog.askopenfilename(title="Select a video file", filetypes=[("Video files", "*.mp4;*.avi;*.mkv")])
    print(file_path)

def play_video():
    global file_path, cap
    # Prompt the user to select a video file
    if not file_path:
        messagebox.showerror("Error", "No video file selected")
        return  # User cancelled the file dialog

    # Define a function to read and display the video
    def display_video():
        global cap, current_second

        

        

        cap = cv2.VideoCapture(file_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Get the current frame number and calculate the current second
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
            current_second = frame_number / frame_rate

            

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize the frame to fit the GUI
            frame_resized = cv2.resize(frame_rgb, (640, 480))

            # Convert the frame to a PIL ImageTk format
            img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_resized))

            # Update the label with the new image
            label.config(image=img)
            label.image = img

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Close the SQLite connection
        

        cap.release()
        cv2.destroyAllWindows()

    # Start a new thread to display the video
    threading.Thread(target=display_video).start()

def stop_video():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()

# Create the main application window
root = tk.Tk()
root.title("Video Player App")
root.geometry("600x800")

# Create a label widget to display the video frames
label = tk.Label(root)
label.pack()

# Create a button widget to select a video file
button1 = tk.Button(root, text="Select Video", command=select_video)
button1.pack()

# Create a button widget to play the video
button2 = tk.Button(root, text="Play Video", command=play_video)
button2.pack()

# Create a button widget to stop the video
button3 = tk.Button(root, text="Stop Video", command=stop_video)
button3.pack()

button4 = tk.Button(root, text ="Traffic Light Exist", command=add_traffic_light_toDb)
button4.pack()

button5 = tk.Button(root, text ="Traffic Light Does Not Exist", command=add_not_traffic_light_toDb)
button5.pack()

# Run the event loop
root.mainloop()
