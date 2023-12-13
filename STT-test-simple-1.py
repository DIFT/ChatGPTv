import azure.cognitiveservices.speech as speechsdk
import requests
import json
import os
import subprocess

# Retrieve API keys and regions from environment variables
stt_speech_key = os.getenv('STT_SPEECH_KEY')
service_region = os.getenv('SERVICE_REGION')
tts_speech_key = os.getenv('TTS_SPEECH_KEY')
tts_service_region = os.getenv('TTS_SERVICE_REGION')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize the speech configuration for Speech-to-Text
speech_config_stt = speechsdk.SpeechConfig(subscription=stt_speech_key, region=service_region)

# Initialize the audio configuration for Speech-to-Text
audio_config_stt = speechsdk.AudioConfig(use_default_microphone=True)

# Initialize the speech recognizer for Speech-to-Text
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config_stt, audio_config=audio_config_stt)

# Recognize the audio and get the transcribed text
result = speech_recognizer.recognize_once()

if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    transcribed_text = result.text
    print("Transcribed Text: {}".format(transcribed_text))
    
    # Initialize data for OpenAI API
    openai_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": transcribed_text}
        ]
    }

    # Make a request to OpenAI's API
    openai_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    openai_response = requests.post(openai_url, data=json.dumps(openai_data), headers=headers)
    
    if openai_response.status_code == 200:
        chatgpt_response = openai_response.json()["choices"][0]["message"]["content"]
        print("ChatGPT Response: {}".format(chatgpt_response))
        
        # Initialize the speech configuration for Text-to-Speech
        speech_config_tts = speechsdk.SpeechConfig(subscription=tts_speech_key, region=tts_service_region)

        # Updated SSML string with facial expression viseme
        ssml_string = f"""
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>
  <voice name='en-US-JennyNeural'>
    <mstts:viseme type='FacialExpression'/>
    {chatgpt_response}
  </voice>
</speak>
"""

        # Send the SSML data to your Unity project via named pipe
        try:
            with open('my_pipe', 'w') as pipe:
                pipe.write(ssml_string)
            print("SSML data sent to Unity for facial expression animation.")
        except Exception as e:
            print(f"Failed to send SSML data to Unity via named pipe: {e}")
    else:
        print("OpenAI API request failed.")
else:
    print("Speech Recognition failed with unexpected reason: {}".format(result.reason))
