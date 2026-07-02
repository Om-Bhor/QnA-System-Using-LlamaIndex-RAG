# 🎓 AI Academic Assistant using RAG + Gemini + ChromaDB

An AI-powered Academic Assistant designed for colleges and universities that helps students learn from their own study materials instead of relying solely on general-purpose LLM knowledge.

The system combines **Retrieval-Augmented Generation (RAG)** with **Google Gemini** to provide accurate, context-aware answers from uploaded notes, assignments, and academic documents.

---

## 🚀 Features

### 📚 Document-Based Question Answering

* Upload PDF, DOCX, and TXT study materials.
* Semantic search using ChromaDB.
* Retrieves the most relevant content before generating an answer.
* Displays source references for transparency.

### 📝 Assignment Assistance

* Generates structured assignment solutions.
* Uses uploaded notes whenever relevant.
* Falls back to Gemini only when no relevant academic content is found.

### 📖 Topic Explanation

* Explains difficult concepts in simple language.
* Provides detailed academic explanations.
* Uses retrieved study material as the primary knowledge source.

### 📄 Automatic Summarization

* Generates concise exam-oriented summaries.
* Highlights important concepts.
* Easy revision notes.

### ❓ MCQ Generation

* Generates practice MCQs from uploaded notes.
* Useful for self-assessment and exam preparation.

### 🎯 Placement & Interview Preparation

* Placement preparation guidance.
* Interview preparation roadmaps.
* Domain-specific project ideas.
* Career guidance for technical roles.

### 🔍 Source-Aware Responses

* Displays document name and chunk number used to generate the response.
* Improves trust and explainability.

### 🚫 Academic-Only AI Assistant

The assistant is designed to answer only educational and career-related queries.

Supported:

* Exam preparation
* Assignment solving
* Concept explanation
* Summarization
* MCQ generation
* Placement preparation
* Interview guidance
* Project ideas

Not Supported:

* Politics
* News
* Entertainment
* Sports
* Stock Market
* General chit-chat

---

## 🏗️ Tech Stack

### Programming Language

* Python

### Generative AI

* Google Gemini 2.5 Flash
* Retrieval-Augmented Generation (RAG)

### Vector Database

* ChromaDB

### Document Processing

* PDFPlumber
* Python-docx
* python-pptx
* pypdfium2

### Frontend

* Streamlit

### Libraries

* NumPy
* Pillow
* python-dotenv

---

## ⚙️ Project Workflow

```text
Student Uploads Notes
        │
        ▼
Document Processing
        │
        ▼
Text Chunking
        │
        ▼
Gemini Embeddings
        │
        ▼
ChromaDB Storage
        │
        ▼
Student Query
        │
        ▼
Intent Detection
        │
        ▼
Semantic Retrieval
        │
        ▼
Prompt Construction
        │
        ▼
Gemini Response
        │
        ▼
Answer + Sources
```

---

## 📂 Project Structure

```
AI-Academic-Assistant/

│── app.py
│── backend.py
│── requirements.txt
│── .env
│── Data/
│── Chroma_db/
│── uploaded_files.json
│── README.md
```

---

## 💻 Installation

Clone the repository

```bash
git clone <repository-link>
```

Navigate to the project

```bash
cd AI-Academic-Assistant
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```
GOOGLE_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run app.py
```

---

## 🎯 Future Improvements

* Image-based Assignment Solving
* Question Paper Analysis
* Gemini Vision Integration
* PPT Image Extraction
* Handwritten Notes Understanding
* Previous Year Question Paper Analysis
* Automatic Flashcard Generation
* Study Planner
* Quiz Mode
* Multi-document Comparison
* AI Tutor Mode

---

## 📸 Screenshots

(Add screenshots here after deployment.)

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📜 License

This project is intended for educational and research purposes.
