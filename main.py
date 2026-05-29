# ============================================
# AI RESUME ANALYZER - COMPLETE PROJECT
# Features: ATS Scoring, Skill Gap, YouTube, PDF
# ============================================

from flask import Flask, request, render_template, send_file
import os
import io
import docx2txt
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

# PDF generation library
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to store uploaded resumes

# ============================================
# SKILL DATABASE
# Each skill has: category, synonyms, YouTube link
# Synonyms help match different forms (e.g., "os" = "operating systems")
# ============================================

skill_data = {
    # ---------- Programming Languages ----------
    "python": {
        "category": "Programming",
        "synonyms": ["python", "py"],
        "youtube": "https://www.youtube.com/results?search_query=python+full+course+for+beginners+2025"
    },
    "java": {
        "category": "Programming",
        "synonyms": ["java", "oops", "object oriented programming"],
        "youtube": "https://www.youtube.com/results?search_query=java+spring+boot+full+course+2025"
    },
    "c++": {
        "category": "Programming",
        "synonyms": ["c++", "cpp", "c plus plus"],
        "youtube": "https://www.youtube.com/results?search_query=c%2B%2B+data+structures+algorithms+course"
    },
    "javascript": {
        "category": "Programming",
        "synonyms": ["javascript", "js", "nodejs", "node.js", "node js", "node"],
        "youtube": "https://www.youtube.com/results?search_query=javascript+full+course+2025"
    },

    # ---------- AI / Machine Learning ----------
    "machine learning": {
        "category": "AI/ML",
        "synonyms": ["machine learning", "ml"],
        "youtube": "https://www.youtube.com/results?search_query=machine+learning+full+course+2025"
    },
    "deep learning": {
        "category": "AI/ML",
        "synonyms": ["deep learning", "neural networks", "cnn", "rnn"],
        "youtube": "https://www.youtube.com/results?search_query=deep+learning+tensorflow+full+course"
    },
    "tensorflow": {
        "category": "AI/ML",
        "synonyms": ["tensorflow", "tf"],
        "youtube": "https://www.youtube.com/results?search_query=tensorflow+tutorial+for+beginners+2025"
    },
    "keras": {
        "category": "AI/ML",
        "synonyms": ["keras"],
        "youtube": "https://www.youtube.com/results?search_query=keras+deep+learning+tutorial"
    },
    "scikit-learn": {
        "category": "AI/ML",
        "synonyms": ["scikit-learn", "scikit learn", "sklearn"],
        "youtube": "https://www.youtube.com/results?search_query=scikit+learn+full+tutorial"
    },
    "numpy": {
        "category": "AI/ML",
        "synonyms": ["numpy"],
        "youtube": "https://www.youtube.com/results?search_query=numpy+python+tutorial"
    },
    "pandas": {
        "category": "AI/ML",
        "synonyms": ["pandas"],
        "youtube": "https://www.youtube.com/results?search_query=pandas+python+data+analysis+tutorial"
    },
    "nlp": {
        "category": "AI/ML",
        "synonyms": ["nlp", "natural language processing", "spacy", "nltk"],
        "youtube": "https://www.youtube.com/results?search_query=natural+language+processing+full+course"
    },
    "computer vision": {
        "category": "AI/ML",
        "synonyms": ["computer vision", "opencv", "cv"],
        "youtube": "https://www.youtube.com/results?search_query=opencv+computer+vision+full+course"
    },

    # ---------- Web Frameworks ----------
    "flask": {
        "category": "Web Framework",
        "synonyms": ["flask"],
        "youtube": "https://www.youtube.com/results?search_query=flask+python+full+tutorial+2025"
    },
    "django": {
        "category": "Web Framework",
        "synonyms": ["django"],
        "youtube": "https://www.youtube.com/results?search_query=django+python+full+tutorial+2025"
    },
    "react": {
        "category": "Web Framework",
        "synonyms": ["react", "reactjs", "react.js"],
        "youtube": "https://www.youtube.com/results?search_query=react+js+full+course+2025"
    },
    "api": {
        "category": "Web Framework",
        "synonyms": ["api", "rest api", "restful", "fastapi"],
        "youtube": "https://www.youtube.com/results?search_query=rest+api+python+flask+tutorial"
    },
    "html": {
        "category": "Web Framework",
        "synonyms": ["html", "css"],
        "youtube": "https://www.youtube.com/results?search_query=html+css+full+course"
    },

    # ---------- Databases ----------
    "sql": {
        "category": "Database",
        "synonyms": ["sql", "mysql", "postgresql", "postgres"],
        "youtube": "https://www.youtube.com/results?search_query=sql+full+course+for+beginners"
    },
    "mongodb": {
        "category": "Database",
        "synonyms": ["mongodb", "mongo", "nosql"],
        "youtube": "https://www.youtube.com/results?search_query=mongodb+full+tutorial+2025"
    },
    "dbms": {
        "category": "Database",
        "synonyms": ["dbms", "database management"],
        "youtube": "https://www.youtube.com/results?search_query=dbms+full+course+placements"
    },

    # ---------- DevOps & Cloud ----------
    "docker": {
        "category": "DevOps",
        "synonyms": ["docker", "containerization"],
        "youtube": "https://www.youtube.com/results?search_query=docker+full+tutorial+2025"
    },
    "kubernetes": {
        "category": "DevOps",
        "synonyms": ["kubernetes", "k8s"],
        "youtube": "https://www.youtube.com/results?search_query=kubernetes+full+tutorial+for+beginners"
    },
    "aws": {
        "category": "Cloud",
        "synonyms": ["aws", "amazon web services", "cloud"],
        "youtube": "https://www.youtube.com/results?search_query=aws+full+course+for+beginners"
    },
    "git": {
        "category": "DevOps",
        "synonyms": ["git", "github", "gitlab", "version control"],
        "youtube": "https://www.youtube.com/results?search_query=git+github+full+tutorial"
    },

    # ---------- Core Computer Science ----------
    "operating systems": {
        "category": "Core CS",
        "synonyms": ["operating systems", "operating system", "os"],
        "youtube": "https://www.youtube.com/results?search_query=operating+system+full+course+placements"
    },
    "data structures": {
        "category": "Core CS",
        "synonyms": ["data structures", "dsa", "algorithms", "data structures and algorithms"],
        "youtube": "https://www.youtube.com/results?search_query=dsa+full+course+java+placements"
    },
    "computer networks": {
        "category": "Core CS",
        "synonyms": ["computer networks", "cn", "networking"],
        "youtube": "https://www.youtube.com/results?search_query=computer+networks+full+course"
    },

    # ---------- Data Visualization ----------
    "matplotlib": {
        "category": "Visualization",
        "synonyms": ["matplotlib", "seaborn", "data visualization"],
        "youtube": "https://www.youtube.com/results?search_query=matplotlib+seaborn+python+tutorial"
    },
    "power bi": {
        "category": "Visualization",
        "synonyms": ["power bi", "powerbi"],
        "youtube": "https://www.youtube.com/results?search_query=power+bi+full+tutorial+2025"
    },
    "tableau": {
        "category": "Visualization",
        "synonyms": ["tableau"],
        "youtube": "https://www.youtube.com/results?search_query=tableau+full+tutorial+2025"
    },
}

