import sounddevice as sd
import numpy as np
import whisper_timestamped as whisper
import scipy.io.wavfile as wavfile

def print_colored_text(data):
    colors = {
        "red": "\033[31m",
        "yellow": "\033[33m",
        "white": "\033[37m"
    }

    # extracting words and their confidences
    words = data['segments'][0]['words']

    # printing words with colors based on confidence
    for word in words:
        confidence = word['confidence']
        text = word['text']

        if confidence < 0.4:
            color = colors["red"]
        elif 0.4 <= confidence < 0.7:
            color = colors["yellow"]
        else:
            color = colors["white"]

        # print words with its corresponding color, and original confidence for debug purposes
        print(f"{color}{text}\033[0m", end=" ")
        #print(f"{color}{confidence}\033[0m", end=" ")

    print()

def print_colored_fluency(data):
    colors = {
        "blue": "\033[34m",
        "cyan": "\033[36m",
        "white": "\033[37m"
    }

    # extract words with their durations
    words = data['segments'][0]['words']

    # calculating fluency for each word and print with colors
    for word in words:
        text = word['text']
        duration = word['end'] - word['start']
        word_length = len(text)
        if word_length == 0:
            # max fluency for empty words
            fluency = 1  
        else:
            # fluency score (lower is better)
            fluency = duration / word_length  
        
        if fluency < 0.2:
            color = colors["white"]
        elif 0.2 <= fluency < 0.35:
            color = colors["cyan"]
        else:
            color = colors["blue"]

        print(f"{color}{text}\033[0m", end=" ")
        #print(f"{color}{fluency}\033[0m", end=" ")

    print()

# ----------------------------------------------------------------------------

# duration in seconds of the recording
duration = 10  
# whisper expects 16 kHz audio
sample_rate = 16000  

print(f"Recording from {duration} seconds ...")
audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()
print("Recording finished.")

# save the recorded audio to a file, but in the final version it can be saved in buffer
wavfile.write("audio.wav", sample_rate, (audio_data * 32767).astype(np.int16))

audio = whisper.load_audio("audio.wav")

model = whisper.load_model("base", device="cpu")

result = whisper.transcribe_timestamped(model, audio, language="en", task="transcribe", vad="silero", detect_disfluencies=False, compute_word_confidence=True)

print_colored_text(result)

print_colored_fluency(result)