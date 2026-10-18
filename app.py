# app.py
# AI Resume and Job Description Matcher
# Tools: Python + Streamlit only (no backend API, no paid AI API)

import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader

# ----------------------------------------------------------------------
# 1. PAGE SETTINGS
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume & JD Matcher",
    page_icon="📄",
    layout="wide",
)

# ----------------------------------------------------------------------
# 2. SKILLS DATABASE
# Format:  "Category": { "skill name": [list of ways it may be written] }
# To add a new skill, add one line in the right category.
# ----------------------------------------------------------------------
SKILLS = {
    "Programming Languages": {
        "python": ["python"],
        "java": ["java"],
        "javascript": ["javascript", "es6"],
        "typescript": ["typescript"],
        "c++": ["c++"],
        "c#": ["c#"],
        "php": ["php"],
        "kotlin": ["kotlin"],
        "sql": ["sql"],
    },
    "Frontend": {
        "html": ["html", "html5"],
        "css": ["css", "css3"],
        "react": ["react", "react.js", "reactjs"],
        "angular": ["angular", "angularjs"],
        "vue": ["vue", "vue.js", "vuejs"],
        "next.js": ["next.js", "nextjs"],
        "redux": ["redux"],
        "bootstrap": ["bootstrap"],
        "tailwind css": ["tailwind", "tailwind css", "tailwindcss"],
        "responsive design": ["responsive design", "responsive web design"],
    },
    "Backend": {
        "spring boot": ["spring boot", "springboot", "spring framework", "spring mvc", "spring"],
        "hibernate": ["hibernate", "spring data jpa", "jpa"],
        "node.js": ["node.js", "nodejs", "node js"],
        "express.js": ["express.js", "expressjs"],
        "django": ["django"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        "rest api": ["rest api", "rest apis", "restful", "restful api", "restful apis"],
        "graphql": ["graphql"],
        "microservices": ["microservices", "microservice"],
    },
    "Databases": {
        "mysql": ["mysql"],
        "postgresql": ["postgresql", "postgres"],
        "mongodb": ["mongodb", "mongo db"],
        "sqlite": ["sqlite"],
        "oracle": ["oracle"],
        "redis": ["redis"],
        "nosql": ["nosql"],
    },
    "Cloud & DevOps": {
        "aws": ["aws", "amazon web services"],
        "azure": ["azure"],
        "gcp": ["gcp", "google cloud"],
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "git": ["git"],
        "github": ["github"],
        "jenkins": ["jenkins"],
        "ci/cd": ["ci/cd", "cicd", "ci cd"],
        "linux": ["linux"],
        "terraform": ["terraform"],
    },
    "Data & AI": {
        "pandas": ["pandas"],
        "numpy": ["numpy"],
        "scikit-learn": ["scikit-learn", "sklearn"],
        "tensorflow": ["tensorflow"],
        "pytorch": ["pytorch"],
        "machine learning": ["machine learning"],
        "deep learning": ["deep learning"],
        "nlp": ["nlp", "natural language processing"],
        "data analysis": ["data analysis", "data analytics"],
        "power bi": ["power bi", "powerbi"],
        "tableau": ["tableau"],
        "excel": ["excel"],
    },
    "Engineering Concepts & Tools": {
        "data structures": ["data structures", "dsa"],
        "algorithms": ["algorithms", "algorithm"],
        "oop": ["oop", "oops", "object oriented", "object-oriented"],
        "system design": ["system design"],
        "agile": ["agile"],
        "scrum": ["scrum"],
        "jira": ["jira"],
        "postman": ["postman"],
        "unit testing": ["unit testing", "junit", "pytest"],
        "selenium": ["selenium"],
        "debugging": ["debugging", "debug"],
        "troubleshooting": ["troubleshooting", "troubleshoot"],
        "networking": ["networking", "tcp/ip"],
    },
}


# ----------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ----------------------------------------------------------------------
def extract_pdf_text(uploaded_file):
    """Read every page of the PDF and return all the text as one string."""
    reader = PdfReader(uploaded_file)
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    return "\n".join(pages_text)


def clean_text(text):
    """Lowercase the text and replace line breaks/extra spaces with one space."""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def find_skills(text):
    """
    Look for every skill from the SKILLS database inside the text.
    Returns a dictionary:  {skill_name: category}
    The pattern makes sure 'java' does NOT match inside 'javascript',
    and 'sql' does NOT match inside 'mysql'.
    """
    text = clean_text(text)
    found = {}
    for category, skills in SKILLS.items():
        for skill_name, aliases in skills.items():
            for alias in aliases:
                pattern = r"(?<![a-z0-9+#])" + re.escape(alias) + r"(?![a-z0-9+#])"
                if re.search(pattern, text):
                    found[skill_name] = category
                    break  # one alias is enough, go to next skill
    return found


def calculate_match(resume_skills, jd_skills):
    """
    Transparent score:
        match % = (skills required by the job that are in the resume)
                  / (all skills required by the job) x 100
    """
    matched = sorted(set(jd_skills) & set(resume_skills))
    missing = sorted(set(jd_skills) - set(resume_skills))
    extra = sorted(set(resume_skills) - set(jd_skills))
    if len(jd_skills) > 0:
        score = round(len(matched) / len(jd_skills) * 100, 1)
    else:
        score = 0.0
    return matched, missing, extra, score


def get_verdict(score):
    if score >= 75:
        return "Strong match"
    if score >= 50:
        return "Moderate match"
    return "Low match"


def build_category_table(jd_skills, resume_skills):
    """For each category, count how many required skills are matched/missing."""
    rows = []
    for category in SKILLS:
        needed = [s for s, c in jd_skills.items() if c == category]
        if needed:
            got = [s for s in needed if s in resume_skills]
            rows.append(
                {
                    "Category": category,
                    "Matched": len(got),
                    "Missing": len(needed) - len(got),
                }
            )
    return pd.DataFrame(rows)


def build_skill_table(jd_skills, matched):
    """A table listing every skill the job requires and whether it was found."""
    rows = []
    for skill, category in sorted(jd_skills.items()):
        status = "Matched" if skill in matched else "Missing"
        rows.append({"Skill": skill, "Category": category, "Status": status})
    return pd.DataFrame(rows)


def build_report(r):
    """Create the text report that the user can download."""

    def bullet_lines(items):
        if items:
            return ["  - " + item for item in items]
        return ["  (none)"]

    lines = []
    lines.append("AI RESUME AND JOB DESCRIPTION MATCH REPORT")
    lines.append("=" * 50)
    lines.append("Generated: " + datetime.now().strftime("%d %b %Y, %I:%M %p"))
    lines.append("Resume file: " + r["filename"])
    lines.append("")
    lines.append("MATCH SCORE: " + str(r["score"]) + "% (" + r["verdict"] + ")")
    lines.append("Formula: matched skills / skills required in job description x 100")
    lines.append(
        "Calculation: "
        + str(len(r["matched"]))
        + " / "
        + str(len(r["jd_skills"]))
        + " x 100 = "
        + str(r["score"])
        + "%"
    )
    lines.append("")
    lines.append("MATCHED SKILLS (" + str(len(r["matched"])) + ")")
    lines += bullet_lines(r["matched"])
    lines.append("")
    lines.append("MISSING SKILLS (" + str(len(r["missing"])) + ")")
    lines += bullet_lines(r["missing"])
    lines.append("")
    lines.append("EXTRA SKILLS IN RESUME, NOT REQUESTED BY JOB (" + str(len(r["extra"])) + ")")
    lines += bullet_lines(r["extra"])
    lines.append("")
    lines.append("NEXT STEPS")
    lines.append("  - Add missing skills to your resume ONLY if you genuinely have them.")
    lines.append("  - Learn or build a small project for the important missing skills.")
    lines.append("")
    lines.append("Note: This tool uses keyword matching on a fixed skills list.")
    lines.append("It is a guide, not a guarantee of how any employer will screen you.")
    return "\n".join(lines)


# ----------------------------------------------------------------------
# 4. PAGE HEADER
# ----------------------------------------------------------------------
st.title("📄 AI Resume & Job Description Matcher")
st.caption(
    "Upload your resume, paste a job description, and see how well your "
    "technical skills match. Everything runs on your own computer."
)

with st.expander("How is the match percentage calculated?"):
    st.markdown(
        """
1. The app finds every known technical skill in the **job description**.
2. It finds every known technical skill in your **resume**.
3. **Match % = (job skills found in your resume ÷ total job skills) × 100**

Example: the job asks for 10 skills and your resume has 7 of them → 7 ÷ 10 × 100 = **70%**.

Score guide: **75%+ Strong**, **50–74% Moderate**, **below 50% Low**.
        """
    )

# ----------------------------------------------------------------------
# 5. INPUTS
# ----------------------------------------------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("1. Upload Resume (PDF)")
    uploaded_resume = st.file_uploader("Choose a PDF file", type=["pdf"])

with right_col:
    st.subheader("2. Paste Job Description")
    job_description = st.text_area(
        "Paste the full job description here",
        height=250,
        placeholder="Example: We need a developer with Python, SQL, Git, Docker and REST API experience...",
    )

analyze_clicked = st.button("🔍 Analyze Match", type="primary")

# ----------------------------------------------------------------------
# 6. RUN THE ANALYSIS WHEN THE BUTTON IS CLICKED
# We save results in st.session_state so they do not disappear when the
# page re-runs (for example after clicking a download button).
# ----------------------------------------------------------------------
if analyze_clicked:
    if uploaded_resume is None:
        st.error("Please upload your resume PDF first.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    else:
        try:
            resume_text = extract_pdf_text(uploaded_resume)
        except Exception as error:
            resume_text = ""
            st.error("Could not read this PDF: " + str(error))

        if resume_text and not resume_text.strip():
            st.error(
                "No text was found in this PDF. It may be a scanned image. "
                "Please upload a PDF where you can select and copy the text."
            )
        elif resume_text.strip():
            resume_skills = find_skills(resume_text)
            jd_skills = find_skills(job_description)

            if len(jd_skills) == 0:
                st.error(
                    "No known technical skills were found in the job description. "
                    "Paste the full description, or add more skills to the SKILLS list in app.py."
                )
            else:
                matched, missing, extra, score = calculate_match(resume_skills, jd_skills)
                st.session_state["result"] = {
                    "filename": uploaded_resume.name,
                    "resume_text": resume_text,
                    "resume_skills": resume_skills,
                    "jd_skills": jd_skills,
                    "matched": matched,
                    "missing": missing,
                    "extra": extra,
                    "score": score,
                    "verdict": get_verdict(score),
                }

# ----------------------------------------------------------------------
# 7. SHOW THE DASHBOARD
# ----------------------------------------------------------------------
if "result" in st.session_state:
    r = st.session_state["result"]

    st.divider()
    st.header("📊 Results")

    tab_dashboard, tab_details, tab_report = st.tabs(
        ["Dashboard", "Skill Details", "Download Report"]
    )

    # ---------------- TAB 1: DASHBOARD ----------------
    with tab_dashboard:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Match Score", str(r["score"]) + "%")
        c2.metric("Matched Skills", len(r["matched"]))
        c3.metric("Missing Skills", len(r["missing"]))
        c4.metric("Extra Skills in Resume", len(r["extra"]))

        st.progress(int(r["score"]) / 100)

        if r["score"] >= 75:
            st.success("Verdict: " + r["verdict"])
        elif r["score"] >= 50:
            st.warning("Verdict: " + r["verdict"])
        else:
            st.error("Verdict: " + r["verdict"])

        st.caption(
            "Calculation: "
            + str(len(r["matched"]))
            + " matched ÷ "
            + str(len(r["jd_skills"]))
            + " required × 100 = "
            + str(r["score"])
            + "%"
        )

        chart_left, chart_right = st.columns(2)

        with chart_left:
            pie_fig = px.pie(
                names=["Matched", "Missing"],
                values=[len(r["matched"]), len(r["missing"])],
                hole=0.5,
                color=["Matched", "Missing"],
                color_discrete_map={"Matched": "#2e9e5b", "Missing": "#d64545"},
                title="Matched vs Missing Skills",
            )
            st.plotly_chart(pie_fig)

        with chart_right:
            category_df = build_category_table(r["jd_skills"], r["resume_skills"])
            bar_fig = px.bar(
                category_df,
                x="Category",
                y=["Matched", "Missing"],
                barmode="stack",
                color_discrete_map={"Matched": "#2e9e5b", "Missing": "#d64545"},
                title="Skills by Category (required by the job)",
            )
            bar_fig.update_layout(yaxis_title="Number of skills", legend_title_text="")
            st.plotly_chart(bar_fig)

    # ---------------- TAB 2: SKILL DETAILS ----------------
    with tab_details:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.subheader("✅ Matched")
            if r["matched"]:
                for skill in r["matched"]:
                    st.write("- " + skill)
            else:
                st.write("None")

        with col_b:
            st.subheader("❌ Missing")
            if r["missing"]:
                for skill in r["missing"]:
                    st.write("- " + skill)
            else:
                st.write("None. Your resume covers every skill in the job description!")

        with col_c:
            st.subheader("➕ Extra in Resume")
            if r["extra"]:
                for skill in r["extra"]:
                    st.write("- " + skill)
            else:
                st.write("None")

        st.subheader("Full Skill Table")
        skill_df = build_skill_table(r["jd_skills"], r["matched"])
        st.dataframe(skill_df, hide_index=True)

        with st.expander("View text extracted from your resume PDF"):
            st.text(r["resume_text"])

    # ---------------- TAB 3: DOWNLOAD REPORT ----------------
    with tab_report:
        report_text = build_report(r)
        st.text(report_text)

        st.download_button(
            label="⬇️ Download Report (.txt)",
            data=report_text,
            file_name="resume_match_report.txt",
            mime="text/plain",
        )

        skill_df_download = build_skill_table(r["jd_skills"], r["matched"])
        st.download_button(
            label="⬇️ Download Skill Table (.csv)",
            data=skill_df_download.to_csv(index=False),
            file_name="resume_match_skills.csv",
            mime="text/csv",
        )