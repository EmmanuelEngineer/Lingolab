import sounddevice as sd
import numpy as np
import whisper_timestamped as whisper
import scipy.io.wavfile as wavfile

class TextPronunciationFluency:
    def __init__(self, model_name="base", device="cpu"):
        print("Loading the model...")
        self.model = whisper.load_model(model_name, device=device)
        print("Model loaded successfully.")

    def transcribe_audio(self, audio_file_path, language="en", task="transcribe"):
        audio = whisper.load_audio(audio_file_path)
        result = whisper.transcribe_timestamped(
            self.model,
            audio,
            language=language,
            task=task,
            vad="auditok",
            detect_disfluencies=False,
            compute_word_confidence=True
        )
        return result

    def process_audio_recording(self, duration, sample_rate=16000, output_file="audio.wav"):
        print(f"Recording for {duration} seconds...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        print("Recording finished. Saving to file...")
        wavfile.write(output_file, sample_rate, (audio_data * 32767).astype(np.int16))
        return self.transcribe_audio(output_file)

    @staticmethod
    def format_transcription(result):
        output = ""
        words = result['segments'][0]['words']
        for word in words:
            confidence = word['confidence']
            text = word['text']
            output += f"{text} (Confidence: {confidence:.2f}) "
        return output

    @staticmethod
    def format_fluency(result):
        output = ""
        words = result['segments'][0]['words']
        for word in words:
            text = word['text']
            duration = word['end'] - word['start']
            word_length = len(text)
            fluency = 1 if word_length == 0 else duration / word_length
            output += f"{text} (Fluency: {fluency:.2f}) "
        return output
