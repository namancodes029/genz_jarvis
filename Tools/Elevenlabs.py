# Main Website Url: https://elevenlabs.io/?from=shyamsundar5735

import requests
import re
import time
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
try:from Interrupted_Playsound import play_audio
except: from .Interrupted_Playsound import play_audio

def ElevenlabsTTS(text: str, voice: str = "Brian", output_file: str = "Assets\output_file.mp3", verbose: bool = True) -> str:
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

    # Split text into sentences
    sentences = re.split(r'(?<!\b\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # Function to request audio for each chunk
    def generate_audio_for_chunk(part_text: str, part_number: int):
        while True:
            try:
                json_data = {'text': part_text,'model_id': 'eleven_multilingual_v2'}
                response = requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',params=params, headers=headers, json=json_data, timeout=None)
                response.raise_for_status()
                # Check if the request was successful
                if response.ok and response.status_code == 200:
                    if verbose:print(f"Chunk {part_number} processed successfully.")
                    return part_number, response.content
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
    print(ElevenlabsTTS("Thermodynamics deals with heat, work, and temperature, and their relation to energy, entropy, and the physical properties of matter and radiation. The behavior of these quantities is governed by the four laws of thermodynamics, which convey a quantitative description using measurable macroscopic physical quantities, but may be explained in terms of microscopic constituents by statistical mechanics. Thermodynamics plays a role in a wide variety of topics in science and engineering. Historically, thermodynamics developed out of a desire to increase the efficiency of early steam engines, particularly through the work of French physicist Sadi Carnot."))