import requests
import base64
import os
import time
import threading
from Interrupted_Playsound import play_audios

def ElevenlabsTTS(text: str, voice: str = "Brian", filename: str = "STREAM_AUDIOS/output_audio", verbose: bool = True):
    available_voices = {"Brian": "nPczCjzI2devNBz1zQrb", "Alice":"Xb7hH8MSUJpSbSDYk0k2", "Bill":"pqHfZKP75CvOlQylNhV4", "Callum":"N2lVS1w4EtoT3dr4eOWO", "Charlie":"IKne3meq5aSn9XLyUdCD", "Charlotte":"XB0fDUnXU5powFXDhCwa", "Chris":"iP95p4xoKVk53GoZ742B", "Daniel":"onwK4e9ZLuTAKqWW03F9", "Eric":"cjVigY5qzO86Huf0OWal", "George":"JBFqnCBsd6RMkjVDRZzb", "Jessica":"cgSgspJ2msm6clMCkdW9", "Laura":"FGY2WhTYpPnrIDTdsKH5", "Liam":"TX3LPaxmHKxFdv7VOQHJ", "Lily":"pFZP5JQG7iQjIQuC4Bku", "Matilda":"XrExE9yKIg1WjnnlVkGX", "Sarah":"EXAVITQu4vr4xnSDxMaL", "Will":"bIHbv24MWmeRgasZH58o"}

    if voice not in available_voices.keys():
        return f"Invalid voice name. Available voices are: {', '.join(list(available_voices.keys()))}"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://elevenlabs.io',
        'priority': 'u=1, i',
        'referer': 'https://elevenlabs.io/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    voice_id = available_voices[voice]
    params = {'allow_unauthenticated': '1'}

    # Create the directory if it doesn't exist
    if not os.path.exists("STREAM_AUDIOS"):
        os.makedirs("STREAM_AUDIOS")

    sentences = text.split(".")
    audio_files = []  # List to store generated audio file paths
    stop_event = threading.Event()  # Event to signal if hotword detected

    def generate_audio_sequentially(text, part_number):
        success = False
        while not success and not stop_event.is_set():
            try:
                json_data = {'text': text,'model_id': 'eleven_multilingual_v2'}
                response = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',params=params, headers=headers, json=json_data, timeout=None)
                response.raise_for_status()
                # Check if the request was successful
                if response.ok and response.status_code == 200:
                    part_filename = f"{filename}_{part_number}.mp3"
                    # Save the response content as an audio file
                    with open(part_filename, "wb") as audio_file:
                        audio_file.write(response.content)
                        if verbose: print(f"Audio saved as {part_filename}.\n")
                        audio_files.append(part_filename)  # Add to list of audio files for playback
                        success = True
                else:
                    print("Error:",response.status_code, response.content)
                    time.sleep(1)
            except requests.RequestException as e:
                print(e)
                time.sleep(1)

    def play_audio_with_hotword_detection():
        play_audios(audio_files, prints=verbose)
        # Signal stop event if hotword detected during playback
        if any(os.path.exists(file) for file in audio_files):  # Check if files exist
            stop_event.set()  # Set event to stop generation if hotword detected

    # Start playback in a background thread once the first file is generated
    playback_started = False
    for chunk_num, sentence in enumerate(sentences, start=1):
        if sentence.strip():
            print(f"{chunk_num}* Chunk Text: {sentence.strip()}")
        if stop_event.is_set():  # Stop generation if hotword detected
            break
        generate_audio_sequentially(sentence.strip(), chunk_num)
        
        # Start playback thread once the first audio file is ready
        if audio_files and not playback_started:
            playback_thread = threading.Thread(target=play_audio_with_hotword_detection, daemon=True)
            playback_thread.start()
            playback_started = True

    # Clean up: Stop playback and delete all generated audio files if hotword detected
    if stop_event.is_set():
        for audio_file in audio_files:
            if os.path.exists(audio_file):
                os.remove(audio_file)
                if verbose: print(f"Audio file {audio_file} removed.")
    else:
        playback_thread.join()  # Wait for playback to complete if no hotword detected

if __name__ == "__main__":
    ElevenlabsTTS("Thermodynamics deals with heat, work, and temperature, and their relation to energy, entropy, and the physical properties of matter and radiation. The behavior of these quantities is governed by the four laws of thermodynamics, which convey a quantitative description using measurable macroscopic physical quantities, but may be explained in terms of microscopic constituents by statistical mechanics. Thermodynamics plays a role in a wide variety of topics in science and engineering. Historically, thermodynamics developed out of a desire to increase the efficiency of early steam engines, particularly through the work of French physicist Sadi Carnot.")