# 🚀 Deep Learning Resume Screening & Skill Assessment

An AI-powered Resume Screening and Skill Assessment System built using **Flask**, **Python**, and **Sentence Transformers**. The application helps recruiters automatically analyze resumes, calculate ATS compatibility scores, match candidates with job descriptions, and generate AI-powered resume insights.

---

## 📌 Features

### 👨‍💼 Recruiter (Admin)

- Secure Admin Login
- Create and manage job postings
- View all job applications
- Resume ranking based on ATS score
- Detailed candidate analysis
- AI-generated resume summary
- Urgent hiring dashboard

### 👨‍🎓 Candidate

- User Registration & Login
- Upload Resume (PDF)
- Apply for Jobs
- View Application Status
- Compare Resume with Job Description
- AI Resume Analysis

### 🤖 AI Features

- ATS Resume Matching
- Semantic Resume Similarity using Sentence Transformers
- Resume Skill Extraction
- AI-powered Resume Summary
- Job Description Matching
- Resume Ranking

---

# 🛠️ Tech Stack

### Backend

- Python
- Flask
- Flask Login
- SQLAlchemy

### AI / Machine Learning

- Sentence Transformers
- Hugging Face Transformers
- Llama API (if configured)
- PyMuPDF

### Database

- SQLite

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript

---

# 📂 Project Structure

```
deep-learning-resume-screening/
│
├── app.py
├── config.py
├── models/
├── routes/
├── templates/
├── static/
├── utils/
├── README.md
├── requirements.txt
└── .gitignore
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/MansiJagtap96/deep-learning-resume-screening.git
```

Move into the project

```bash
cd deep-learning-resume-screening
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Open your browser

```
http://127.0.0.1:5000
```

---

# 📸 Screenshots

Add screenshots of your application inside a folder named **screenshots**

Example

```
screenshots/
    login.png
    dashboard.png
    resume-upload.png
    ats-score.png
    admin-dashboard.png
```

Then display them like this

```markdown
## Login Page

![Login](screenshots/login.png)

## Dashboard

![Dashboard](screenshots/dashboard.png)

## ATS Analysis

![ATS](screenshots/ats-score.png)
```

---

# 📊 Workflow

```
Resume Upload
       │
       ▼
Extract Resume Text
       │
       ▼
Generate Embeddings
       │
       ▼
Compare with Job Description
       │
       ▼
Calculate ATS Score
       │
       ▼
Generate AI Summary
       │
       ▼
Display Results
```

---

# 💡 Future Improvements

- PostgreSQL Support
- Docker Deployment
- AWS Deployment
- Email Notifications
- Resume OCR
- Multiple Resume Formats
- Admin Analytics Dashboard
- Interview Recommendation System

---

# 🧪 Technologies Used

- Python
- Flask
- SQLAlchemy
- HTML
- CSS
- Bootstrap
- JavaScript
- SQLite
- Sentence Transformers
- Hugging Face
- AI Resume Matching

---

# 👩‍💻 Author

**Mansi Jagtap**

GitHub:
https://github.com/MansiJagtap96

LinkedIn:
https://www.linkedin.com/in/mansi-jagtap-8a0a66226

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
