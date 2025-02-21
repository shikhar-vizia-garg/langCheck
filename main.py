from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, jsonify
import streamlit as st
import sounddevice as sd
import wavio
from pydub import AudioSegment
import threading
import requests
import numpy as np
import os

app = Flask(__name__)

# Global variables for recording control
recording = False
recorded_data = []


def callback(indata, frames, time, status):
    if status:
        print(status)
    if recording:
        recorded_data.append(indata.copy())


def record_audio(filename="output.wav", samplerate=44100):
    global recording, recorded_data
    print("Recording... Speak now!")
    recorded_data = []
    recording = True
    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback):
        while recording:
            sd.sleep(100)

    if recorded_data:
        recorded_array = np.concatenate(recorded_data, axis=0)  # Concatenate all recorded frames
        wavio.write(filename, recorded_array, samplerate, sampwidth=2)
        print("Recording finished!")
    else:
        print("No audio recorded.")
    print("Recording finished!")


@app.route("/start_recording", methods=["POST"])
def start_recording():
    threading.Thread(target=record_audio, args=("output.wav",)).start()
    return jsonify({"message": "Recording started"})


@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    global recording
    recording = False
    return jsonify({"message": "Recording stopped"})


def convert_to_mp3(wav_filename="output.wav", mp3_filename="output.mp3"):
    print("Converting to MP3...")
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")
    print(f"Conversion completed: {mp3_filename}")


def correct_grammar(text, client):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that corrects grammar."},
            {"role": "user", "content": f"Correct the grammar of the following text:\n\n{text}"}
        ],
        temperature=0.0,
    )
    corrected_text = response.choices[0].message.content.strip()
    return corrected_text


@app.route("/process_audio", methods=["POST"])
def process_audio():
    load_dotenv()
    client = OpenAI()

    convert_to_mp3("output.wav", "output.mp3")
    os.remove("output.wav")  # Cleanup the wav file after conversion

    audio_file = open("output.mp3", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    input_text = transcription.text
    output_text = correct_grammar(input_text, client)

    speech_file_path = Path(os.path.abspath(os.getcwd())) / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=output_text,
    )
    response.stream_to_file(speech_file_path)

    return jsonify({"input_text": input_text, "output_text": output_text, "speech_file": str(speech_file_path)})


# Streamlit Interface
def streamlit_ui():
    st.title("Laura Lite")
    col1, col2, col3 = st.columns(3)  # Arrange buttons horizontally

    with col1:
        if st.button("Start Recording"):
            requests.post("http://127.0.0.1:5000/start_recording")
            st.write("Recording started...")

    with col2:
        if st.button("Stop Recording"):
            requests.post("http://127.0.0.1:5000/stop_recording")
            st.write("Recording stopped...")

    with col3:
        if st.button("Process Recording"):

            response = requests.post("http://127.0.0.1:5000/process_audio")
            # Debugging step: Print response before parsing
            st.write("Raw Response:", response.text)
            try:
                data = response.json()
                st.write("Recording processed...")
                st.write("Original Text:", data.get("input_text"))
                st.write("Corrected Text:", data.get("output_text"))
                st.audio(data.get("speech_file"))
            except requests.exceptions.JSONDecodeError:
                st.error("Error: Received invalid response from server. Check Flask logs.")


if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()
    streamlit_ui()
