import requests
import json
import base64
import os
import time
import threading
import queue
import glob
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from Tools.Interrupted_Playsound import play_audios, play_audio

def OpenAITTS_v1(text: str, voice_name: str = "Shimmer", filename: str = "assets\streaming_audio\output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True):
    def split_text(text):
        parts = []

        def split(text):
            text = str(text).replace("*", "")
            while len(text) > max_length:
                split_index = text.rfind('.', 0, max_length)
                if split_index != -1:
                    parts.append(text[:split_index + 1].strip())
                    text = text[split_index + 1:].strip()
                else:
                    parts.append(text[:max_length].strip())
                    text = text[max_length:].strip()
            parts.append(text)

        split(text)

        i = 0
        while i < len(parts):
            if len(parts[i]) > max_length:
                split(parts.pop(i))
            else:
                i += 1
        return parts

    voices = {"Alloy": "alloy", "Echo": "echo", "Fable": "fable", "Onyx": "onyx", "Nova": "nova", "Shimmer": "shimmer"}

    voice_id = voices.get(voice_name)

    if voice_id is None:
        return ValueError(f"Voice name '{voice_name}' not found. Available voices are: {', '.join(voices.keys())}")

    url = "https://ttsmp3.com/makemp3_ai.php"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'dnt': '1',
        'origin': 'https://ttsmp3.com',
        'priority': 'u=1, i',
        'referer': 'https://ttsmp3.com/ai',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    parts = split_text(text)
    audio_queue = queue.Queue()

    def generate_audio_sequentially(part_text, part_number):
        payload = {'msg': part_text, 'lang': voice_id, 'speed': '1.00', 'source': 'ttsmp3'}
        success = False
        while not success:
            try:
                response = requests.post(url, data=payload, headers=headers, timeout=None)
                response.raise_for_status()
                if response.status_code == 200:
                    audio_url = json.loads(response.content).get('URL')
                    if audio_url:
                        audio_response = requests.get(audio_url, timeout=None)
                        part_filename = f"{filename}_{part_number}.mp3"
                        with open(part_filename, "wb") as file:
                            file.write(audio_response.content)
                        if verbose:print(f"Audio saved as {part_filename}.")
                        if auto_play:
                            audio_queue.put(part_filename)  # Enqueue for playback only if auto_play is True
                        success = True  # Set to True to exit the loop if successful
                    else:print(f"Error: {json.loads(response.content)['Error']}. Request error for part {part_number}, Received status code {response.status_code}, Retrying after 1 Second...");time.sleep(1)
                else:print(f"Error: Received status code {response.status_code}. Request error for part {part_number}, Retrying after 1 Second...");time.sleep(1)
            except requests.RequestException as e:
                print(f"Request error for part {part_number}: {e}. Retrying after 1 Second...");time.sleep(1)

    def play_audio():
        while True:
            audio_file = audio_queue.get()
            if audio_file is None:
                break
            play_audio(audio_file)
            os.remove(audio_file)  # Clean up the file after playing
            if verbose:print(f"Audio file {audio_file} removed.")
            audio_queue.task_done()

    # Start the audio playback in a background thread only if auto_play is True
    if auto_play:
        playback_thread = threading.Thread(target=play_audio, daemon=True)
        playback_thread.start()

    # Generate audio files sequentially in ascending order
    for i, part in enumerate(parts, start=1):
        generate_audio_sequentially(part, i)

    # If auto_play is True, wait for all audio files to be generated and played
    if auto_play:
        audio_queue.join()
        audio_queue.put(None)  # Signal playback thread to exit when done
        playback_thread.join()

def OpenAITTS_v2(text: str, voice_name: str = "Shimmer", filename: str = "assets\streaming_audio\output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True):
        # Get all file paths in the folder
    files = glob.glob(os.path.join(filename, "*"))

    for file_path in files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    def split_text(text):
        parts = []

        def split(text):
            text = str(text).replace("*", "")
            while len(text) > max_length:
                split_index = text.rfind('.', 0, max_length)
                if split_index != -1:
                    parts.append(text[:split_index + 1].strip())
                    text = text[split_index + 1:].strip()
                else:
                    parts.append(text[:max_length].strip())
                    text = text[max_length:].strip()
            parts.append(text)

        split(text)

        i = 0
        while i < len(parts):
            if len(parts[i]) > max_length:
                split(parts.pop(i))
            else:
                i += 1
        return parts

    voices = {"Alloy": "OA001", "Echo": "OA002", "Fable": "OA003", "Onyx": "OA004", "Nova": "OA005", "Shimmer": "OA006"}

    voice_id = voices.get(voice_name)

    if voice_id is None:
        return ValueError(f"Voice name '{voice_name}' not found. Available voices are: {', '.join(voices.keys())}")

    url = "https://api.ttsopenai.com/api/v1/public/text-to-speech-stream"
    headers = {
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://ttsopenai.com',
    'priority': 'u=1, i',
    'referer': 'https://ttsopenai.com/',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    parts = split_text(text)
    audio_queue = queue.Queue()

    def generate_audio_sequentially(part_text, part_number):
        payload = json.dumps({
            "model": "tts-1",
            "speed": 1,
            "input": part_text,
            "voice_id": voice_id
        })
        success = False
        while not success:
            try:
                response = requests.post(url, headers=headers, data=payload, timeout=None)
                response.raise_for_status()
                if response.status_code == 200:
                        part_filename = f"{filename}_{part_number}.mp3"
                        with open(part_filename, "wb") as file:
                            file.write(response.content)
                        if verbose:print(f"Audio saved as {part_filename}.")
                        if auto_play:
                            audio_queue.put(part_filename)  # Enqueue for playback only if auto_play is True
                        success = True  # Set to True to exit the loop if successful
                else:print(f"Error: Received status code {response.status_code}. Request error for part {part_number}, Retrying after 1 Second...");time.sleep(1)
            except requests.RequestException as e:
                print(f"Request error for part {part_number}: {e}. Retrying after 1 Second...");time.sleep(1)

    def play_audio():
        while True:
            audio_file = audio_queue.get()
            if audio_file is None:
                break
            play_audio(audio_file)
            os.remove(audio_file)  # Clean up the file after playing
            if verbose:print(f"Audio file {audio_file} removed.")
            audio_queue.task_done()

    # Start the audio playback in a background thread only if auto_play is True
    if auto_play:
        playback_thread = threading.Thread(target=play_audio, daemon=True)
        playback_thread.start()

    # Generate audio files sequentially in ascending order
    for i, part in enumerate(parts, start=1):
        generate_audio_sequentially(part, i)

    # If auto_play is True, wait for all audio files to be generated and played
    if auto_play:
        audio_queue.join()
        audio_queue.put(None)  # Signal playback thread to exit when done
        playback_thread.join()

def LazypyTTS(text: str, voice_name: str = "Joanna", filename: str = "assets\streaming_audio\output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True) -> str:
        # Get all file paths in the folder
    files = glob.glob(os.path.join(filename, "*"))

    for file_path in files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'dnt': '1',
    'origin': 'https://lazypy.ro',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    def _split_text(text) -> str:
        parts = []

        def split(text):
            text = str(text).replace("*", "")
            while len(text) > max_length:
                split_index = text.rfind('.', 0, max_length)
                if split_index != -1:
                    parts.append(text[:split_index + 1].strip())
                    text = text[split_index + 1:].strip()
                else:
                    parts.append(text[:max_length].strip())
                    text = text[max_length:].strip()
            parts.append(text)

        split(text)

        i = 0
        while i < len(parts):
            if len(parts[i]) > max_length:
                split(parts.pop(i))
            else:
                i += 1
        return parts

    parts = _split_text(text)
    audio_queue = queue.Queue()

    def generate_audio_sequentially(part_text, part_number):
        payload = {'service': 'StreamElements','voice': voice_name,'text': part_text}
        success = False
        while not success:
            try:
                response = requests.post(url="https://lazypy.ro/tts/request_tts.php", headers=headers, data=payload, timeout=None)
                response.raise_for_status()
                response_data = response.json()
                if response.status_code == 200:
                        part_filename = f"{filename}_{part_number}.mp3"
                        audio_url = response_data['audio_url']
                        if audio_url:
                            response = requests.get(url=audio_url, timeout=None)
                            with open(part_filename, "wb") as file:
                                file.write(response.content)
                            if verbose:print(f"Audio saved as {part_filename}.")
                            if auto_play:
                                audio_queue.put(part_filename)  # Enqueue for playback only if auto_play is True
                            success = True  # Set to True to exit the loop if successful
                else:print(f"Error: Received status code {response.status_code}. Request error for part {part_number}, Retrying after 1 Second...");time.sleep(1)
            except requests.RequestException as e:
                print(f"Request error for part {part_number}: {e}. Retrying after 1 Second...");time.sleep(1)

    def play_audio():
        while True:
            audio_file = audio_queue.get()
            if audio_file is None:
                break
            # pygame.mixer.init()
            # pygame.mixer.music.load(audio_file)
            # pygame.mixer.music.play()
            # # Keep the program running while the music plays
            # while pygame.mixer.music.get_busy():
            #     pygame.time.Clock().tick()
            
            # playsound(audio_file)
            play_audio(audio_file)

            os.remove(audio_file)  # Clean up the file after playing
            if verbose:print(f"Audio file {audio_file} removed.")
            audio_queue.task_done()

    # Start the audio playback in a background thread only if auto_play is True
    if auto_play:
        playback_thread = threading.Thread(target=play_audio, daemon=True)
        playback_thread.start()

    # Generate audio files sequentially in ascending order
    for i, part in enumerate(parts, start=1):
        generate_audio_sequentially(part, i)

    # If auto_play is True, wait for all audio files to be generated and played
    if auto_play:
        audio_queue.join()
        audio_queue.put(None)  # Signal playback thread to exit when done
        playback_thread.join()

def DeepgramTTS(text: str, voice_name: str = "Perseus", filename: str = "Assets/streaming_audio/output_audio", verbose: bool = True):
    available_voices = {
        "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
        "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
        "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
        "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en"
    }
    if voice_name not in available_voices:
        raise ValueError(f"Invalid voice name. Available voices are: {list(available_voices.keys())}")
    
    url = "https://deepgram.com/api/ttsAudioGeneration"
    headers = {
        "accept": "*/*", "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8", "content-type": "application/json",
        "origin": "https://deepgram.com", "priority": "u=1, i", "referer": "https://deepgram.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "dnt": "1"
    }

    # Create the directory if it doesn't exist
    if not os.path.exists("Assets/streaming_audio"):
        os.makedirs("Assets/streaming_audio")

    sentences = text.split(".")
    audio_files = []  # List to store generated audio file paths
    stop_event = threading.Event()  # Event to signal if hotword detected

    def generate_audio_sequentially(part_text, part_number):
        success = False
        while not success and not stop_event.is_set():
            try:
                payload = {"text": part_text, "model": available_voices[voice_name]}
                print(f"Chunk >>{part_text}")
                response = requests.post(url, headers=headers, json=payload, timeout=None)
                response.raise_for_status()
                if response.status_code == 200:
                    part_filename = f"{filename}_{part_number}.mp3"
                    with open(part_filename, 'wb') as audio_file:
                        audio_file.write(base64.b64decode(response.json()['data']))
                        if verbose: print(f"Audio saved as {part_filename}.")
                        audio_files.append(part_filename)  # Add to list of audio files for playback
                        success = True
                else:
                    print(f"Error: Received status code {response.status_code}. Retrying...")
                    time.sleep(1)
            except requests.RequestException as e:
                print(f"Request error: {e}. Retrying...")
                time.sleep(1)

    def play_audio_with_hotword_detection():
        play_audios(audio_files, prints=verbose)
        # Signal stop event if hotword detected during playback
        if any(os.path.exists(file) for file in audio_files):  # Check if files exist
            stop_event.set()  # Set event to stop generation if hotword detected

    # Start playback in a background thread once the first file is generated
    playback_started = False
    for i, part in enumerate(sentences, start=1):
        if stop_event.is_set():  # Stop generation if hotword detected
            break

        generate_audio_sequentially(part, i)

        # Start playback thread once the first audio file is ready
        if audio_files and not playback_started:
            playback_thread = threading.Thread(target=play_audio_with_hotword_detection, daemon=True)
            playback_thread.start()
            playback_started = True

    # Clean up: Stop playback and delete all generated audio files if hotword detected
    if stop_event.is_set():
        for audio_file in audio_files:
            print(audio_file)
            if os.path.exists(audio_file):
                os.remove(audio_file)
                if verbose: print(f"Audio file {audio_file} removed.")
    else:
        playback_thread.join()  # Wait for playback to complete if no hotword detected


# import requests
# import base64
# import os
# import re
# import time
# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from Interrupted_Playsound import play_audios

# def DeepgramTTS(text: str, voice_name: str = "Stella", filename: str = "STREAM_AUDIOS/output_audio", verbose: bool = True):
#     available_voices = {
#         "Asteria": "aura-asteria-en", "Arcas": "aura-arcas-en", "Luna": "aura-luna-en",
#         "Zeus": "aura-zeus-en", "Orpheus": "aura-orpheus-en", "Angus": "aura-angus-en",
#         "Athena": "aura-athena-en", "Helios": "aura-helios-en", "Hera": "aura-hera-en",
#         "Orion": "aura-orion-en", "Perseus": "aura-perseus-en", "Stella": "aura-stella-en"
#     }
#     if voice_name not in available_voices:
#         raise ValueError(f"Invalid voice name. Available voices are: {list(available_voices.keys())}")
    
#     url = "https://deepgram.com/api/ttsAudioGeneration"
#     headers = {
#         "accept": "*/*", "accept-encoding": "gzip, deflate, br, zstd",
#         "accept-language": "en-US,en;q=0.9,hi;q=0.8", "content-type": "application/json",
#         "origin": "https://deepgram.com", "priority": "u=1, i", "referer": "https://deepgram.com/",
#         "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
#         "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"',
#         "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
#         "dnt": "1"
#     }

#     # Create the directory if it doesn't exist
#     if not os.path.exists("STREAM_AUDIOS"):
#         os.makedirs("STREAM_AUDIOS")

#     sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
#     audio_files = []  # List to store generated audio file paths in sequence
#     stop_event = threading.Event()  # Event to signal if hotword detected

#     def generate_audio(part_text: str, part_number: int):
#         """Generate audio for each text part and save in sequence."""
#         part_filename = f"{filename}_{part_number}.mp3"
#         while not stop_event.is_set():
#             try:
#                 payload = {"text": part_text, "model": available_voices[voice_name]}
#                 response = requests.post(url, headers=headers, json=payload, timeout=None)
#                 response.raise_for_status()
#                 if response.status_code == 200:
#                     audio_data = base64.b64decode(response.json()['data'])
#                     return part_number, audio_data
#             except requests.RequestException:
#                 time.sleep(1)  # Retry after a short delay if there's a request error
#         return part_number, None  # Return None if stopped

#     def save_audio_file(part_number, audio_data):
#         """Save audio data to a file in the correct sequence."""
#         part_filename = f"{filename}_{part_number}.mp3"
#         with open(part_filename, 'wb') as audio_file:
#             audio_file.write(audio_data)
#         if verbose: print(f"Audio saved as {part_filename}.\n")
#         return part_filename

#     def play_audio_with_hotword_detection():
#         """Play audio files sequentially and detect hotword to stop playback if necessary."""
#         play_audios(audio_files, prints=verbose)
#         if any(os.path.exists(file) for file in audio_files):  # Check if files exist
#             stop_event.set()  # Set event to stop generation if hotword detected

#     # Start downloading audio files using ThreadPoolExecutor
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         futures = {executor.submit(generate_audio, sentence.strip(), i + 1): i for i, sentence in enumerate(sentences) if sentence.strip()}
        
#         # Ensure audio files are stored in order as they complete
#         audio_results = {}
#         for future in as_completed(futures):
#             part_number, audio_data = future.result()
#             if audio_data and not stop_event.is_set():
#                 audio_results[part_number] = audio_data
#                 # Save files sequentially once the required part is available
#                 while len(audio_files) + 1 in audio_results:
#                     current_number = len(audio_files) + 1
#                     saved_filename = save_audio_file(current_number, audio_results.pop(current_number))
#                     audio_files.append(saved_filename)
#             if stop_event.is_set():
#                 break  # Stop generating if hotword detected

#     # Start playback in a background thread if audio files have been generated
#     if audio_files:
#         playback_thread = threading.Thread(target=play_audio_with_hotword_detection, daemon=True)
#         playback_thread.start()
#         playback_thread.join()  # Wait for playback to complete

#     # Clean up: Stop playback and delete all generated audio files if hotword detected
#     if stop_event.is_set():
#         for audio_file in audio_files:
#             if os.path.exists(audio_file):
#                 os.remove(audio_file)
#                 if verbose: print(f"Audio file {audio_file} removed.")