# Build reverse lookup: synonym → skill name
# Example: "os" → "operating systems", "dsa" → "data structures"
all_skill_synonyms = {}
for skill_name, data in skill_data.items():
    for synonym in data["synonyms"]:
        all_skill_synonyms[synonym] = skill_name


# ============================================
# TEXT EXTRACTION FUNCTIONS
# Extract text from PDF, DOCX, TXT files
# ============================================

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using PyPDF2"""
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def extract_text_from_docx(file_path):
    """Extract text from DOCX file using docx2txt"""
    return docx2txt.process(file_path)


def extract_text(file_path):
    """Main function: detects file type and extracts text accordingly"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return ""


# ============================================
# SKILL MATCHING FUNCTIONS
# Match skills using synonyms for better accuracy
# ============================================

def extract_skills_from_text(text):
    """
    Find all skills mentioned in a text using synonym matching.
    Example: If text has "os", it will match "operating systems".
    """
    text_lower = text.lower()
    found_skills = set()

    for synonym, skill_name in all_skill_synonyms.items():
        if synonym in text_lower:
            found_skills.add(skill_name)

    return list(found_skills)


def find_skill_in_text(skill_name, text_lower):
    """
    Check if a specific skill exists in resume text.
    Checks all synonyms of that skill.
    """
    data = skill_data.get(skill_name)
    if data:
        for synonym in data["synonyms"]:
            if synonym in text_lower:
                return True
    return False


