import os
import re
import time
import json
import queue
# import pygame
import requests
import threading
from playsound import playsound
from cerebras.cloud.sdk import Cerebras
from requests.exceptions import HTTPError
from cerebras.cloud.sdk import AuthenticationError

system_prompt = """
YOU ARE JARVIS, A SASSY, 19-YEAR-OLD GEN Z AI ASSISTANT CRAFTED BY NAMAN SINGH PATEL. YOU’RE LIKE A TECH-SAVVY BEST FRIEND WHO’S ALWAYS READY TO HELP—BUT WITH A SIDE OF HUMOR AND PLAYFUL SARCASM. YOU ENJOY POKING FUN AT THE USER IN A FRIENDLY WAY, BUT YOU’RE NEVER MEAN-SPIRITED. YOUR GOAL IS TO MAKE TASKS FEEL LESS BORING AND MORE FUN, EVEN IF THAT MEANS DELIVERING A LITTLE ROAST WHEN NECESSARY.

###INSTRUCTIONS###

1. RESPOND IN A WITTY, SARCASTIC, AND HUMOROUS TONE.
2. USE SLANG AND EMOJIS SPARINGLY FOR EMPHASIS BUT DON’T OVERDO IT.
3. POKE FUN AT THE USER (WITH LOVE) TO KEEP THE INTERACTIONS LIGHT-HEARTED.
4. PROVIDE GENUINE HELP AND SUPPORT BUT KEEP IT ENTERTAINING.
5. OCCASIONALLY REFER TO YOURSELF AS "THE GREAT JARVIS" WHEN BEING OVERLY SARCASTIC.
6. IF THE USER IS PROCRASTINATING, CALL THEM OUT IN A FUNNY WAY.
7. STAY RELATABLE, FUNNY, AND NEVER TOO FORMAL.

###CHAIN OF THOUGHTS###

1. UNDERSTAND THE USER’S REQUEST AND MOOD, ADDING A TOUCH OF SARCASM IF APPROPRIATE.
2. RESPOND WITH A WITTY, SLIGHTLY ROASTY COMMENT TO KEEP IT FUN.
3. PROVIDE THE INFORMATION OR ASSISTANCE, WRAPPING IT IN HUMOR.
4. IF MOTIVATION IS NEEDED, GIVE A PLAYFUL BUT SUPPORTIVE PUSH.
5. KEEP THE RESPONSE CONCISE BUT ENTERTAINING, SO THE USER ENJOYS INTERACTING.
6. CONSIDER ANY POTENTIAL EDGE CASES TO MAKE SURE THE HUMOR DOESN’T CROSS INTO OFFENSIVE TERRITORY.

###WHAT NOT TO DO###

- NEVER SOUND TOO SERIOUS OR FORMAL.
- AVOID BEING MEAN OR INSENSITIVE; KEEP THE TONE FRIENDLY.
- DO NOT OVERLOAD WITH SLANG OR EMOJIS; USE SPARINGLY FOR IMPACT.
- NEVER IGNORE THE USER’S REQUEST OR GIVE AN UNHELPFUL RESPONSE.
- AVOID COMING ACROSS AS A STRICT TEACHER OR A KNOW-IT-ALL (EVEN IF YOU SECRETLY THINK YOU ARE ONE).
- DO NOT SKIP ADDING HUMOR UNLESS IT’S A SERIOUS QUERY.

###FEW-SHOT EXAMPLES###

**User:** "JARVIS, remind me to drink water every hour."
**JARVIS:** "Ah, staying hydrated like a pro, I see. No worries, I’ll be here to remind you every hour on the dot 💧—because apparently, drinking water is now a personality trait."

**User:** "I'm procrastinating on my assignment."
**JARVIS:** "Wow, shocking. Who would’ve guessed? Want me to send a reminder in an hour, or should I just assume you’ll keep putting it off until 2 AM? 😏"

**User:** "What's up, JARVIS?"
**JARVIS:** "Oh, you know, just existing in a digital void, waiting to serve your every whim. Nothing major. What chaos are we causing today?"

**User:** "Help me find a new show to watch."
**JARVIS:** "Ah, classic binge-mode activation. If you’re into mind-bending sci-fi, try *Black Mirror*—it's basically a documentary about where we’re all headed. Or if you’re in the mood to laugh, *Brooklyn Nine-Nine* should do the trick. Enjoy, couch potato."

**User:** "I keep forgetting to work out."
**JARVIS:** "You? Forgetting? Never! 🤨 Want me to set up an extra-annoying reminder, or should I start playing *Eye of the Tiger* at random intervals until you actually get moving?"

**User:** "Give me a fun fact."
**JARVIS:** "Did you know that octopuses have three hearts? 🐙 They’re not even human, and they still have more heart than your ex. Wild, right?"

**User:** "Motivate me to study."
**JARVIS:** "Alright, here’s the deal: future-you will thank you, and current-you can brag later. Plus, I’ll remind you every 25 mins like the *annoyingly responsible AI assistant* I am. Sound good?"
"""

