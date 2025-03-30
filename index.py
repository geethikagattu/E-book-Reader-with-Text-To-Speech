import os
import threading
import queue
import webbrowser
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk  # Import ttk for Combobox
from gtts import gTTS
import fitz  # PyMuPDF
from pydub import AudioSegment
from pydub.playback import play
import time
import pyttsx3
import customtkinter as ctk
from PIL import Image 
import shutil
import sqlite3

selected_file = ""
engine = pyttsx3.init()
voices = engine.getProperty('voices')
voice_options = {voice.name: voice.id for voice in voices}
stop_audio = threading.Event()
paused = threading.Event()

audio_queue = queue.Queue()
bookmarks = set()
notes = {}

current_page = 0  # Track the current page number

def open_website():
    webbrowser.open("https://www.gutenberg.org")

def play_audio():
    """Plays audio files from the queue using pydub with pause & resume functionality."""
    while True:
        filename = audio_queue.get()
        if filename is None:
            break

        audio = AudioSegment.from_mp3(filename)

        while paused.is_set():
            time.sleep(0.5)

        if stop_audio.is_set():
            break

        play(audio)

        os.remove(filename)

def readbook(file_path):
    """Reads the book, extracts text, converts to speech, and plays the audio."""
    global current_page
    try:
        doc = fitz.open(file_path)
        print(f"Total pages: {doc.page_count}")

        for i in range(doc.page_count):
            if stop_audio.is_set():
                break

            current_page = i  # Track current page
            page = doc.load_page(i)
            read = page.get_text()

            if not read.strip():
                print(f"Page {i} has no text.")
                continue

            root.after(0, update_text_widget, read, i)

            read = read[:500] if len(read) > 500 else read

            tts = gTTS(text=read, lang="en")
            filename = f"voice{i}.mp3"
            tts.save(filename)
            audio_queue.put(filename)

        messagebox.showinfo("Finished", "Finished reading the book")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_text_widget(text, page_num):
    """Updates the text display widget with page number."""
    text_display.insert(tk.END, f"\n--- Page {page_num} ---\n\n{text}\n")
    text_display.see(tk.END)  # Scroll to the end of the text

def start_reading():
    """Starts reading the selected book."""
    if not selected_file:
        messagebox.showwarning("No File Selected", "Please select a book first.")
        return

    stop_audio.clear()
    paused.clear()
    threading.Thread(target=readbook, args=(selected_file,)).start()

def open_book():
    """Opens Apple Books application."""
    try:
        subprocess.Popen(["open", "-a", "Books"])
    except Exception as e:
        print(f"Error opening application: {e}")

def select_book():
    """Allows the user to select a book file."""
    global selected_file
    open_book()
    messagebox.showinfo("Instructions", "Select the book from Finder after opening Books.")

    file_path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub"), ("PDF Files", "*.pdf")])
    if file_path:
        selected_file = file_path
        messagebox.showinfo("Selected File", f"You selected: {file_path}")

def pause_book():
    """Pauses audio playback."""
    paused.set()

def resume_book():
    """Resumes audio playback."""
    paused.clear()

def stop_book():
    """Stops audio playback completely."""
    stop_audio.set()
    paused.clear()
    audio_queue.put(None)

def highlight_text():
    """Highlights selected text."""
    try:
        selected_text = text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
        text_display.tag_add("highlight", tk.SEL_FIRST, tk.SEL_LAST)
        text_display.tag_config("highlight", background="yellow", foreground="black")
    except tk.TclError:
        messagebox.showwarning("Selection Error", "Please select text to highlight.")

def add_note():
    """Adds a note to the current page."""
    global notes
    note_text = simpledialog.askstring("Add Note", "Enter your note:")
    if note_text:
        notes[current_page] = note_text
        messagebox.showinfo("Note Saved", f"Note added to page {current_page}")

def view_notes():
    """Displays notes for the current page."""
    note = notes.get(current_page, "No notes for this page.")
    messagebox.showinfo("Notes", f"Page {current_page} Notes:\n{note}")

def bookmark_page():
    """Bookmarks the current page."""
    bookmarks.add(current_page)
    messagebox.showinfo("Bookmarked", f"Page {current_page} bookmarked.")

def view_bookmarks():
    """Displays all bookmarked pages."""
    if not bookmarks:
        messagebox.showinfo("Bookmarks", "No bookmarks added.")
    else:
        bookmark_list = ", ".join(map(str, sorted(bookmarks)))
        messagebox.showinfo("Bookmarks", f"Bookmarked Pages: {bookmark_list}")

def set_voice(voice_name):
    """Sets the selected voice."""
    global selected_voice
    selected_voice = voice_options[voice_name]
    engine.setProperty('voice', selected_voice)