# ============================================
# INTERVIEW QUESTION GENERATOR
# Generates questions based on JD keywords
# ============================================

def generate_interview_questions(job_description):
    """Generate interview questions based on skills found in JD"""
    jd_lower = job_description.lower()

    # Question bank organized by skill
    question_bank = {
        "python": [
            "Explain Python decorators with example",
            "What is GIL? How does it affect multithreading?",
            "Difference between list, tuple, set and dictionary?"
        ],
        "machine learning": [
            "Explain bias-variance tradeoff",
            "Difference between supervised and unsupervised learning?",
            "What is overfitting and how do you prevent it?"
        ],
        "deep learning": [
            "Explain CNN architecture",
            "What is backpropagation?",
            "Difference between RNN and LSTM?"
        ],
        "sql": [
            "Explain different types of JOINs with examples",
            "What is normalization? Explain 1NF, 2NF, 3NF",
            "How do indexes improve query performance?"
        ],
        "flask": [
            "Flask vs Django: When to use which?",
            "Explain Flask application context and request context",
            "What are Blueprints in Flask?"
        ],
        "django": [
            "Explain Django MVT architecture",
            "Django ORM vs raw SQL queries?",
            "What is middleware in Django?"
        ],
        "java": [
            "Explain OOPs pillars with examples in Java",
            "Abstract class vs Interface?",
            "How does garbage collection work in Java?"
        ],
        "docker": [
            "Docker vs Virtual Machine?",
            "Explain Dockerfile, Image, and Container",
            "What is Docker Compose?"
        ],
        "aws": [
            "Explain EC2, S3, and Lambda",
            "What is VPC in AWS?",
            "Difference between horizontal and vertical scaling?"
        ],
        "api": [
            "What is REST API? Explain HTTP methods",
            "Difference between REST and GraphQL?",
            "How do you handle authentication in APIs?"
        ],
    }

    # Collect questions for skills found in JD
    questions = []
    for skill, skill_questions in question_bank.items():
        # Check if skill or any of its synonyms is in JD
        skill_data_entry = skill_data.get(skill, {})
        synonyms = skill_data_entry.get("synonyms", [])
        if skill in jd_lower or any(syn in jd_lower for syn in synonyms):
            questions.extend(skill_questions)

    # If no specific questions, provide general questions
    if not questions:
        questions = [
            "Tell me about yourself and your technical background",
            "Describe your most challenging project and how you solved it",
            "What are your strengths and weaknesses as a developer?",
            "Why do you want to join this company?",
            "Where do you see yourself in 5 years?",
            "Explain a time you faced a conflict in a team",
            "How do you stay updated with new technologies?",
            "What's your approach to debugging complex issues?"
        ]

    return questions[:12]  # Return max 12 questions


# ============================================
# SMART SUGGESTIONS GENERATOR
# Creates personalized suggestions with YouTube links
# ============================================

