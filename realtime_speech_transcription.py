import pyaudio
import audioop
import requests
import wave
import time
from collections import deque
import sys

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
THRESHOLD = 2000  # audio level threshold for starting recording
SILENCE_LIMIT = 1  # silence time to consider end of a chunk
PREV_AUDIO = 0.5  # seconds of audio kept before start of a chunk

# URLs for Speech to Text (STT) and Text to Speech (TTS) containers
STT_URL = 'http://localhost:5001'
TTS_URL = 'http://localhost:5002'

def listen_for_speech(threshold=THRESHOLD):
    """
    Listen to the microphone and send chunks of speech to the STT service.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("* Listening. Speak now.")
    audio2send = []
    cur_data = ''  # current chunk of audio data
    rel = RATE / CHUNK
    slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
    prev_audio = deque(maxlen=int(PREV_AUDIO * rel))  # previous audio buffer

    started = False

    while True:
        cur_data = stream.read(CHUNK)
        slid_win.append(abs(audioop.avg(cur_data, 4)))

        if sum([x > threshold for x in slid_win]) > 0:
            if not started:
                print("Starting recording")
                started = True
            audio2send.append(cur_data)
        elif started:
            print("Finished recording, processing chunk")
            filename = save_speech(list(prev_audio) + audio2send, p)
            transcribed_text = send_audio_to_stt(filename)
            audio2send = []
            prev_audio = deque(maxlen=int(PREV_AUDIO * rel))  # reset the buffer
            started = False
            slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))

            # Send transcribed text to TTS container
            tts_audio_data = send_text_to_tts(transcribed_text)
            # You can save or play the synthesized audio as needed
            save_tts_audio(tts_audio_data)
        else:
            prev_audio.append(cur_data)

    print("* Done recording")
    stream.close()
    p.terminate()

def save_speech(data, p):
    """
    Save the recorded speech data to a file.
    """
    filename = 'output_' + str(int(time.time())) + '.wav'
    print("Saving .wav file to:", filename)  # Debugging statement to print filename and directory
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data))
    wf.close()
    return filename

def send_audio_to_stt(filename):
    """
    Send the audio file to the STT service and return the transcribed text.
    """
    headers = {'Content-Type': 'audio/wav'}
    with open(filename, 'rb') as f:
        audio_data = f.read()
    response = requests.post(STT_URL, data=audio_data, headers=headers)
    transcribed_text = response.text.strip()
    print("Transcription: ")
    print(transcribed_text)
    return transcribed_text

def send_text_to_tts(text):
    """
    Send the transcribed text to the TTS service and return the synthesized audio data.
    """
    headers = {'Content-Type': 'text/plain'}
    response = requests.post(TTS_URL, data=text, headers=headers)
    tts_audio_data = response.content
    return tts_audio_data

def save_tts_audio(data):
    """
    Save the synthesized audio data to a file.
    """
    filename = 'output_tts.wav'
    print("Saving TTS .wav file to:", filename)  # Debugging statement to print filename and directory
    with open(filename, 'wb') as tts_file:
        tts_file.write(data)

if __name__ == "__main__":
    listen_for_speech()  # Uncomment to start listening
