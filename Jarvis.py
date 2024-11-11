import os
import time
import cv2
import threading
from dotenv import load_dotenv;load_dotenv()
from Tools.Colors import *
# from Tools.CerebrasChat import CerebrasAI
from Tools.Phind import chat
from playsound import playsound
# from Tools.Vision import GroqVision
from Tools.STT import SpeechToTextListener
from Tools.DeepGram import DeepgramTTS
from mtranslate import translate
from Tools.Alpaca_DS_Converser import ConversationHistoryManager
history_manager = ConversationHistoryManager()

class CameraVision:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.frame = None

        # Check if the camera opened successfully
        if not self.cap.isOpened():
            print("Error: Camera could not be opened.")
            self.running = False

    def start(self):
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()

    def update(self):
        while self.running:
            ret, self.frame = self.cap.read()
            if not ret:
                print("Error: Failed to read frame from camera.")
                break
            # Display the frame
            cv2.imshow('JARVIS Camera Feed', self.frame)
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

    def take_picture(self):
        if self.frame is not None:
            filename = os.path.join("assets", "captured_image.jpg")
            cv2.imwrite(filename, self.frame)
            return filename
        return None

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        # camera = CameraVision()
        # camera.start()
        listener = SpeechToTextListener(language="en-IN")  # Assuming this is defined elsewhere
        print("\033[92mJARVIS >> Hello, Sir! Welcome back. How can I assist you today?\033[0m")
        playsound("Assets\Welcome.mp3")
        while True:
            speech = listener.listen()  # Assuming this method blocks until speech is detected
            print("\033[93mNaman >> " + speech + "\033[0m")
            if not speech.strip():continue
            if "jarvis" in speech.lower():
                try:speech = translate(speech, "en", "auto")
                except:...
                print("\033[92mTranslated Speech >> " + speech + "\033[0m")
                if "take picture" in speech.lower():...
                    # speech = speech.replace("jarvis", "").strip()
                    # speech = speech.replace("take picture", "").strip()
                    # filename = camera.take_picture()
                    # if filename:
                    #     print(f"\033[93mPicture saved as {filename}\033[0m\n")
                    #     vision = GroqVision().generate(user_message=speech, image_path=filename)  # Assuming this is defined elsewhere
                    #     print(f"\033[92mJARVIS >> {vision}\033[0m\n")
                    #     DeepgramTTS(vision)
                else:
                    history_manager.store_history(history_manager.history + [{"role": "user", "content": speech}])
                    start = time.time()
                    response = chat(history_manager.history, stream=False)
                    end = time.time()
                    print(f"\033[1;93m\nTime Taken: {end - start:.2f} Seconds")
                    history_manager.update_file(speech, response)
                    print("\033[92mJARVIS >> {}\033[0m".format(response))
                    DeepgramTTS(response)
    except Exception as e:print(f"Jarvis RunTime Error: {bold_bright_red}{e}{reset}")
    finally:...
        # camera.stop()