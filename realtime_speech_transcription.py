import pyaudio
import audioop
import requests
import wave
import time
from collections import deque

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
THRESHOLD = 2000  # audio level threshold for starting recording
SILENCE_LIMIT = 1  # silence time to consider end of a chunk
PREV_AUDIO = 0.5  # seconds of audio kept before start of a chunk

def listen_for_speech(threshold=THRESHOLD):
    """
    Listen to the microphone and send chunks of speech to the speech-to-text service.
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
            send_audio_to_stt(filename)
            audio2send = []
            prev_audio = deque(maxlen=int(PREV_AUDIO * rel))  # reset the buffer
            started = False
            slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
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
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data))
    wf.close()
    return filename

def send_audio_to_stt(filename):
    """
    Send the audio file to the Speech to Text service and print the response.
    """
    url = 'http://localhost:5001/speech-to-text'
    headers = {'Content-Type': 'audio/wav'}
    with open(filename, 'rb') as f:
        audio_data = f.read()
    response = requests.post(url, data=audio_data, headers=headers)
    print("Transcription: ")
    print(response.text)

listen_for_speech()  # Uncomment to start listening