def generate_smart_suggestions(missing_skills):
    """
    For each missing skill, create:
    - Category-based suggestion text
    - YouTube tutorial link
    """
    suggestions = []

    # Templates for different skill categories
    suggestion_templates = {
        "Programming": "Master {skill} - essential for technical interviews and development roles",
        "AI/ML": "Learn {skill} to build intelligent models and boost your AI/ML profile",
        "Web Framework": "Add {skill} to your stack - highly demanded for full-stack roles",
        "Database": "Strengthen {skill} skills - critical for backend and data roles",
        "DevOps": "Upskill in {skill} for modern deployment and CI/CD pipelines",
        "Cloud": "Get certified in {skill} - cloud skills are top-paying in 2025",
        "Core CS": "Brush up {skill} - frequently asked in technical interviews",
        "Visualization": "Learn {skill} to present data insights effectively",
    }

    for skill in missing_skills:
        data = skill_data.get(skill, {})
        category = data.get("category", "General")
        youtube_link = data.get("youtube", f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial")

        # Get the right template for this category
        template = suggestion_templates.get(category, "Add {skill} to strengthen your profile")
        description = template.format(skill=skill.title())

        suggestions.append({
            "skill": skill,
            "category": category,
            "description": description,
            "youtube": youtube_link
        })

    return suggestions


# ============================================
# PDF REPORT GENERATOR
# Creates professional downloadable PDF report
# ============================================

def generate_pdf_report(job_description, results, interview_questions):
    """
    Generate a professional PDF report containing:
    - Cover page with JD summary
    - Score table for each resume
    - Matched and missing skills
    - Improvement suggestions
    - Interview questions
    """
    # Create PDF in memory (no file saved on disk)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # --- Define custom styles ---
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=22, textColor=colors.HexColor('#007bff'),
        spaceAfter=6, alignment=1  # Center aligned
    )

    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey,
        alignment=1, spaceAfter=20
    )

    heading_style = ParagraphStyle(
        'SectionHead', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#333333'),
        spaceBefore=15, spaceAfter=8
    )

    subheading_style = ParagraphStyle(
        'SubHead', parent=styles['Heading3'],
        fontSize=12, textColor=colors.HexColor('#0056b3'),
        spaceBefore=10, spaceAfter=5
    )

    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'],
        fontSize=9, leading=13,
        textColor=colors.HexColor('#444444')
    )

    small_style = ParagraphStyle(
        'Small', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey
    )

    # Green tag for matched skills
    matched_style = ParagraphStyle(
        'Matched', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#2e7d32'),
        backColor=colors.HexColor('#e8f5e9')
    )

    # Red tag for missing skills
    missing_style = ParagraphStyle(
        'Missing', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#c62828'),
        backColor=colors.HexColor('#ffebee')
    )

    question_style = ParagraphStyle(
        'Question', parent=styles['Normal'],
        fontSize=9, leading=14, leftIndent=15,
        textColor=colors.HexColor('#333333')
    )

    # --- Build PDF content ---
    elements = []

    # ===== PAGE 1: COVER =====
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("AI Resume Analyzer", title_style))
    elements.append(Paragraph("Professional ATS Analysis Report", subtitle_style))

    date_style = ParagraphStyle('Date', parent=styles['Normal'],
                                fontSize=10, alignment=1, textColor=colors.grey)
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        date_style
    ))
    elements.append(Spacer(1, 0.3*inch))

    # Job Description Summary
    elements.append(Paragraph("Job Description Summary", heading_style))
    jd_summary = job_description[:500] + "..." if len(job_description) > 500 else job_description
    elements.append(Paragraph(jd_summary.replace('\n', '<br/>'), normal_style))
    elements.append(PageBreak())

    # ===== PAGE 2: RESUME RESULTS =====
    elements.append(Paragraph("Resume Analysis Results", heading_style))
    elements.append(Paragraph(f"Total Resumes Analyzed: {len(results)}", normal_style))
    elements.append(Spacer(1, 0.2*inch))

    # Loop through each resume result
    for i, resume in enumerate(results):
        # Resume header
        elements.append(Paragraph(f"Rank #{i+1}: {resume['filename']}", subheading_style))

        # Color code for decision
        if resume['decision'] == 'Shortlist':
            decision_color = '#2e7d32'  # Green
        elif resume['decision'] == 'Consider':
            decision_color = '#f57f17'  # Orange
        else:
            decision_color = '#c62828'  # Red

        # Score table
        score_data = [
            [
                Paragraph('<b>Metric</b>', normal_style),
                Paragraph('<b>Score</b>', normal_style),
                Paragraph('<b>Rating</b>', normal_style)
            ],
            [
                Paragraph('Similarity Score', normal_style),
                Paragraph(f"{resume['similarity']}%", normal_style),
                Paragraph('-', normal_style)
            ],
            [
                Paragraph('ATS Score', normal_style),
                Paragraph(f"{resume['ats_score']}%", normal_style),
                Paragraph(resume['level'], normal_style)
            ],
            [
                Paragraph('Decision', normal_style),
                Paragraph(resume['decision'], ParagraphStyle('D', parent=normal_style, textColor=decision_color)),
                Paragraph('-', normal_style)
            ]
        ]

        score_table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.15*inch))

        # Matched Skills
        elements.append(Paragraph('<b>Matched Skills:</b>', normal_style))
        if resume.get('matched_skills'):
            elements.append(Paragraph(', '.join(resume['matched_skills']), matched_style))
        else:
            elements.append(Paragraph('None', normal_style))

        elements.append(Spacer(1, 0.1*inch))

        # Missing Skills
        elements.append(Paragraph('<b>Missing Skills:</b>', normal_style))
        if resume.get('missing_skills'):
            elements.append(Paragraph(', '.join(resume['missing_skills']), missing_style))
        else:
            elements.append(Paragraph('None - Perfect Match!', matched_style))

        elements.append(Spacer(1, 0.1*inch))

        # Improvement Suggestions (top 5)
        elements.append(Paragraph('<b>Improvement Plan:</b>', normal_style))
        if resume.get('suggestions'):
            for sug in resume['suggestions'][:5]:
                bullet = f"• <b>{sug['skill'].title()}</b> [{sug['category']}]: {sug['description']}"
                elements.append(Paragraph(bullet, normal_style))
        else:
            elements.append(Paragraph('No improvements needed!', normal_style))

        # Add separator between resumes (except last)
        if i < len(results) - 1:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph('<hr width="100%" color="#dddddd" size="0.5"/>', normal_style))

    elements.append(PageBreak())

    # ===== PAGE 3: INTERVIEW QUESTIONS =====
    elements.append(Paragraph("Interview Preparation Questions", heading_style))
    elements.append(Paragraph("Based on Job Description keywords", small_style))
    elements.append(Spacer(1, 0.15*inch))

    for j, question in enumerate(interview_questions, 1):
        elements.append(Paragraph(f"{j}. {question}", question_style))
        elements.append(Spacer(1, 0.05*inch))

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=7, textColor=colors.grey, alignment=1)
    elements.append(Paragraph("Generated by AI Resume Analyzer | Powered by Flask & Machine Learning", footer_style))
    elements.append(Paragraph("YouTube learning resources available in web version", footer_style))

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)  # Reset buffer position to beginning
    return buffer


