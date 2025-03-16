import os
import time
import threading
from playsound import playsound
from gtts import gTTS
import fitz
import tkinter as tk 
from tkinter import messagebox
import queue

def readbook():
    try:
        doc = fitz.open("/Users/geethikagattu/Desktop/python project/sample (2).pdf")
        print(doc.page_count)

        for i in range(0, doc.page_count): 
            page = doc.load_page(i)
            print(page.get_text())
            read = page.get_text()
            tts = gTTS(text=read, lang="en")
            filename = f"voice{i}.mp3"
            tts.save(filename)
            playsound(filename)
            os.remove(filename)

        messagebox.showinfo("Finished", "Finished reading the pdf")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def start_reading():
    threading.Thread(target=readbook).start()

root = tk.Tk()
root.title("E-book Reader")
root.geometry("300x200")

# Add a button to start reading (not in your original request, but necessary for functionality)
start_button = tk.Button(root, text="Start Reading", command=start_reading)
start_button.pack(pady=20)

root.mainloop()