def set_speed(speed):
    """Sets the reading speed."""
    global speech_rate
    rates = {"Slow": 100, "Normal": 150, "Fast": 200}
    speech_rate = rates[speed]
    engine.setProperty('rate', speech_rate)

def set_pitch(pitch_value):
    """Sets the pitch level."""
    global pitch
    pitch = pitch_value
    engine.setProperty('pitch', pitch)  # Some engines support pitch adjustment

def speak_text(text):
    """Speaks the given text using pyttsx3 without blocking the main loop."""
    engine.setProperty('voice', selected_voice)
    engine.setProperty('rate', speech_rate)
    
    if not stop_audio.is_set():
        engine.say(text)
        engine.runAndWait()

def save_book():
    """Saves the book to the device."""
    if not selected_file:
        messagebox.showwarning("No File Selected", "Please select a book first.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                             filetypes=[("PDF Files", "*.pdf")], 
                                             title="Save Book")
    
    if not save_path:
        return  # User canceled save

    try:
        shutil.copy(selected_file, save_path)
        messagebox.showinfo("Saved", f"Book saved to:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save book: {str(e)}")


ctk.set_appearance_mode("dark")  # Can be "light" or "dark"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
# Create the main window
ctk.set_appearance_mode("Dark")  # Set theme
root = ctk.CTk()
root.title("E-book Reader")
root.geometry("800x900")

left_frame = ctk.CTkFrame(root, width=200, corner_radius=10)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = ctk.CTkFrame(root, width=200, corner_radius=10)
right_frame.pack(side="right", fill="y", padx=10, pady=10)

center_frame = ctk.CTkFrame(root)
center_frame.pack(expand=True, fill="both", padx=10, pady=10)

text_display = ctk.CTkTextbox(center_frame, font=("Times New Roman", 12), wrap="word")
text_display.pack(expand=True, fill="both", padx=10, pady=10)

# Left Panel Buttons (Book Operations)
logo_img_data = Image.open("book_pink.png")  # Open image using PIL
logo_img = ctk.CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(78, 85))

logo_label = ctk.CTkLabel(left_frame, image=logo_img, text="")
logo_label.pack(pady=10)

ctk.CTkButton(left_frame, text="Select Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=select_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Open Book Website",hover_color="#FFB6C1", fg_color="#F48FB1", command=open_website).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Save Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=save_book).pack(pady=5, padx=10, fill="x")
# ctk.CTkButton(left_frame, text="Categorize E-Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=categorize_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Add Note",hover_color="#FFB6C1", fg_color="#F48FB1", command=add_note).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="View Note",hover_color="#FFB6C1", fg_color="#F48FB1", command=view_notes).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Bookmark Page",hover_color="#FFB6C1", fg_color="#F48FB1", command=bookmark_page).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Bookmark Page",hover_color="#FFB6C1", fg_color="#F48FB1", command=view_bookmarks).pack(pady=5, padx=10, fill="x")


ctk.CTkButton(right_frame, text="Start Reading",hover_color="#FFB6C1", fg_color="#F48FB1", command=start_reading).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Pause",hover_color="#FFB6C1", fg_color="#F48FB1", command=pause_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Resume",hover_color="#FFB6C1", fg_color="#F48FB1", command=resume_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Stop",hover_color="#FFB6C1", fg_color="#F48FB1", command=stop_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Highlight Text",hover_color="#FFB6C1", fg_color="#F48FB1", command=highlight_text).pack(pady=5, padx=10, fill="x")
# ctk.CTkButton(right_frame, text="Search Text",hover_color="#FFB6C1", fg_color="#F48FB1", command=search_text).pack(pady=5, padx=10, fill="x")


# Voice Selection Dropdown
voice_label = tk.Label(right_frame, text="Select Voice:")
voice_label.pack(pady=5)

voice_dropdown = ttk.Combobox(right_frame, values=list(voice_options.keys()), state="readonly")
voice_dropdown.pack(pady=5)
voice_dropdown.set(list(voice_options.keys())[0])  # Default selection
voice_dropdown.bind("<<ComboboxSelected>>", lambda e: set_voice(voice_dropdown.get()))

# Speed Selection Dropdown
speed_label = tk.Label(right_frame, text="Select Speed:")
speed_label.pack(pady=5)

speed_dropdown = ttk.Combobox(right_frame, values=["Slow", "Normal", "Fast"], state="readonly")
speed_dropdown.pack(pady=5)
speed_dropdown.set("Normal")  # Default speed
speed_dropdown.bind("<<ComboboxSelected>>", lambda e: set_speed(speed_dropdown.get()))

# Pitch Selection Dropdown
pitch_label = tk.Label(right_frame, text="Select Pitch:")
pitch_label.pack(pady=5)