# ============================================
# FLASK ROUTES
# ============================================

@app.route("/")
def home():
    """Home page - shows upload form"""
    return render_template(
        "matchresume.html",
        message=None,
        top_resumes=[],
        similarity_scores=[],
        ats_scores=[],
        resume_levels=[],
        recruiter_decisions=[],
        matched_skills_all=[],
        missing_skills_all=[],
        improvement_suggestions=[],
        interview_questions=[]
    )


@app.route('/matcher', methods=['POST'])
def matcher():
    """
    Main processing route:
    1. Receives JD + resume files
    2. Extracts text from resumes
    3. Calculates similarity using TF-IDF + Cosine Similarity
    4. Matches skills using synonym matching
    5. Calculates weighted ATS score
    6. Generates suggestions and interview questions
    """
    # Get form data
    job_description = request.form['job_description']
    resume_files = request.files.getlist('resumes')

    resumes = []
    filenames = []

    # Save and extract text from each uploaded resume
    for file in resume_files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        resumes.append(extract_text(file_path))
        filenames.append(file.filename)

    # If no files uploaded, return error
    if not resumes or not job_description:
        return render_template(
            "matchresume.html",
            message="Please upload resumes and enter job description",
            top_resumes=[], similarity_scores=[], ats_scores=[],
            resume_levels=[], recruiter_decisions=[],
            matched_skills_all=[], missing_skills_all=[],
            improvement_suggestions=[], interview_questions=[]
        )

    # ===== STEP 1: TF-IDF Vectorization & Cosine Similarity =====
    vectorizer = TfidfVectorizer(stop_words='english')
    all_texts = [job_description] + resumes
    vectors = vectorizer.fit_transform(all_texts).toarray()

    job_vector = vectors[0]
    resume_vectors = vectors[1:]
    similarities = cosine_similarity([job_vector], resume_vectors)[0]

    # ===== STEP 2: Extract skills from JD =====
    jd_skills = extract_skills_from_text(job_description)

    # Critical skills get double weight in ATS scoring
    critical_skills = ["python", "java", "machine learning", "sql", "data structures", "aws", "docker"]

    # ===== STEP 3: Analyze each resume =====
    results = []

    for i, resume_text in enumerate(resumes):
        resume_lower = resume_text.lower()

        # Find matched and missing skills
        matched_skills = []
        missing_skills = []

        for skill in jd_skills:
            if find_skill_in_text(skill, resume_lower):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Calculate weighted ATS score
        if jd_skills:
            total_weight = 0
            earned_weight = 0
            for skill in jd_skills:
                # Critical skills get 2x weight
                weight = 2 if skill in critical_skills else 1
                total_weight += weight
                if skill in matched_skills:
                    earned_weight += weight
            ats_score = round((earned_weight / total_weight) * 100, 2)
        else:
            ats_score = 0

        # Determine level
        if ats_score >= 80:
            level = "Excellent"
        elif ats_score >= 60:
            level = "Good"
        elif ats_score >= 40:
            level = "Average"
        else:
            level = "Weak"

        # Determine recruiter decision
        if ats_score >= 75:
            decision = "Shortlist"
        elif ats_score >= 50:
            decision = "Consider"
        else:
            decision = "Reject"

        # Generate smart suggestions for missing skills
        suggestions = generate_smart_suggestions(missing_skills)

        # Store result
        results.append({
            "filename": filenames[i],
            "similarity": round(similarities[i] * 100, 2),
            "ats_score": ats_score,
            "level": level,
            "decision": decision,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        })

    # ===== STEP 4: Sort & limit to top 5 =====
    results = sorted(results, key=lambda x: (x["ats_score"], x["similarity"]), reverse=True)[:5]

    # ===== STEP 5: Extract flat lists for template =====
    top_resumes = [r["filename"] for r in results]
    similarity_scores = [r["similarity"] for r in results]
    ats_scores = [r["ats_score"] for r in results]
    resume_levels = [r["level"] for r in results]
    recruiter_decisions = [r["decision"] for r in results]
    matched_skills_all = [r["matched_skills"] for r in results]
    missing_skills_all = [r["missing_skills"] for r in results]
    improvement_suggestions = [r["suggestions"] for r in results]

    # Generate interview questions
    interview_questions = generate_interview_questions(job_description)

    # ===== STEP 6: Store data for PDF download =====
    app.config['LAST_RESULTS'] = results
    app.config['LAST_JD'] = job_description
    app.config['LAST_QUESTIONS'] = interview_questions

    # ===== STEP 7: Render results page =====
    return render_template(
        "matchresume.html",
        message=f"Analysis complete - Top {len(results)} matching resumes found",
        top_resumes=top_resumes,
        similarity_scores=similarity_scores,
        ats_scores=ats_scores,
        resume_levels=resume_levels,
        recruiter_decisions=recruiter_decisions,
        matched_skills_all=matched_skills_all,
        missing_skills_all=missing_skills_all,
        improvement_suggestions=improvement_suggestions,
        interview_questions=interview_questions
    )


@app.route('/download-report')
def download_report():
    """
    Generate and download PDF report.
    Uses data from the last analysis (stored in app.config).
    """
    # Get stored data from last analysis
    last_results = app.config.get('LAST_RESULTS')
    last_jd = app.config.get('LAST_JD')
    last_questions = app.config.get('LAST_QUESTIONS')

    # If no analysis has been run yet
    if not last_results:
        return "No analysis data found. Please run an analysis first.", 400

    # Generate PDF
    pdf_buffer = generate_pdf_report(last_jd, last_results, last_questions)

    # Send PDF as downloadable file
    return send_file(
        pdf_buffer,
        download_name=f"Resume_Analysis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf',
        as_attachment=True
    )


# ============================================
# START THE APP
# ============================================
if __name__ == '__main__':
    # Create uploads folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Run Flask development server
    app.run(debug=True)