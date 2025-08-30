from faster_whisper import WhisperModel
from typing import List

class GenerateCaptions:
    def __init__(self, model_size="medium", device="cpu"):
        self.model = WhisperModel(model_size, device=device)

    def get_word_timestamps_faster_whisper(self, audio_file_path) -> List[dict]:
        segments, info = self.model.transcribe(audio_file_path, language="en", word_timestamps=True)
        segments = list(segments)
        wordlevel_info = []

        for segment in segments:
            for word in segment.words:
                wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})

        return wordlevel_info

    def generate(self, audio_path):
        word_timestamps = self.get_word_timestamps_faster_whisper(audio_path)

        captions = [word_info['word'] for word_info in word_timestamps]
        captions = list(map(str.upper, captions))
        captions = list(map(str.strip, captions))

        start_times = [word_info['start'] for word_info in word_timestamps]
        durations = [word_info['end'] - word_info['start'] for word_info in word_timestamps]

        return {
            'captions': captions,
            'start_times': start_times,
            'durations': durations,
            'word_timestamps': word_timestamps
        }
    
if __name__ == "__main__":
    generator = GenerateCaptions(model_size="medium", device="cpu")
    result = generator.generate("/Users/anubhavchoubey/Documents/Codes/Own_Projects/Ultimate_Shorts_Editor/testing_stuff/audio_processed.wav")

    print(result)