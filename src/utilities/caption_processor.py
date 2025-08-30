from faster_whisper import WhisperModel
from google import genai
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class GenerateCaptions:
    def __init__(self, model_size="medium", device="cpu"):
        self.model = WhisperModel(model_size, device=device)
        self.google_model = genai.Client(api_key=getenv("GEMINI_API_KEY"))

    def generate(self, audio_path):
        segments, _ = self.model.transcribe(audio_path)
        captions = []
        for segment in segments:
            captions.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        return captions
    

if __name__ == "__main__":
    generator = GenerateCaptions(model_size="medium", device="cpu")
    captions = generator.generate("/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/audio_processed.wav")
    print(captions)

    for caption in captions:
        response = generator.google_model.models.generate_content(
            model="gemini-2.5-flash", contents=caption["text"]
        )
        print(response.text)
