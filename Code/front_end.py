import customtkinter as ctk
import threading
from TextPronunciationFluency import TextPronunciationFluency
import scipy.io.wavfile as wavfile
import sounddevice as sd
import numpy as np

# initialize CustomTkinter settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# create the main app window
class LingoLab(ctk.CTk):
    def __init__(self):
        super().__init__()

        # main window
        self.title("LingoLab")
        self.geometry("500x400")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.processor = TextPronunciationFluency()
        self.recording = False
        self.current_exercise = 0
        self.sample_rate = 16000
        self.exercises = [
            {"text": "Traduci: 'Ciao'", "response": "Hello"},
            {"text": "Traduci: 'Addio'", "response": "Farewell"},
            {"text": "Traduci: 'Grazie'", "response": "Thank you"},
        ]

        self.create_start_page()

    def create_start_page(self):
        # start page frame
        self.start_frame = ctk.CTkFrame(self, corner_radius=10)
        self.start_frame.pack(pady=50, padx=50, fill="both", expand=True)
        self.start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.start_frame.grid_columnconfigure(0, weight=1)

        self.start_label1 = ctk.CTkLabel(
            self.start_frame, 
            font=("Arial", 20, "bold"),
            text="Bentornato Arsenio!", justify="center"
        )
        self.start_label1.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.start_label2 = ctk.CTkLabel(
            self.start_frame, 
            text="Continua ad esercitarti sulla lingua Inglese", justify="center"
        )
        self.start_label2.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        
        self.start_button = ctk.CTkButton(
            self.start_frame, 
            text="Procedi", 
            command=self.start_exercises
        )
        self.start_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    def start_exercises(self):
        self.start_frame.destroy()
        self.create_exercise_page()

    def create_exercise_page(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # header section
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Esercizi generali")
        self.header_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")

        self.progress_label = ctk.CTkProgressBar(self.header_frame, orientation="horizontal")
        self.progress_label.set((self.current_exercise + 1) / len(self.exercises))
        self.progress_label.grid(row=1, column=0, padx=20, pady=(0,15), sticky="s")

        # alert text
        self.feedback_label = ctk.CTkLabel(self, text="", font=("Arial", 20))
        self.feedback_label.grid(row=2, column=0, padx=20, pady=(0,15), sticky="s")

        self.populate()

    def populate(self):
        # exercise section
        self.exercise_frame = ctk.CTkFrame(self, corner_radius=10)
        self.exercise_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.exercise_frame.grid_columnconfigure(0, weight=1)

        self.exercise_label = ctk.CTkLabel(self.exercise_frame, text=self.exercises[self.current_exercise]["text"], font=("Arial", 16))
        self.exercise_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")

        self.answer_entry = ctk.CTkEntry(self.exercise_frame, placeholder_text="Scrivi qui la risposta")
        self.answer_entry.grid(row=1, column=0, padx=20, pady=(0,15), sticky="ew")
        self.answer_entry.bind("<Return>", self.submit_answer)

        # buttons
        self.buttons_frame = ctk.CTkFrame(self, corner_radius=10)
        self.buttons_frame.grid(row=3, column=0, padx=20, pady=20, sticky="sew")
        self.buttons_frame.grid_columnconfigure(0, weight=5)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        self.submit_button = ctk.CTkButton(self.buttons_frame, text="Procedi", command=self.submit_answer)
        self.submit_button.grid(row=0, column=0, padx=(20,0), pady=20, sticky="w")

        self.record_button = ctk.CTkButton(self.buttons_frame, text="Avvia microfono", command=self.toggle_recording, fg_color="OrangeRed2", hover_color="red2")
        self.record_button.grid(row=0, column=1, padx=(0,20), pady=20, sticky="s")

    def toggle_recording(self, event=None):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def record_audio(self):
        while self.recording:
            chunk = sd.rec(int(self.sample_rate * 0.5), samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()
            self.audio_data.append(chunk)

    def start_recording(self):
        self.recording = True
        self.answer_entry.delete(0, ctk.END)
        self.answer_entry.configure(state="disabled")
        self.submit_button.configure(state="disabled")
        self.record_button.configure(text="Stop Recording")
        self.audio_data = []
        self.thread = threading.Thread(target=self.record_audio)
        self.thread.start()

    def stop_recording(self):
        self.recording = False
        self.answer_entry.configure(state="normal")
        self.submit_button.configure(state="normal")
        self.record_button.configure(text="Start Recording")
        if self.thread.is_alive():
            self.thread.join() 

        wavfile.write("audio.wav", self.sample_rate, (np.concatenate(self.audio_data) * 32767).astype(np.int16))
        self.transcribe_audio("audio.wav")

    def transcribe_audio(self, file_path):
        result = self.processor.transcribe_audio(file_path)
        transcription = self.processor.format_transcription(result)
        fluency = self.processor.format_fluency(result)
        
        self.answer_entry.insert(0, result['text'])

    def submit_answer(self, event=None):
        user_answer = self.answer_entry.get().strip().lower()
        correct_answer = self.exercises[self.current_exercise]["response"].strip().lower()

        if(user_answer == correct_answer and self.current_exercise < len(self.exercises) - 1):
            self.feedback_label.configure(text="Risposta esatta!", text_color="white")
            self.exercise_frame.destroy()
            self.buttons_frame.destroy()
            self.feedback_label.grid(row=1, column=0, padx=20, pady=(0,15), sticky="ew")
            self.feedback_label.after(2000, lambda : self.next_exercise())
        elif(not user_answer == correct_answer):
            self.feedback_label.configure(text="Risposta errata!", text_color="yellow")
            self.feedback_label.after(2000, lambda : self.feedback_label.configure(text=""))
        else:
            self.end_exercises()

    def next_exercise(self):
        self.feedback_label.configure(text="")
        self.feedback_label.grid(row=2, column=0, padx=20, pady=(0,15), sticky="ew")
        self.current_exercise += 1
        self.progress_label.set((self.current_exercise + 1) / len(self.exercises))
        self.populate()

    def end_exercises(self):
        self.feedback_label.configure(text="Hai completato tutti gli esercizi!", text_color="white")
        self.exercise_frame.destroy()
        self.buttons_frame.destroy()
        self.feedback_label.grid(row=1, column=0, padx=20, pady=(0,15), sticky="ew")

# Run the app
if __name__ == "__main__":
    app = LingoLab()
    app.mainloop()
