import customtkinter as ctk
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from speechbrain.inference.interfaces import foreign_class
from TextPronunciationFluency import TextPronunciationFluency
import random

class LingoLab(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize the model for pronunciation feedback
        self.pronunciation_model = TextPronunciationFluency()

        # Load emotion recognition model
        try:
            self.emotion_recognizer = foreign_class(
                source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
                pymodule_file="custom_interface.py",
                classname="CustomEncoderWav2vec2Classifier"
            )
            print("Emotion recognition model loaded successfully.")
        except Exception as e:
            print(f"Error loading emotion recognition model: {e}")
            self.emotion_recognizer = None

        # Main window setup
        self.title("LingoLab")
        self.geometry("500x400")

        # Create a frame for the initial greeting and start button
        self.start_frame = ctk.CTkFrame(self)
        self.start_frame.pack(pady=20)

        # Welcome message
        self.welcome_label = ctk.CTkLabel(self.start_frame, text="Hi Arsenio!\nWelcome to LingoLab!", font=("Arial", 20))
        self.welcome_label.pack(pady=20)

        # "Let's Start" button
        self.start_button = ctk.CTkButton(self.start_frame, text="Let's Start", command=self.start_random_exercises)
        self.start_button.pack(pady=20)

    def start_random_exercises(self):
        # Combine grammar and speaking exercises into one random set
        self.start_frame.destroy()

        grammar_exercises = [
            ("She ___ (be) a teacher.", "is"),
            ("They ___ (speak) English.", "do"),
            ("This is my book. It's ___ (I).", "mine"),
            ("This book is ___ (interesting) than that one.", "more interesting"),
            ("I don't have ___ money.", "any"),
            ("The cat is ___ the chair.", "on"),
            ("I ___ (read) a book right now.", "am reading"),
            ("She ___ (drive) a car.", "can't"),
            ("___ a window open in the room.", "There is"),
            ("I ___ (go) to the party tomorrow.", "will")
        ]

        speaking_exercises = [
            ("bit", "speaking"), ("this", "speaking"), ("see", "speaking"),
            ("chip", "speaking"), ("ship", "speaking"), ("left", "speaking"),
            ("banana", "speaking"), ("read (present)", "speaking"), ("how", "speaking"),
            ("coin", "speaking")
        ]

        self.all_exercises = grammar_exercises + speaking_exercises
        random.shuffle(self.all_exercises)

        self.current_exercise_index = 0
        self.correct_answers = 0
        self.incorrect_answers = []

        self.exercise_frame = ctk.CTkFrame(self)
        self.exercise_frame.pack(pady=20)

        self.exercise_label = ctk.CTkLabel(self.exercise_frame, text="", font=("Arial", 20))
        self.exercise_label.pack(pady=20)

        self.input_entry = ctk.CTkEntry(self.exercise_frame, font=("Arial", 16))
        self.input_entry.pack(pady=10)

        self.submit_button = ctk.CTkButton(self.exercise_frame, text="Submit", command=self.submit_answer)
        self.submit_button.pack(pady=10)

        self.feedback_label = ctk.CTkLabel(self.exercise_frame, text="", font=("Arial", 16))
        self.feedback_label.pack(pady=10)

        self.score_label = ctk.CTkLabel(self.exercise_frame, text="Correct: 0 | Incorrect: 0", font=("Arial", 14))
        self.score_label.pack(pady=10)

        self.update_exercise()

    def update_exercise(self):
        if self.current_exercise_index < len(self.all_exercises):
            current_exercise = self.all_exercises[self.current_exercise_index]
            if current_exercise[1] == "speaking":
                self.exercise_label.configure(text=f"Pronounce: {current_exercise[0]}")
            else:
                self.exercise_label.configure(text=current_exercise[0])
        else:
            self.show_results()

    def submit_answer(self):
        current_exercise = self.all_exercises[self.current_exercise_index]

        if current_exercise[1] == "speaking":
            self.record_audio(current_exercise[0])
        else:
            user_answer = self.input_entry.get().strip().lower()
            correct_answer = current_exercise[1].lower()

            if user_answer == correct_answer:
                self.correct_answers += 1
                self.feedback_label.configure(text="Correct! Well done.")
            else:
                self.feedback_label.configure(text="Oops! Try again.")
                self.incorrect_answers.append((current_exercise[0], user_answer))

        self.current_exercise_index += 1
        self.update_score()
        self.update_exercise()
        self.input_entry.delete(0, 'end')

    def record_audio(self, expected_word):
        self.feedback_label.configure(text="Recording... Please speak now.")
        duration = 3  # seconds
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        audio_file = "pronunciation.wav"
        wavfile.write(audio_file, sample_rate, recording)

        transcription_result = self.pronunciation_model.transcribe_audio(audio_file)
        transcription = transcription_result.get("text", "").strip().lower()

        if transcription == expected_word.lower():
            self.correct_answers += 1
            self.feedback_label.configure(text="Great! Your pronunciation is correct.")
        else:
            self.feedback_label.configure(text=f"Oops! You said: {transcription}. Try again.")
            self.incorrect_answers.append((expected_word, transcription))

        # Emotion recognition
        if self.emotion_recognizer:
            try:
                out_prob, score, index, text_lab = self.emotion_recognizer.classify_file(audio_file)
                emotion_feedback = f"Emotion detected: {text_lab}"
                self.feedback_label.configure(text=f"{self.feedback_label.cget('text')}\n{emotion_feedback}")
            except Exception as e:
                emotion_feedback = f"Emotion analysis failed: {str(e)}"
                self.feedback_label.configure(text=f"{self.feedback_label.cget('text')}\n{emotion_feedback}")

        self.current_exercise_index += 1
        self.update_score()
        self.update_exercise()

    def update_score(self):
        self.score_label.configure(text=f"Correct: {self.correct_answers} | Incorrect: {len(self.incorrect_answers)}")

    def show_results(self):
        self.exercise_frame.destroy()

        results_frame = ctk.CTkFrame(self)
        results_frame.pack(pady=20)

        results_label = ctk.CTkLabel(results_frame, text="Results", font=("Arial", 20))
        results_label.pack(pady=10)

        results_text = "Correct Exercises:\n"
        for exercise in self.all_exercises:
            if exercise not in [x[0] for x in self.incorrect_answers]:
                results_text += f"- {exercise[0]}\n"

        results_text += "\nIncorrect Exercises:\n"
        for incorrect in self.incorrect_answers:
            results_text += f"- {incorrect[0]} (Your answer: {incorrect[1]})\n"

        results_display = ctk.CTkLabel(results_frame, text=results_text, font=("Arial", 14), justify="left")
        results_display.pack(pady=10)

if __name__ == "__main__":
    app = LingoLab()
    app.mainloop()