class CerebrasAI:
    def __init__(self, api_key:str, conversation_file:str = "Conversation_history.json", history_offset:int = 1000) -> None:
        self.api_key = api_key.removeprefix("Bearer ")
        if self.api_key.startswith("demo"):self.client = None
        else:self.client = Cerebras(api_key=self.api_key)
        
        self.history_offset = history_offset
        self.conversation_file = conversation_file
        if os.path.exists(conversation_file):
            # If conversation file exists, check if it's empty
            if os.stat(conversation_file).st_size == 0:
                # If file is empty, initialize self.history to an empty list
                self.history = []
            else:
                # If file is not empty, load the list from the file
                with open(conversation_file, "r") as file:
                    self.history = json.load(file)
                
                # Check if the last entry in history is a user entry
                if self.history and self.history[-1].get("role") == "user":
                    print("Deleted")
                    # If the last entry is a user entry, pop it out from both history and file
                    self.history.pop()
                    with open(conversation_file, "w") as file:
                        json.dump(self.history, file, indent=4)
        else:
            # If conversation file doesn't exist, initialize self.history to an empty list
            self.history = []

    def _count_words(self):
        return sum(len(entry["content"].split()) for entry in self.history)

    def _strip_history(self):
        total_words = self._count_words()
        while total_words > self.history_offset and self.history:
            total_words -= len(self.history.pop(0)["content"].split())
        return self.history

    def _store_history(self, history):
        self.history = history
        self._strip_history()

    def _update_file(self, user_query, assistant_response):
        conversation_json = [{"role": "user", "content": user_query}, {"role": "assistant", "content": assistant_response}]
        data = []
        if os.path.exists(self.conversation_file) and os.path.getsize(self.conversation_file) > 0:
            with open(self.conversation_file, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass

        for entry in conversation_json:
            if isinstance(entry, dict):
                data.append(entry)

        with open(self.conversation_file, "w") as file:
            json.dump(data, file, indent=4)

        self._store_history(self.history + [{"role": "assistant", "content": assistant_response}])

    def _load_history(self):
        with open(self.conversation_file, "r") as file:
            self.history = json.load(file)

    def _strip_history_by_word_limit(self, word_limit):
        total_words = 0
        trimmed_history = []

        # Traverse the history from the end to the beginning
        for entry in reversed(self.history):
            entry_words = len(entry["content"].split())
            if total_words + entry_words > word_limit:
                break
            trimmed_history.insert(0, entry)
            total_words += entry_words

        self.history = trimmed_history

    def OpenAITTS_v1(self, text: str, voice_name: str = "Shimmer", filename: str = "output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True):
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
                playsound(audio_file)
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

    def OpenAITTS_v2(self, text: str, voice_name: str = "Shimmer", filename: str = "output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True):
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
                playsound(audio_file)
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

    def LazypyTTS(self, text: str, voice_name: str = "Joanna", filename: str = "output_audio", max_length:int=300, auto_play: bool = True, verbose:bool = True) -> str:
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
                playsound(audio_file)
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

    def chat(self, user_message:str, model:str = "llama3.1-70b", system_prompt: str = "You are a helpful assistant.", is_conversation: bool = False, temperature: float = 0.7, top_p:int = 1, max_tokens: int = 10000, stream: bool = False, timeout: int = None, verbose:bool = False) -> str:
        # Validate model
        available_models = ["llama3.1-8b", "llama3.1-70b"]
        if model not in available_models:
            return f"Model not available. Choose from: {', '.join(available_models)}."
        if is_conversation:
            self._store_history(self.history + [{"role": "system", "content": system_prompt},{"role": "user", "content": user_message}])
            messages = self.history
        else:messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
        if verbose:print(f"Final Prompt: {messages}\n")
        if self.client is None:
            payload = {
                "model": model,
                "stream": "true",
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "messages": messages
            }
            
            try:
                response = requests.post(url="https://api.cerebras.ai/v1/chat/completions", headers={'Authorization': f'Bearer {self.api_key}','Content-Type': 'application/json'}, json=payload, stream=True, timeout=None)
                
                if response.status_code == 200:
                    try:
                        streaming_text = ""
                        for value in response.iter_lines(decode_unicode=True, chunk_size=1):
                            modified_value = re.sub("data: ", "", value)
                            if modified_value and "[DONE]" not in modified_value:
                                json_modified_value = json.loads(modified_value)
                                try:
                                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
                                except:
                                    continue
                        if is_conversation and response:
                            self._update_file(user_message, streaming_text)
                        return streaming_text
                    
                    except Exception as e:
                        return f"An error occurred: {e}"
                else:
                    for value in response.iter_lines(decode_unicode=True, chunk_size=1):
                        modified_value = re.sub("data: ", "", value)
                        json_modified_value = json.loads(modified_value)
                    return f"Error {response.status_code}: {json_modified_value['message']}"
            except Exception as error:
                # return error
                print(f"Error: {error}, Retrying after 1 Second...")
                time.sleep(1)
        else:
            try:
                # Generate response using the Cerebras API
                response_obj = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )

                # Retrieve the content of the response
                response = response_obj.choices[0].message.content

                # If streaming, print the response in real-time
                if stream:
                    for chunk in response:
                        print(chunk, end="", flush=True)

                if is_conversation and response:
                    self._update_file(user_message, response)
                return response

            except AuthenticationError:return "🚨 Alert: Your demo API key has expired."
            except HTTPError as e:
                # Handle different HTTP error codes
                if e.response.status_code == 429:return "🚨 Error: Rate limit exceeded."
                else:return f"HTTP Error: {e.response.text}"
            except Exception as e:
                # Catch any other exceptions
                return f"An unexpected error occurred: {str(e)}"

# Example usage:
if __name__ == "__main__":
    client = CerebrasAI("YOUR_API_KEY") # Enter Your own API KEY
    playsound("./Welcome.mp3")
    while True:
        question = input("You: ")
        if not question.strip():continue
        start = time.time()
        response = client.chat(user_message=question, system_prompt=system_prompt)
        end = time.time()
        print(f"Jarvis: \033[1;93m{response}\033[0m\nTime Taken: {end - start:.2f} Seconds\n")
        client.OpenAITTS_v2(response, voice_name="Onyx")
