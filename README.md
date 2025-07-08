# 📚🎧 Ebook Reader with Text-to-Speech (TTS)

This project is a simple yet effective **Ebook Reader** that converts written text into spoken audio using **Text-to-Speech (TTS)** technology. It's designed to help users listen to their favorite ebooks or text files hands-free.

---

## 📌 Project Objective

To develop a Python-based ebook reader that:
- Loads `.txt` files (or other text-based formats)
- Reads the content aloud using TTS
- Enhances accessibility and multitasking

---

## 🛠️ Technologies Used

- **Python**
- **pyttsx3** – Offline TTS engine
- **tkinter / file input** – For basic UI or file selection (optional)
- **Pandas / Regex** – For text processing (if needed)

---

## 🚀 Features

- 📖 Load text-based ebooks
- 🔊 Read aloud using system voice
- ⏸️ Pause/resume/stop (optional controls)
- 🎚 Adjustable speech rate and voice

---

## 📂 Example Project Structure

ebook-tts-reader/
├── reader.py # Main Python script
├── sample_book.txt # Example ebook file
├── README.md # Project documentation
└── requirements.txt # Dependencies
---

## ▶️ How to Run

1. **Install dependencies**
pip install pyttsx3
Run the script
python reader.py
Follow the prompt to load a .txt file and enjoy listening!

##🔧 Sample Code Snippet

import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)

with open('sample_book.txt', 'r') as file:
    text = file.read()

engine.say(text)
engine.runAndWait()
👀 Use Cases
For visually impaired users

Audiobook-style reading on the go

Background listening while working/studying

##🧠 Future Enhancements
Add GUI for file selection (Tkinter or PyQt)

Support for PDF/EPUB formats

Voice selection and playback control

Export audio to .mp3

##👤 Author
Geethika Reddy Gattu
B.Tech CSE @ SRM University AP
Passionate about accessibility tech and Python projects

##📄 License
Open-source under the MIT License
