import customtkinter as ctk
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from speechbrain.inference.interfaces import foreign_class
from TextPronunciationFluency import TextPronunciationFluency

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
        self.start_button = ctk.CTkButton(self.start_frame, text="Let's Start", command=self.show_exercise_choices)
        self.start_button.pack(pady=20)

    def show_exercise_choices(self):
        # Remove the welcome screen and show the exercise choice buttons
        self.start_frame.destroy()
        self.exercise_choice_frame = ctk.CTkFrame(self)
        self.exercise_choice_frame.pack(pady=20)

        # Welcome to the exercise choices screen
        self.exercise_choice_label = ctk.CTkLabel(self.exercise_choice_frame, text="Choose your exercise type:", font=("Arial", 20))
        self.exercise_choice_label.pack(pady=20)

        # Buttons for Grammar and Speaking
        self.grammar_button = ctk.CTkButton(self.exercise_choice_frame, text="Grammar", command=self.start_grammar_exercises)
        self.grammar_button.pack(pady=10)

        self.speaking_button = ctk.CTkButton(self.exercise_choice_frame, text="Speaking", command=self.start_speaking_exercises)
        self.speaking_button.pack(pady=10)

    def start_grammar_exercises(self):
        # Switch to grammar exercises screen
        self.exercise_choice_frame.destroy()  # Rimuovi la schermata delle scelte
        self.grammar_frame = ctk.CTkFrame(self)
        self.grammar_frame.pack(pady=20)

        # Esercizi di grammatica
        self.grammar_exercises = [
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
        self.current_grammar_exercise = 0
        self.correct_grammar_answers = 0

        # Label per mostrare la domanda
        self.grammar_label = ctk.CTkLabel(self.grammar_frame, text=self.grammar_exercises[self.current_grammar_exercise][0], font=("Arial", 16))
        self.grammar_label.pack(pady=20)

        # Campo di input per la risposta
        self.grammar_answer_entry = ctk.CTkEntry(self.grammar_frame, font=("Arial", 16))
        self.grammar_answer_entry.pack(pady=10)

        # Bottone per inviare la risposta
        self.submit_button = ctk.CTkButton(self.grammar_frame, text="Submit", command=self.submit_grammar_answer)
        self.submit_button.pack(pady=10)

        # Contatore di risposte corrette
        self.correct_answer_label = ctk.CTkLabel(self.grammar_frame, text=f"Correct answers: {self.correct_grammar_answers}", font=("Arial", 14))
        self.correct_answer_label.pack(pady=10)

    def submit_grammar_answer(self):
        # Controlla la risposta per l'esercizio corrente
        correct_answer = self.grammar_exercises[self.current_grammar_exercise][1]
        user_answer = self.grammar_answer_entry.get().strip().lower()

        if user_answer == correct_answer.lower():
            self.correct_grammar_answers += 1
            self.grammar_label.configure(text="Correct! Well done.")
        else:
            self.grammar_label.configure(text="Oops! Try again.")

        # Aggiorna il contatore
        self.correct_answer_label.configure(text=f"Correct answers: {self.correct_grammar_answers}")

        # Passa all'esercizio successivo
        self.current_grammar_exercise += 1
        if self.current_grammar_exercise < len(self.grammar_exercises):
            self.grammar_label.configure(text=self.grammar_exercises[self.current_grammar_exercise][0])
            self.grammar_answer_entry.delete(0, 'end')  # Pulisce l'input
        else:
            self.grammar_label.configure(text="All exercises completed!")
            self.submit_button.configure(state="disabled")

    def start_speaking_exercises(self):
        # Switch to speaking exercises screen
        self.exercise_choice_frame.destroy()
        self.speaking_frame = ctk.CTkFrame(self)
        self.speaking_frame.pack(pady=20)

        # List of speaking exercises (one word at a time)
        self.exercises = [
            "bit", "this", "see", "chip", "ship", 
            "left", "banana", "read (present)", "how", "coin"
        ]
        
        self.current_exercise = 0
        self.correct_speaking_answers = 0
        self.incorrect_speaking_answers = []

        self.exercise_label = ctk.CTkLabel(self.speaking_frame, text=self.exercises[self.current_exercise], font=("Arial", 24))
        self.exercise_label.pack(pady=20)

        # Record button to record pronunciation
        self.record_button = ctk.CTkButton(self.speaking_frame, text="Record Pronunciation", command=self.record_audio)
        self.record_button.pack(pady=10)

        # Next button to go to the next exercise
        self.next_button = ctk.CTkButton(self.speaking_frame, text="Next", command=self.next_exercise)
        self.next_button.pack(pady=10)

        # Feedback label
        self.feedback_label = ctk.CTkLabel(self.speaking_frame, text="", font=("Arial", 16))
        self.feedback_label.pack(pady=20)

        # Correct answer count display for speaking
        self.correct_speaking_label = ctk.CTkLabel(self.speaking_frame, text=f"Correct answers: {self.correct_speaking_answers}", font=("Arial", 14))
        self.correct_speaking_label.pack(pady=10)

    def record_audio(self):
        # Record audio for 3 seconds
        self.feedback_label.configure(text="Recording... Please speak now.")
        duration = 3  # seconds
        sample_rate = 16000
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()  # Wait until the recording is finished

        # Save the recorded audio
        audio_file = "pronunciation.wav"
        wavfile.write(audio_file, sample_rate, recording)

        # Transcribe the audio
        transcription_result = self.pronunciation_model.transcribe_audio(audio_file)

        # Extract the transcription text
        transcription = transcription_result.get("text", "").strip()
        transcription_cleaned = transcription.lower().strip().replace("?", "").replace(".", "").replace("!", "")

        # Compare the transcription with the expected word
        expected_word = self.exercises[self.current_exercise].lower().strip()
        if transcription_cleaned == expected_word:
            self.correct_speaking_answers += 1
            self.feedback_label.configure(text="Great! Your pronunciation is correct.")
        else:
            self.feedback_label.configure(text=f"Oops! You said: {transcription}. Try again.")
            self.incorrect_speaking_answers.append(self.exercises[self.current_exercise])

        # Update the correct answers label for speaking
        self.correct_speaking_label.configure(text=f"Correct answers: {self.correct_speaking_answers}")

        # Analyze emotion using the emotion recognition model
        if self.emotion_recognizer:
            try:
                out_prob, score, index, text_lab = self.emotion_recognizer.classify_file(audio_file)
                # Display only the emotion label
                emotion_feedback = f"Emotion detected: {text_lab}"
            except Exception as e:
                emotion_feedback = f"Emotion analysis failed: {str(e)}"
            self.feedback_label.configure(text=f"{self.feedback_label.cget('text')}\n{emotion_feedback}")

    def next_exercise(self):
        # Update the exercise word
        self.current_exercise += 1
        if self.current_exercise < len(self.exercises):
            self.exercise_label.configure(text=self.exercises[self.current_exercise])
            self.feedback_label.configure(text="")
        else:
            self.exercise_label.configure(text="No more exercises!")
            self.record_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.show_incorrect_speaking_answers()

    def show_incorrect_speaking_answers(self):
        # Display the incorrect answers at the end of the speaking exercises
        incorrect_answers_text = "Incorrect Answers:\n"
        for answer in self.incorrect_speaking_answers:
            incorrect_answers_text += f"- {answer}\n"
        
        self.exercise_label.configure(text=incorrect_answers_text)
        self.correct_speaking_label.configure(text="")

if __name__ == "__main__":
    app = LingoLab()
    app.mainloop()
