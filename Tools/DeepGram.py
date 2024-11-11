import requests
import base64
import re
import time
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
try:from Interrupted_Playsound import play_audio
except: from .Interrupted_Playsound import play_audio

def DeepgramTTS(text: str, voice_name: str = "Perseus", output_file: str = "Assets\output_file.mp3", verbose: bool = True):
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

    # Split text into sentences
    sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Function to request audio for each chunk
    def generate_audio_for_chunk(part_text: str, part_number: int):
        while True:
            try:
                payload = {"text": part_text, "model": available_voices[voice_name]}
                response = requests.post(url, headers=headers, json=payload, timeout=None)
                response.raise_for_status()
                response_data = response.json().get('data')
                if response_data:
                    audio_data = base64.b64decode(response_data)
                    if verbose:
                        print(f"Chunk {part_number} processed successfully.")
                    return part_number, audio_data
                else:
                    if verbose:
                        print(f"No data received for chunk {part_number}. Retrying...")
            except requests.RequestException as e:
                # print(f"Error for chunk {part_number}: {e}. Retrying...")
                time.sleep(1)

    # Using ThreadPoolExecutor to handle requests concurrently
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(generate_audio_for_chunk, sentence.strip(), chunk_num): chunk_num 
                   for chunk_num, sentence in enumerate(sentences, start=1)}
        
        # Dictionary to store results with order preserved
        audio_chunks = {}

        for future in as_completed(futures):
            chunk_num = futures[future]
            try:
                part_number, audio_data = future.result()
                audio_chunks[part_number] = audio_data  # Store the audio data in correct sequence
            except Exception as e:
                if verbose:
                    print(f"Failed to generate audio for chunk {chunk_num}: {e}")

    # Combine audio chunks in the correct sequence
    combined_audio = BytesIO()
    for part_number in sorted(audio_chunks.keys()):
        combined_audio.write(audio_chunks[part_number])
        # if verbose:
        #     print(f"Added chunk {part_number} to the combined file.")

    # Save the combined audio data to a single file
    with open(output_file, 'wb') as f:
        f.write(combined_audio.getvalue())
    print(f"\033[1;93mFinal audio saved as {output_file}.\033[0m\n")
    play_audio(output_file)
    
if __name__ == "__main__":
    start = time.time()
    DeepgramTTS("Hello, Sir! Welcome back. How can I assist you today?")
    end = time.time()
    print(f"Time Taken: {end-start:.2f} Seconds.")