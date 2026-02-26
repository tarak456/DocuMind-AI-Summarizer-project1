# 🧠 DocuMind AI – Smart Document Summarizer

DocuMind AI is a Streamlit-based AI web application that allows users to summarize text and PDF documents using powerful Transformer-based NLP models.

It provides a clean UI, multiple model options, summary size control, and downloadable outputs.

---

## 🚀 Features

- Upload PDF documents  
- Paste text directly  
- Multiple AI models (Fast / Balanced / Best Quality)  
- Short, Medium, and Long summaries  
- Paragraph or Bullet-point format  
- Download summary as text file  
- History of previous summaries  
- Dark-themed professional UI  

---

## 🛠️ Technologies Used

- Python  
- Streamlit  
- HuggingFace Transformers  
- PyTorch  
- PDFPlumber  
- SentencePiece  

---

## 📂 Project Structure
AI-Writer-Text-Summarizer/ │ ├── app.py ├── requirements.txt ├── README.md ├── screenshots/ │   ├── home.png │   ├── upload.png │   ├── summary.png │   └── history.png └── .gitignore
---

## ⚙️ Installation & Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py