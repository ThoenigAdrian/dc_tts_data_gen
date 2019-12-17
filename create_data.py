# coding=utf-8
text = """
Add your multineline text here
You can just paste a very long text and this script will split it up for you in ~10 second chunks
"""
import csv
from itertools import islice
import time
import os
import re
import pyaudio
import wave
import datetime
from num2words import num2words

CHUNK = 49
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
p = pyaudio.PyAudio()

def record_until_enter(file_name):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    time = datetime.datetime.now()
    raw_input("\n\n\nSpeak now ! Hit enter when finished !")
    time_passed = (datetime.datetime.now() - time).total_seconds()
    frames = []
    for i in range(0, int(float(RATE) / CHUNK * abs(time_passed))):  # -0.5 to get rid of abs as a safeguard
        data = stream.read(CHUNK)
        frames.append(data)
    print "* done recording"
    stream.stop_stream()
    stream.close()
    sample_size = p.get_sample_size(FORMAT)
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return frames, sample_size

data_path = "~/dc_tts_data_own/LJSpeech-1.1"
wav_path = "~/dc_tts_data_own/LJSpeech-1.1/wavs"


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def normalize_text(text):
    norm_t = ""
    for word in text.split(" "):
        word = word.replace(":", "")
        word = word.replace("%", " percent")
        word = word.replace("'", "")
        word = word.replace('"', "")
        word = word.replace("’", "")
        word = word.replace("”", "")
        word = word.replace("/", " slash ")
        try:
            nr = int(word)
            if 1300 < nr < 3000:
                word = num2words(nr, to="year")# assume it's a year
                word = word.encode("ascii")
            else:
                word = num2words(nr)# assume it's a number
                word = word.encode("ascii")
        except ValueError:
            if word.endswith("s"):
                try:
                    nr = int(word.strip("s"))
                    if 1300 < nr < 3000:
                        word = num2words(nr, to="year")  # assume it's a year
                        word += "s"
                        word = word.encode("ascii")
                    else:
                        word = num2words(nr)  # assume it's a number
                        word += "s"
                        word = word.encode("ascii")
                except ValueError:
                    pass
        if any(word.startswith(nr) for nr in "0123456789"):
            # Assume this is a composition word like 3D or 2D or 5x
            num = re.search(r'(\d+)', word).group(0)
            word = num2words(num).encode("ascii") + " " + word[len(num):]

        norm_t += word + " "
    return norm_t

print "**Checking if all text can be normalized"
for index, text_to_speak in enumerate(chunk(text.split(" "), 18)):
    text_to_speak_str = " ".join(text_to_speak).replace("\n", " ")
    normalize_text(text_to_speak_str)
print "** Normalization successfull"


with open(os.path.join(data_path, "metadata.csv"), 'r') as metadata:
    reader = csv.reader(metadata, delimiter='|', quoting=csv.QUOTE_NONE)
    already_existing = row_count = sum(1 for row in reader)



with open(os.path.join(data_path, "metadata.csv"), 'a') as metadata:
    metadata_writer = csv.writer(metadata, delimiter='|', quoting=csv.QUOTE_NONE)
    for index, text_to_speak in enumerate(chunk(text.split(" "), 18)):
        text_to_speak_str = " ".join(text_to_speak).replace("\n", " ")
        print "\n\n" + text_to_speak_str
        time.sleep(1)
        wav_file_name = "LJ001-" + str(index + already_existing).zfill(4) + ".wav"

        record_until_enter(os.path.join(wav_path, wav_file_name))
        metadata_writer.writerow([wav_file_name.split(".wav")[0], text_to_speak_str, normalize_text(text_to_speak_str)])

p.terminate()