# AI Resume & Job Description Matcher

A Python-based web application that analyzes resumes against job descriptions to identify matching skills, missing skills, and resume-job alignment using keyword-based analysis.

## Live Demo

**Live Application:** [Open Resume Matcher](https://resume-job-matcher-qciy.onrender.com/)

## Features

- **PDF Resume Upload:** Upload a resume in PDF format for analysis.
- **Job Description Analysis:** Paste a job description to identify required skills.
- **PDF Text Extraction:** Extract text from resumes using PyMuPDF.
- **Skill Matching:** Identify technical skills present in both the resume and job description.
- **Missing Skill Detection:** Highlight relevant skills that may be missing from the resume.
- **Match Score:** Calculate a keyword-based match percentage.
- **Interactive Dashboard:** Present analysis results using charts and visual summaries.
- **Downloadable Report:** Download the analysis report for further review.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and text processing |
| Streamlit | Interactive web interface |
| PyMuPDF | PDF text extraction |
| Pandas | Data processing |
| Plotly | Data visualization |
| GitHub | Version control and source code hosting |
| Render | Application deployment |

## How It Works

1. Upload a PDF resume.
2. Paste the target job description.
3. Extract the resume text.
4. Identify relevant skills in the resume and job description.
5. Compare skills and calculate a keyword-based match score.
6. Display matching skills, missing skills, and visual analysis.
7. Download the report if required.

## Installation and Setup

### Prerequisites

- Python 3.11 or compatible version
- pip
- Git (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/Heenakousar26/resume-job-matcher.git
cd resume-job-matcher
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

`http://localhost:8501`

## Deployment

The application is deployed using Render.

Deployment configuration:

**Build command**
```bash
pip install -r requirements.txt
```

**Start command**
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Project Structure

```text
resume-job-matcher/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Future Enhancements

- Semantic similarity analysis between resumes and job descriptions.
- AI-generated resume improvement suggestions.
- Support for additional document formats.
- Customizable technical skill categories.
- More detailed reports with actionable recommendations.

## Limitations

The match score is based on keyword matching and should be treated as an indicative measure of alignment, not as a prediction of hiring success. Results depend on the extracted text and the skills recognized by the application.

## Author

**Heenakousar26**
**ShareefShaik1234**

## License

This project is intended for educational and portfolio purposes. Add an appropriate open-source license if you intend to distribute it under specific reuse terms.
