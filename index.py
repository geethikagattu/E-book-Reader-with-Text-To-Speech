import os
import threading
from playsound import playsound
from gtts import gTTS
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import webbrowser
import subprocess
import queue

selected_file = ""

def open_website():
    webbrowser.open("https://www.gutenberg.org")

# Queue to hold audio files
audio_queue = queue.Queue()

def play_audio():
    while True:
        filename = audio_queue.get()  # Get the next audio file from the queue
        if filename is None:  # Exit condition
            break
        playsound(filename)
        os.remove(filename)  # Remove the file after playing

def readbook(file_path):
    try:
        
        doc = fitz.open(file_path)
        print(f"Total pages: {doc.page_count}")

        for i in range(doc.page_count): 
            page = doc.load_page(i)
            read = page.get_text()
            
            # Check if there is text to read
            if not read.strip():  # If the text is empty or only whitespace
                print(f"Page {i} has no text.")
                continue  # Skip to the next page
            
            # Update the Text widget in the main thread
            root.after(0, update_text_widget, read)  # Schedule the update
            
            # Limit the text length for TTS
            if len(read) > 500:  # Adjust the limit as needed
                read = read[:500]  # Truncate to the first 500 characters
            
            tts = gTTS(text=read, lang="en")
            filename = f"voice{i}.mp3"
            tts.save(filename)
            audio_queue.put(filename)  # Add the filename to the queue

        messagebox.showinfo("Finished", "Finished reading the PDF")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_text_widget(text):
    pri.insert(tk.END, text + "\n")  # Insert the text into the Text widget
    pri.see(tk.END)  # Scroll to the end of the Text widget

def start_reading():
    if not selected_file:
        messagebox.showwarning("No File Selected", "Please select a book first.")
        return
    threading.Thread(target=readbook, args=(selected_file,)).start()

def open_book():
       try:
         subprocess.Popen(["open", "-a", "Books"])  # Open Apple Books
       except Exception as e:
          print(f"Error opening application: {e}")


def select_book():
    """Allows the user to select an EPUB file after opening Books."""
    global selected_file
    open_book()  # Open Apple Books first
    messagebox.showinfo("Instructions", "Select the book from Finder after opening Books.")
    
    file_path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub"), ("PDF Files", "*.pdf")])
    if file_path:
        selected_file = file_path
        messagebox.showinfo("Selected File", f"You selected: {file_path}")
          # Call your reading function
# Create the main window

def pause_book() :
    global stop_audio 
    stop_audio = threading.Event()
    stop_audio.set()
    audio_queue.put(None)
        
root = tk.Tk()
root.title("E-book Reader")
root.geometry("800x900")  # Set a geometry for the window

website_button = tk.Button(root, text="Open Book Website", command=open_website)
website_button.pack(pady=10)

pause = tk.Button(root , text = "Pause the book" , font = ("Times New Roman" , 12) , command = pause_book)

open_button = tk.Button(root, text="Select Book from Apple Books", command=select_book)
open_button.pack(pady=20)
# Create a button to start reading
start_button = tk.Button(root, text="Start Reading", command=start_reading)
start_button.pack(pady=20)

# Create a Text widget to display the PDF text
pri = tk.Text(root, font=("Times New Roman", 12))
pri.pack(expand=True, fill=tk.BOTH)


# Start a thread to play audio
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()

# Run the application
try:
    root.mainloop()
finally:
    # Stop the audio thread when the application closes
    audio_queue.put(None)  # Signal the audio thread to exit
    audio_thread.join()  # Wait for the audio thread to finish