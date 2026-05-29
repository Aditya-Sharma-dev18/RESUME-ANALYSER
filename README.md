# 📄 RESUME ANALYSER (AI Powered)

An AI-based Resume Analyzer that evaluates resumes against job descriptions and generates an ATS (Applicant Tracking System) score along with skill gap analysis, keyword matching, and improvement suggestions.

This project is built to help students and job seekers understand how well their resume performs in real hiring systems and how to optimize it for better selection chances.

---

## 🚀 Features

### 🎯 ATS Score Generator
- Calculates resume match score against job description
- Shows overall hiring compatibility percentage

### 🧠 AI Skill Extraction
- Extracts technical and soft skills from resume
- Identifies missing skills required for the job role

### 📊 Resume vs Job Matching
- Compares resume content with job description
- Highlights matched and missing keywords

### 🔍 Gap Analysis
- Shows weak areas in resume
- Suggests improvements based on role

### ✨ Smart Suggestions
- AI-based recommendations to improve resume
- ATS-friendly optimization tips

### 📄 File Support
- PDF resume upload support
- DOCX resume support
- Text extraction and cleaning

---

## ⚙️ Tech Stack

**Frontend:**
- HTML / CSS 
- Bootstrap 

**Backend:**
- Python / Flask 

**AI / NLP:**
-  NLP techniques
- Keyword extraction algorithms
- Text similarity matching

**Libraries:**
- pdfplumber / pdf-parse
- nltk / reportlab

---

## 🧠 How It Works

1. User uploads resume (PDF/DOCX)
2. System extracts raw text
3. Text is cleaned and processed
4. Job description is compared with resume
5. AI/NLP engine calculates:
   - Skill match
   - Keyword overlap
   - Experience relevance
6. Final ATS score + insights are generated

---

## 📊 Scoring Logic

ATS Score is calculated using:

- Keyword Matching → 40%
- Skill Match → 25%
- Experience Relevance → 20%
- Formatting & Structure → 15%

---

## 📁 Project Structure

```
RESUME-ANALYSER/
│
├── static/
├── templates/
├── app.py
├── utils.py
├── requirements.txt
├── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/Aditya-Sharma-dev18/RESUME-ANALYSER.git
cd RESUME-ANALYSER
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run project:
```bash
python app.py
```

---

## 📸 Screenshots
<img width="1886" height="912" alt="Screenshot 2026-05-29 195744" src="https://github.com/user-attachments/assets/f8df1521-191b-4d3b-be4c-891498da8fb3" />
<img width="1577" height="917" alt="Screenshot 2026-05-29 195857" src="https://github.com/user-attachments/assets/0e7521aa-4bba-44f4-a55c-472de4fa49b6" />
<img width="1842" height="900" alt="Screenshot 2026-05-29 195929" src="https://github.com/user-attachments/assets/87ae600d-a0e5-4d2e-81b8-a25213bad9ef" />
<img width="1835" height="887" alt="Screenshot 2026-05-29 195958" src="https://github.com/user-attachments/assets/79789763-0b14-4441-8075-b0c30667af48" />





---

## 🔥 Use Cases

- Students improving resume for placements
- Job seekers optimizing ATS score
- HR screening automation
- Career guidance tools

---

## 🚀 Future Improvements

- AI resume rewriting engine
- Multi-candidate ranking system
- Industry-specific scoring models
- Cloud deployment (SaaS version)

---

## 👨‍💻 Author

Aditya Sharma  
Engineering Student | AI & Software Development Enthusiast

---

## 📄 License

This project is open-source and available under the MIT License.