pitch_dropdown = ttk.Combobox(right_frame, values=["Low", "Normal", "High"], state="readonly")
pitch_dropdown.pack(pady=5)
pitch_dropdown.set("Normal")  # Default pitch
pitch_dropdown.bind("<<ComboboxSelected>>", lambda e: set_pitch(pitch_dropdown.get()))


# Start a thread to play audio
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()


# Run the application
try:
    root.mainloop()
finally:
    stop_audio.set()
    audio_queue.put(None)
    audio_thread.join()

def start_reading():
    """Starts reading the selected book."""
    if not selected_file:
        messagebox.showwarning("No File Selected", "Please select a book first.")
        return

    stop_audio.clear()
    paused.clear()
    threading.Thread(target=readbook, args=(selected_file,)).start()

def open_book():
    """Opens Apple Books application."""
    try:
        subprocess.Popen(["open", "-a", "Books"])
    except Exception as e:
        print(f"Error opening application: {e}")

def select_book():
    """Allows the user to select a book file."""
    global selected_file
    open_book()
    messagebox.showinfo("Instructions", "Select the book from Finder after opening Books.")

    file_path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub"), ("PDF Files", "*.pdf")])
    if file_path:
        selected_file = file_path
        messagebox.showinfo("Selected File", f"You selected: {file_path}")

def pause_book():
    """Pauses audio playback."""
    paused.set()

def resume_book():
    """Resumes audio playback."""
    paused.clear()

def stop_book():
    """Stops audio playback completely."""
    stop_audio.set()
    paused.clear()
    audio_queue.put(None)

def highlight_text():
    """Highlights selected text."""
    try:
        selected_text = text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
        text_display.tag_add("highlight", tk.SEL_FIRST, tk.SEL_LAST)
        text_display.tag_config("highlight", background="yellow", foreground="black")
    except tk.TclError:
        messagebox.showwarning("Selection Error", "Please select text to highlight.")

def add_note():
    """Adds a note to the current page."""
    global notes
    note_text = simpledialog.askstring("Add Note", "Enter your note:")
    if note_text:
        notes[current_page] = note_text
        messagebox.showinfo("Note Saved", f"Note added to page {current_page}")

def view_notes():
    """Displays notes for the current page."""
    note = notes.get(current_page, "No notes for this page.")
    messagebox.showinfo("Notes", f"Page {current_page} Notes:\n{note}")

def bookmark_page():
    """Bookmarks the current page."""
    bookmarks.add(current_page)
    messagebox.showinfo("Bookmarked", f"Page {current_page} bookmarked.")

def view_bookmarks():
    """Displays all bookmarked pages."""
    if not bookmarks:
        messagebox.showinfo("Bookmarks", "No bookmarks added.")
    else:
        bookmark_list = ", ".join(map(str, sorted(bookmarks)))
        messagebox.showinfo("Bookmarks", f"Bookmarked Pages: {bookmark_list}")

def set_voice(voice_name):
    """Sets the selected voice."""
    global selected_voice
    selected_voice = voice_options[voice_name]
    engine.setProperty('voice', selected_voice)

def set_speed(speed):
    """Sets the reading speed."""
    global speech_rate
    rates = {"Slow": 100, "Normal": 150, "Fast": 200}
    speech_rate = rates[speed]
    engine.setProperty('rate', speech_rate)

def set_pitch(pitch_value):
    """Sets the pitch level."""
    global pitch
    pitch = pitch_value
    engine.setProperty('pitch', pitch)  # Some engines support pitch adjustment

def speak_text(text):
    """Speaks the given text using pyttsx3 without blocking the main loop."""
    engine.setProperty('voice', selected_voice)
    engine.setProperty('rate', speech_rate)
    
    if not stop_audio.is_set():
        engine.say(text)
        engine.runAndWait()

def search_text():
    query = simpledialog.askstring("Search", "Enter text to search:")
    if not query:
        return

    text_display.tag_remove("search", "1.0", tk.END)  # Remove old highlights
    start_pos = "1.0"
    found = False  # Flag to check if any matches are found

    while True:
        start_pos = text_display.search(query, start_pos, stopindex=tk.END, nocase=True)
        if not start_pos:
            break  # No more matches found

        end_pos = f"{start_pos}+{len(query)}c"
        text_display.tag_add("search", start_pos, end_pos)
        start_pos = end_pos
        found = True  # At least one match was found

    text_display.tag_config("search", background="lightblue")  # Highlight matches

    if not found:
        messagebox.showinfo("Search Result", "No matches found.")

def categorize_books():
    """Allows the user to select a book file and categorize it."""
    global selected_file
    file_path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub"), ("PDF Files", "*.pdf")])
    if file_path:
        selected_file = file_path
        category = simpledialog.askstring("Categorize Book", "Enter category (e.g., Fiction, Study):")
        if category:
            save_book_with_category(selected_file, category)
            messagebox.showinfo("Selected File", f"You selected: {file_path}\nCategory: {category}")

