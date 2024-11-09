# Interrupted_Playsound.py

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import threading
import time

try:from .Hotword_Detection import HotwordDetector
except ModuleNotFoundError: from Hotword_Detection import HotwordDetector
except:raise Exception("Failed to import Hotword_Detection module.")

def play_audio_Event(file_path: str, stop_event: threading.Event, prints: bool = True) -> None:
    """
    Plays an audio file. Stops playback if the stop_event is set.
    
    Args:
        file_path (str): The path to the audio file.
        stop_event (threading.Event): Event to signal stopping the playback.
        prints (bool): If True, enables print statements. Defaults to False.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    if prints: print(f"Playing audio: {file_path}")
    
    while pygame.mixer.music.get_busy() and not stop_event.is_set():
        time.sleep(0.1)  # Small sleep to prevent busy-waiting
    
    if stop_event.is_set():
        pygame.mixer.music.stop()
    
    pygame.mixer.quit()

def detect_hotword(detector: HotwordDetector, stop_event: threading.Event, prints: bool = True) -> None:
    """
    Detects hotwords using the HotwordDetector instance. Sets the stop_event if a hotword is detected.
    
    Args:
        detector (HotwordDetector): The hotword detector instance.
        stop_event (threading.Event): Event to signal that a hotword has been detected.
        prints (bool): If True, enables print statements. Defaults to False.
    """
    hotword_detected = detector.listen_for_hotwords()
    if hotword_detected:
        stop_event.set()
        if prints: print("Hotword detected, Setting Stop Event.")

def play_audio(audio_file: str, auto_remove:bool = False, prints: bool = True) -> None:
    """
    Plays multiple audio files sequentially and detects hotword concurrently.
    
    Args:
        audio_file_paths (list): List of paths to the audio files.
        prints (bool): If True, enables print statements. Defaults to False.
    """
    stop_event = threading.Event()
    detector = HotwordDetector()

    # Start hotword detection in a separate thread
    hotword_thread = threading.Thread(target=detect_hotword, args=(detector, stop_event, prints))
    hotword_thread.start()

    # Reset the stop event for each new file
    stop_event.clear()
    
    # Play the audio file in the main thread and wait for it to finish
    play_audio_Event(audio_file, stop_event, prints)
    if auto_remove:os.remove(audio_file);print(f"{audio_file} Auto removed sucessfully.")
    
    # If hotword was detected, stop the loop
    if stop_event.is_set():
        if prints:print(">> Exiting playback loop due to hotword detection.")
        
    detector.stop()
    hotword_thread.join()

def play_audios(audio_file_paths:list, auto_remove:bool = True, prints:bool = False) -> None:
    """
    Plays multiple audio files sequentially and detects hotword concurrently.
    
    Args:
        audio_file_paths (list): List of paths to the audio files.
        prints (bool): If True, enables print statements. Defaults to False.
    """
    stop_event = threading.Event()
    detector = HotwordDetector()

    # Start hotword detection in a separate thread
    hotword_thread = threading.Thread(target=detect_hotword, args=(detector, stop_event, prints))
    hotword_thread.start()

    for file_path in audio_file_paths:
        # Reset the stop event for each new file
        stop_event.clear()
        
        # Play the audio file in the main thread and wait for it to finish
        play_audio_Event(file_path, stop_event, prints)
        if auto_remove:os.remove(file_path);print(f"{file_path} Auto removed sucessfully.")

        # If hotword was detected, stop the loop
        if stop_event.is_set():
            if prints: print("Exiting playback loop due to hotword detection.")
            break

    detector.stop()
    hotword_thread.join()

# Example usage
if __name__ == "__main__":
    play_audio(audio_file="output_audio.mp3")
    # play_audios(audio_file_paths=["STREAM_AUDIOS\output_audio_1.mp3", "STREAM_AUDIOS\output_audio_2.mp3", "STREAM_AUDIOS\output_audio_3.mp3"])