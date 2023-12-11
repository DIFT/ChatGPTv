import pyaudio
import wave
import requests
import os

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 10  # Duration for recording

# Azure Speech to Text Configuration
SPEECH_SERVICE_ENDPOINT = 'https://eastus.api.cognitive.microsoft.com/'  # Replace <region> with your Azure region
SPEECH_SERVICE_KEY = '9ee891ae0ff249c680e9de43f4ac1f4b'  # Replace with your actual API key

def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=1024)
    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / 1024 * RECORD_SECONDS)):
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    return b''.join(frames)

def save_audio_to_file(audio_data, filename='output.wav'):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)  # Adjust based on the format (paInt16)
    wf.setframerate(RATE)
    wf.writeframes(audio_data)
    wf.close()

def send_audio_to_stt(audio_data):
    headers = {
        'Authorization': 'Bearer ' + SPEECH_SERVICE_KEY,
        'Content-Type': 'audio/wav',
    }
    response = requests.post(SPEECH_SERVICE_ENDPOINT, data=audio_data, headers=headers)
    print("Transcription: ")
    print(response.text.strip())

if __name__ == "__main__":
    audio_data = record_audio()
    audio_filename = 'output.wav'
    save_audio_to_file(audio_data, audio_filename)
    send_audio_to_stt(audio_data)
