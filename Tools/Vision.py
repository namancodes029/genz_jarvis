import os
import base64
from groq import Groq
from dotenv import load_dotenv;load_dotenv()

class GroqVision:
    def __init__(self, model: str="llama-3.2-11b-vision-preview"):
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encodes the image file to a Base64 string.

        Parameters:
        image_path (str): The path to the image file.

        Returns:
        str: The Base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def generate(self, user_message: str, image_path:str) -> str:
        image_base64 = self.encode_image_to_base64(image_path)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user","content": [{"type": "text","text": f"Act as if this image has been captured in real time. Describe exactly what you see in the image as if you are observing it live. Answer the user's question based on the details visible in the image, using clear and direct observations. User Question: {user_message}"},{ "type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}]},{"role": "assistant","content": ""}],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        return completion.choices[0].message.content