import os
import time
import playsound
from gtts import gTTS
import fitz

doc = fitz.open("/Users/geethikagattu/Desktop/python project/A-Good-Girls-Guide-Series.pdf")
print(doc.page_count)

for i in range(13 ,doc.page_count): 
 page = doc.load_page(i)
 print(page.get_text())
 read = page.get_text()
 tts = gTTS(text = read , lang = "en")
 filename = "voice.mp3"
 tts.save(filename)
 playsound.playsound(filename)
