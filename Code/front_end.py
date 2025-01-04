import customtkinter as ctk
import threading
from TextPronunciationFluency import TextPronunciationFluency
import scipy.io.wavfile as wavfile
import sounddevice as sd
import numpy as np
import random
import string
from speechbrain.inference.interfaces import foreign_class

# initialize CustomTkinter settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# create the main app window
class LingoLab(ctk.CTk):
    def __init__(self):
        super().__init__()

        # main window, a table of a sigle cell (1x1)
        self.title("LingoLab")
        self.geometry("500x400")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.current_exercise = 0
        self.sample_rate = 16000

        # initialize the model for pronunciation feedback
        self.pronunciation_processor = TextPronunciationFluency()

        # load emotion recognition model
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

        # variable to dedice the focus of the second part
        self.incorrect_speak = 0
        self.incorrect_grammar = 0
        
        # exercises
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
            ("I ___ (go) to the party tomorrow.", "will go")
        ]
        self.speaking_exercises = [
            ("Test of a recording", "speaking"), 
            ("This is you captain speaking", "speaking"), 
            ("The cat is on the table", "speaking"),
            ("Go left", "speaking"), 
            ("Cross the roundabout", "speaking"), 
            ("Thank you very mutch", "speaking"),
            ("See you later", "speaking"), 
            ("That is enough thanks", "speaking"), 
            ("Today is Saturday", "speaking"),
            ("That is a nice coat", "speaking")
        ]

        # shuffle order inside each exercise
        random.shuffle(self.grammar_exercises)
        random.shuffle(self.speaking_exercises)

        # get N + N first exercise for the initial testing part
        self.general_exercises = self.grammar_exercises[:1] + self.speaking_exercises[:1]
        random.shuffle(self.general_exercises)

        # remove the N exercises from both lists, as we don't want to repropose the same exercise also on the specialization part
        self.grammar_exercises = self.grammar_exercises[5:]
        self.speaking_exercises = self.speaking_exercises[5:]

        # create a frame for the initial greeting and start button
        self.create_start_page()

    def create_start_page(self):
        # start page frame, a table of 1x3
        self.start_frame = ctk.CTkFrame(self, corner_radius=10)
        self.start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.start_frame.grid_columnconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(0, weight=1)
        self.start_frame.grid_rowconfigure(1, weight=1)
        self.start_frame.grid_rowconfigure(2, weight=1)

        # in the only cell put the first greeting message
        self.start_label1 = ctk.CTkLabel(self.start_frame, font=("Arial", 20, "bold"), text="Hi Arsenio!", justify="center")
        self.start_label1.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # in the only cell put the second greeting message
        self.start_label2 = ctk.CTkLabel(self.start_frame, text="Welcome to LingoLab!", justify="center")
        self.start_label2.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        
        # in the last cell the button that will call the function start_general_exercises()
        self.start_button = ctk.CTkButton(self.start_frame, text="Let's Start", command=self.start_general_exercises)
        self.start_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    def start_general_exercises(self):
        # remove the greeting page
        self.start_frame.destroy()

        # set as the exercises to be rendered the initial general ones
        self.current_exercise_list = self.general_exercises
        self.current_text = "General exercises"

        # render of the exercises
        self.create_exercise_page()

    def create_exercise_page(self):
        # creation of the exercise frame, a 1x3 table
        self.exercise_frame = ctk.CTkFrame(self, corner_radius=10)
        self.exercise_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.exercise_frame.grid_columnconfigure(0, weight=1)
        self.exercise_frame.grid_rowconfigure(0, weight=1)
        self.exercise_frame.grid_rowconfigure(1, weight=1)
        self.exercise_frame.grid_rowconfigure(2, weight=1)

        # create the header, a 1x3 table
        self.header_frame = ctk.CTkFrame(self.exercise_frame, corner_radius=10)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20), sticky="new")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # first put the text exmplaining the focus of the exercises
        self.header_label = ctk.CTkLabel(self.header_frame, text=self.current_text)
        self.header_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")

        # then the little colored squares that indicate the number of remaining exercises
        self.progress_squares = []
        self.progress_frame = ctk.CTkFrame(self.header_frame, corner_radius=0)
        self.progress_frame.grid(row=1, column=0, padx=0, pady=(0,15), sticky="n")
        for index in range(len(self.current_exercise_list)):
            self.progress_frame.grid_rowconfigure(index, weight=1)
            square = ctk.CTkLabel(self.progress_frame, width=20, height=5, text="", bg_color="gray")
            square.grid(row=0, column=index, padx=0, pady=0, sticky="nsew")
            self.progress_squares.append(square)

        # rendering of the exercise text, buttons
        self.populate()

    def populate(self):
        # update of the table of the done/remaining images
        self.progress_squares[self.current_exercise].configure(bg_color="blue")
        self.progress_squares[self.current_exercise].configure(text=str(self.current_exercise + 1))

        # exercise section, a table of 1x3
        self.fill_out_frame = ctk.CTkFrame(self.exercise_frame, corner_radius=10)
        self.fill_out_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.fill_out_frame.grid_columnconfigure(0, weight=1)
        self.fill_out_frame.grid_rowconfigure(0, weight=1)
        self.fill_out_frame.grid_rowconfigure(1, weight=1)

        # check if the exercise is speech or text, in order to understand if is needed to render which button, and if a text input or plain text
        correct_answer = self.current_exercise_list[self.current_exercise][1]
        if(correct_answer == "speaking"):
            # instructions
            self.exercise_label = ctk.CTkLabel(self.fill_out_frame, text=f"Read aloud: {self.current_exercise_list[self.current_exercise][0]}", font=("Arial", 16))
            self.exercise_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")

            # no text input
            self.answer_entry = ctk.CTkLabel(self.fill_out_frame, text="Your anwer will be put here")
        else:
            # instructions
            self.exercise_label = ctk.CTkLabel(self.fill_out_frame, text=f"Fill out: {self.current_exercise_list[self.current_exercise][0]}", font=("Arial", 16))
            self.exercise_label.grid(row=0, column=0, padx=20, pady=5, sticky="n")
            
            # there is a text input with the enter bounded to check the written text
            self.answer_entry = ctk.CTkEntry(self.fill_out_frame, placeholder_text="Write here the answer")
            self.answer_entry.bind("<Return>", self.submit_answer)

        # the instructions are on the 0th cell, the answer is in the 1st
        self.answer_entry.grid(row=1, column=0, padx=20, pady=(0,15), sticky="ew")

        # the buttons are set in the last frame
        if(correct_answer == "speaking"):
            # custom color and hover color, sending to function start_recording() in case of voice
            self.record_button = ctk.CTkButton(self.exercise_frame, text="Start recording", command=self.start_recording)
            self.orig_back_color = self.record_button.cget("fg_color")
            self.orig_hover_color = self.record_button.cget("hover_color")
            self.record_button.configure(fg_color="OrangeRed2", hover_color="red2")
            self.record_button.grid(row=2, column=0, padx=20, pady=20, sticky="s")
        else:
            # sending to function submit_answer() in case of text
            self.submit_button = ctk.CTkButton(self.exercise_frame, text="Submit", command=self.submit_answer)
            self.submit_button.grid(row=2, column=0, padx=20, pady=20, sticky="s")

    def record_audio(self):
        while self.recording:
            chunk = sd.rec(int(self.sample_rate * 0.5), samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()
            self.audio_data.append(chunk)

    def start_recording(self):
        self.recording = True
        self.record_button.configure(command=self.stop_recording)
        self.record_button.configure(text="Stop Recording")
        self.audio_data = []
        self.thread = threading.Thread(target=self.record_audio)
        self.thread.start()

    def stop_recording(self):
        self.recording = False
        if self.thread.is_alive():
            self.thread.join() 

        self.record_button.configure(command=self.submit_answer)
        wavfile.write("audio.wav", self.sample_rate, (np.concatenate(self.audio_data) * 32767).astype(np.int16))
        self.transcribe_audio("audio.wav")

    def transcribe_audio(self, file_path):
        
        # Emotion recognition part
        if self.emotion_recognizer:
            try:
                out_prob, score, index, text_lab = self.emotion_recognizer.classify_file(file_path)
                emotion_feedback = f"Emotion detected: {text_lab}"
                print(emotion_feedback)
            except Exception as e:
                emotion_feedback = f"Emotion analysis failed: {str(e)}"
                print(emotion_feedback)

        # results from the speech2text, speech2pronunciation, speech2fluency
        result = self.pronunciation_processor.transcribe_audio(file_path)
        words = self.pronunciation_processor.format_words(result)
        confidences = self.pronunciation_processor.format_confidence(result)
        fluencies = self.pronunciation_processor.format_fluency(result)

        # inserting the table head
        words.insert(0, "Speech:")
        confidences.insert(0, "Pronunciation:")
        fluencies.insert(0, "Fluency:")

        # normalizing the user output so that be found in a global variable, not only divided in the display table
        self.user_answer = result['text'].strip().lower()
        self.user_answer = self.user_answer.translate(str.maketrans('', '', string.punctuation))
        
        # define the display table, with three trown and dynamic columns
        # the text answer dummy text is destroyed
        self.answer_entry.destroy()
        self.answer_entry = ctk.CTkFrame(self.fill_out_frame, corner_radius=10)
        self.answer_entry.grid(row=1, column=0, padx=0, pady=0, sticky="ew")
        self.answer_entry.grid_rowconfigure(0, weight=1)
        self.answer_entry.grid_rowconfigure(1, weight=1)
        self.answer_entry.grid_rowconfigure(2, weight=1)
        for index, (word, confidence, fluency) in enumerate(zip(words, confidences, fluencies)):
            # put the word on the first row of the current column
            self.answer_entry.grid_columnconfigure(index, weight=1)
            ctk.CTkLabel(self.answer_entry, text=word).grid(row=0, column=index, padx=0, pady=0)
            
            # put the confidence converted text + color (or head) on the second row of the current column
            if type(confidence) == str:
                color = "white"
                text = confidence
            elif 0.7 <= confidence:
                color = "white"
                text = "good"
            elif confidence < 0.4:
                color = "red"
                text = "low"
            elif 0.4 <= confidence < 0.7:
                color = "yellow"
                text = "fine"
            else:
                raise("confidence coloring error")
            ctk.CTkLabel(self.answer_entry, text=text, text_color=color).grid(row=1, column=index, padx=0, pady=0)
            
            # put the fluency converted text + color (or head) on the second row of the current column
            if type(fluency) == str:
                color = "white"
                text = fluency
            elif fluency < 0.15:
                color = "white"
                text = "good"
            elif 0.15 <= fluency < 0.20:
                color = "royal blue"
                text = "fine"
            elif 0.20 <= fluency:
                color = "blue"
                text = "low"
            else:
                raise("fluency coloring error")
            ctk.CTkLabel(self.answer_entry, text=text, text_color=color).grid(row=2, column=index, padx=0, pady=0)
        
        # given the output is then set back to normal the recording button in order to stop seeing the resuilts and procede to the next exercise
        self.record_button.configure(text="Submit", fg_color=self.orig_back_color, hover_color=self.orig_hover_color)

    def submit_answer(self, event=None):
        # the feedback text is initiated in the center
        self.feedback_label = ctk.CTkLabel(self.exercise_frame, text="", font=("Arial", 20))
        self.feedback_label.grid(row=2, column=0, padx=20, pady=(0,15), sticky="s")

        # the ground truth is loaded
        correct_answer = self.current_exercise_list[self.current_exercise][1].strip().lower()
        
        # check if the exercise is about pronunciation, in order to determine from where to get the user prediction
        speaking = False
        if(correct_answer == "speaking"):
            speaking = True
            correct_answer = self.current_exercise_list[self.current_exercise][0].strip().lower()
        else:
            self.user_answer = self.answer_entry.get().strip().lower()
            self.user_answer = self.user_answer.translate(str.maketrans('', '', string.punctuation))

        if(self.user_answer == correct_answer):
            # if correct well done
            self.feedback_label.configure(text="Correct! Well done", text_color="white")
            self.progress_squares[self.current_exercise].configure(bg_color="green")
            self.progress_squares[self.current_exercise].configure(text="")
        else:
            # if incorrect check wich type of exercise is that
            self.feedback_label.configure(text="Oops! Wrong answer", text_color="yellow")
            self.progress_squares[self.current_exercise].configure(bg_color="red")
            self.progress_squares[self.current_exercise].configure(text="")
            if(speaking):
                self.incorrect_speak += 1
            else:
                self.incorrect_grammar += 1

        # remove the input fied + button to continue from the exercise page
        self.fill_out_frame.destroy()
        if(speaking):
            self.record_button.destroy()
        else:
            self.submit_button.destroy()
        # add in its place the feedback text, after two seconds get to the next exercise
        self.feedback_label.grid(row=1, column=0, padx=20, pady=(0,15), sticky="ew")
        self.feedback_label.after(2000, lambda : self.next_exercise())

    def next_exercise(self):
        # remove the feedback label
        self.feedback_label.destroy()
        # advance the index of the exercise
        self.current_exercise += 1
        if(self.current_exercise < len(self.current_exercise_list)):
            # we can load the next exercise
            self.populate()
        elif(self.current_exercise_list == self.general_exercises):
            # we are in the first part of the program (speech + text) and we need to change focus of exercises
            self.next_step()
        else:
            # we ended the second part also, time to show statistics
            self.end_exercises()

    def next_step(self):
        # reset of the exercise index
        self.current_exercise = 0
        if(self.incorrect_speak == self.incorrect_grammar):
            # if we did the exact number of errors for both types, then load them togeder also here
            self.current_exercise_list = self.grammar_exercises[:3] + self.speaking_exercises[:2]
            random.shuffle(self.current_exercise_list)
            self.current_text = "Mixed exercises"
        elif(self.incorrect_grammar > self.incorrect_speak):
            # if we did more errors in grammar load that 
            self.current_exercise_list = self.grammar_exercises
            self.current_text = "Grammar exercises"
        else:
            # if we did more errors in speaking load that
            self.current_exercise_list = self.speaking_exercises
            self.current_text = "Speaking exercises"
        
        # complete refresh of the exercise section
        self.exercise_frame.destroy()
        self.create_exercise_page()

    def end_exercises(self):
        # dummy exit page
        self.exercise_frame.destroy()
        ctk.CTkLabel(self, text="You completed all the exercises!").grid(row=0, column=0, padx=0, pady=0)

# Run the app
if __name__ == "__main__":
    app = LingoLab()
    app.mainloop()
