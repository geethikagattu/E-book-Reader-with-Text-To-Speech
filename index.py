import os
import time
import playsound
import speech_recognition as sr  
from gtts import gTTS
import fitz

# def speak(text):
#     tts = gTTS(text = text , lang = "te")
#     filename = "voice.mp3"
#     tts.save(filename)
#     playsound.playsound(filename)

# speak("హలో, మీరు ఎలా ఉన్నారు?")

doc = fitz.open("/Users/geethikagattu/Desktop/python project/sample.pdf")
print(doc.page_count)

page = doc.load_page(0)
print(page.get_text())
read = page.get_text()

tts = gTTS(text = read , lang = "en")
filename = "voice.mp3"
tts.save(filename)
playsound.playsound(filename)