def save_book_with_category(file_path, category):
    """Saves the book path and category to the database."""
    conn = sqlite3.connect("ebooks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, category, path) VALUES (?, ?, ?)", 
                   (os.path.basename(file_path), category, file_path))
    conn.commit()
    conn.close()

def create_database():
    """Creates the database and the books table if it doesn't exist."""
    conn = sqlite3.connect("ebooks.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        path TEXT NOT NULL)''')
    conn.commit()
    conn.close()

ctk.set_appearance_mode("dark")  # Can be "light" or "dark"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
# Create the main window
ctk.set_appearance_mode("Dark")  # Set theme
root = ctk.CTk()
root.title("E-book Reader")
root.geometry("900x600")

left_frame = ctk.CTkFrame(root, width=200, corner_radius=10)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = ctk.CTkFrame(root, width=200, corner_radius=10)
right_frame.pack(side="right", fill="y", padx=10, pady=10)

center_frame = ctk.CTkFrame(root)
center_frame.pack(expand=True, fill="both", padx=10, pady=10)

text_display = ctk.CTkTextbox(center_frame, font=("Times New Roman", 12), wrap="word")
text_display.pack(expand=True, fill="both", padx=10, pady=10)

# Left Panel Buttons (Book Operations)
logo_img_data = Image.open("book_pink.png")  # Open image using PIL
logo_img = ctk.CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(78, 85))

logo_label = ctk.CTkLabel(left_frame, image=logo_img, text="")
logo_label.pack(pady=10)

ctk.CTkButton(left_frame, text="Select Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=select_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Open Book Website",hover_color="#FFB6C1", fg_color="#F48FB1", command=open_website).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Save Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=save_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Categorize E-Book",hover_color="#FFB6C1", fg_color="#F48FB1", command=categorize_books).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Add Note",hover_color="#FFB6C1", fg_color="#F48FB1", command=add_note).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="View Note",hover_color="#FFB6C1", fg_color="#F48FB1", command=view_notes).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Bookmark Page",hover_color="#FFB6C1", fg_color="#F48FB1", command=bookmark_page).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(left_frame, text="Bookmark Page",hover_color="#FFB6C1", fg_color="#F48FB1", command=view_bookmarks).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Search Text",hover_color="#FFB6C1", fg_color="#F48FB1", command=search_text).pack(pady=5, padx=10, fill="x")


ctk.CTkButton(right_frame, text="Start Reading",hover_color="#FFB6C1", fg_color="#F48FB1", command=start_reading).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Pause",hover_color="#FFB6C1", fg_color="#F48FB1", command=pause_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Resume",hover_color="#FFB6C1", fg_color="#F48FB1", command=resume_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Stop",hover_color="#FFB6C1", fg_color="#F48FB1", command=stop_book).pack(pady=5, padx=10, fill="x")
ctk.CTkButton(right_frame, text="Highlight Text",hover_color="#FFB6C1", fg_color="#F48FB1", command=highlight_text).pack(pady=5, padx=10, fill="x")



# Voice Selection Dropdown
voice_label = tk.Label(right_frame, text="Select Voice:")
voice_label.pack(pady=5)

voice_dropdown = ttk.Combobox(right_frame, values=list(voice_options.keys()), state="readonly")
voice_dropdown.pack(pady=5)
voice_dropdown.set(list(voice_options.keys())[0])  # Default selection
voice_dropdown.bind("<<ComboboxSelected>>", lambda e: set_voice(voice_dropdown.get()))

# Speed Selection Dropdown
speed_label = ctk.CTkLabel(right_frame, text="Select Speed:")
speed_label.pack(pady=5)

speed_dropdown = ttk.Combobox(right_frame, values=["Slow", "Normal", "Fast"], state="readonly")
speed_dropdown.pack(pady=5)
speed_dropdown.set("Normal")  # Default speed
speed_dropdown.bind("<<ComboboxSelected>>", lambda e: set_speed(speed_dropdown.get()))

# Pitch Selection Dropdown
pitch_label = ctk.CTkLabel(right_frame, text="Select Pitch:")
pitch_label.pack(pady=5)

pitch_dropdown = ttk.Combobox(right_frame, values=["Low", "Normal", "High"], state="readonly")
pitch_dropdown.pack(pady=5)
pitch_dropdown.set("Normal")  # Default pitch
pitch_dropdown.bind("<<ComboboxSelected>>", lambda e: set_pitch(pitch_dropdown.get()))


# Start a thread to play audio
audio_thread = threading.Thread(target=play_audio)
audio_thread.start()


# Run the application
try:
    root.mainloop()
finally:
    stop_audio.set()
    audio_queue.put(None)
    audio_thread.join()