# LingoLab: Enhancing Language Learning through AI and HCI

**LingoLab** is an innovative educational platform designed to bridge the gap between students' learning needs and teachers' instructional goals. Built with a focus on enhancing the language learning experience, LingoLab combines advanced Human-Computer Interaction (HCI) techniques with Artificial Intelligence (AI) to provide personalized learning journeys for students and actionable insights for educators.

---

### Core Features

#### Student-Centered Functionalities
- **Personalized Exercises**: Tailored activities to address individual learning gaps in grammar, vocabulary, and pronunciation.
- **Immediate Feedback**: Real-time assessment of text-based and vocal responses using advanced models like OpenAI's Whisper for speech-to-text and pronunciation analysis.
- **Engagement Analysis**: Non-verbal cues, including facial expressions and gaze tracking (using tools like MPII Gaze), detect discomfort or disengagement, dynamically adapting learning content.
- **Fatigue Detection**: Pauses exercises when gaze or emotional cues (sadness, anger) indicate fatigue, enhancing long-term engagement and comfort.

#### Teacher-Centered Functionalities
- **Performance Dashboards**: Visual statistics (graphs and charts) of student difficulties for specific exercises, aiding lesson planning.
- **Lesson Adaptability**: Insights into common struggles allow teachers to adjust classroom activities effectively.

---

### Technical Highlights

- **Software and Tools**:
  - **CustomTkinter**: For an intuitive and aesthetic user interface.
  - **Speech Recognition**: OpenAI's Whisper for real-time, multi-lingual transcription and pronunciation evaluation.
  - **Emotion Detection**: SpeechBrain, utilizing audio features like MFCCs and pitch to classify emotions (e.g., happiness, sadness, anger).
  - **Gaze Detection**: MPII Gaze for tracking focus and engagement.
  - **OpenCV**: For robust and efficient computer vision applications.
- **Hardware Compatibility**:
  - Optimized for devices like the Surface Laptop SE, ensuring performance on low-cost hardware with 4GB RAM and Intel UHD Graphics.

---

### Installation and Setup

#### Prerequisites
- Python 3.8 or higher
- Recommended OS: Windows 10/11 or macOS
- Hardware Requirements:
  - At least 4GB RAM
  - Camera and microphone for speech and gaze recognition

#### Installation Steps
1. Clone the LingoLab repository:
   ```bash
   git clone https://github.com/example/lingolab.git
   cd lingolab
   ```
2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # For macOS/Linux
   env\Scripts\activate     # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up additional tools:
   - **Whisper**:
     Follow [Whisper installation guide](https://github.com/openai/whisper).
   - **SpeechBrain**:
     Install with:
     ```bash
     pip install speechbrain
     ```
   - **MPII Gaze**:
     Ensure PyTorch is installed and configure MPII Gaze as described in its documentation.

---

### Pedagogical Impact
- **For Students**: Enhanced engagement, motivation, and retention through personalized and adaptive learning experiences.
- **For Teachers**: Efficient assessment tools, providing deeper insights into individual and class-wide performance.

---

LingoLab was conceptualized as part of the **Advanced Human-Computer Interaction 2024-2025** course and developed by **Ceron Andrea, Musso Chiara, and Coppola Emmanuele V.**. By addressing the needs of both students and teachers, this project aims to make language learning more accessible, efficient, and enjoyable.
