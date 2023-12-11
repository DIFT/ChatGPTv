import azure.cognitiveservices.speech as speechsdk
import requests
import json

# Azure Speech API key and region for Speech-to-Text
stt_speech_key = '9ee891ae0ff249c680e9de43f4ac1f4b'
service_region = 'eastus'

# Azure Speech API key and region for Text-to-Speech
tts_speech_key = 'bdc956edb9c246cd9b242ae6b45b12c9'
tts_service_region = 'eastus'

# OpenAI API key
openai_api_key = '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'

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
        
        # Initialize the synthesizer for Text-to-Speech
        tts_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config_tts)
        
        # Synthesize ChatGPT's response into speech
        result = tts_synthesizer.speak_text_async(chatgpt_response).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Save the synthesized audio as a WAV file
            with open('chatgpt_response.wav', 'wb') as audio_file:
                audio_file.write(result.audio_data)
            print("ChatGPT response saved as chatgpt_response.wav")
        else:
            print("Text-to-Speech synthesis failed with unexpected reason: {}".format(result.reason))
    else:
        print("OpenAI API request failed.")
else:
    print("Speech Recognition failed with unexpected reason: {}".format(result.reason))
