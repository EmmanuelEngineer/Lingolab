"""
Uso del Modello di Riconoscimento Emotivo di SpeechBrain

Questo script utilizza il modello preaddestrato 'speechbrain/emotion-recognition-wav2vec2-IEMOCAP'
per riconoscere le emozioni da file audio. Il modello si basa su Wav2Vec2 ed è ottimizzato per
la classificazione delle emozioni, fornendo informazioni utili come l'etichetta dell'emozione,
la confidenza e le probabilità per ciascuna classe.

Requisiti:
- Python 3.7 o superiore
- **Git** installato sul sistema, necessario per clonare i repository dal web.
- Librerie installate:
  - speechbrain (`pip install speechbrain`)
  - transformers (`pip install transformers`)

Come funziona:
1. Il modello e i file associati vengono scaricati automaticamente da HuggingFace Hub
   utilizzando Git. Assicurati che Git sia installato e configurato correttamente.
   Per verificare, esegui `git --version` nel terminale.
2. Il modello viene caricato tramite `foreign_class` di SpeechBrain, che utilizza il file
   `custom_interface.py` per definire il comportamento personalizzato del classificatore.
3. I file audio in formato `.wav` vengono classificati. Il modello restituisce:
   - L'etichetta dell'emozione predetta (es: 'anger', 'happiness').
   - La confidenza della predizione.
   - Le probabilità associate a ciascuna classe di emozione.

Come usare lo script:
1. Assicurati che Git sia installato e funzionante sul tuo computer.
2. Specifica il percorso dei file audio nella variabile `audio_file` o `audio_files`
   per classificare uno o più file.
3. Esegui lo script. Se il modello non è già stato scaricato, sarà automaticamente
   scaricato dalla HuggingFace Hub tramite Git.
4. I risultati saranno stampati nella console. Puoi anche salvare i risultati in un file CSV.

Nota:
- Assicurati che il file `custom_interface.py` sia presente nella directory specificata,
  oppure sarà scaricato automaticamente dalla HuggingFace Hub.

Esempio di utilizzo:
File: speechbrain/emotion-recognition-wav2vec2-IEMOCAP/anger.wav
Predicted Emotion: anger
Confidence Score: 0.92
Output Probabilities: [0.92, 0.05, 0.02, 0.01]
"""

import torch
from speechbrain.inference.interfaces import foreign_class

# Step 1: Load the custom model using SpeechBrain
try:
    classifier = foreign_class(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        pymodule_file="custom_interface.py",  # Ensure this file exists
        classname="CustomEncoderWav2vec2Classifier"
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading the model: {e}")
    exit()

# Step 2: Move the model to GPU if available
if torch.cuda.is_available():
    classifier.model.to("cuda")
    device = "cuda"
else:
    device = "cpu"
print(f"Running on device: {device}")

# Step 3: Classify a single audio file
def classify_audio(file_path):
    try:
        out_prob, score, index, text_lab = classifier.classify_file(file_path)
        print(f"File: {file_path}")
        print(f"Predicted Emotion: {text_lab}")
        print(f"Confidence Score: {score}")
        print(f"Output Probabilities: {out_prob}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Example: Single file classification
audio_file = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP/anger.wav"
classify_audio(audio_file)

# Step 4: Process multiple audio files (optional)
audio_files = [
    "speechbrain/emotion-recognition-wav2vec2-IEMOCAP/anger.wav",
    "speechbrain/emotion-recognition-wav2vec2-IEMOCAP/happiness.wav"
]

print("\nProcessing multiple files:")
for file in audio_files:
    classify_audio(file)

# Step 5: Save results to a CSV file (optional)
import csv

output_file = "emotion_predictions.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["File", "Predicted Emotion", "Confidence Score"])
    for file in audio_files:
        try:
            out_prob, score, index, text_lab = classifier.classify_file(file)
            writer.writerow([file, text_lab, score])
        except Exception as e:
            print(f"Error saving results for {file}: {e}")

print(f"Results saved to {output_file}.")
