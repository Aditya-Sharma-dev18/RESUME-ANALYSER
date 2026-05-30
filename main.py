# ============================================
# AI RESUME ANALYZER - COMPLETE PROJECT
# Features: ATS Scoring, Skill Gap, YouTube, PDF
# 50+ Skills with Synonym Matching
# Deployed on Render
# ============================================

from flask import Flask, request, render_template, send_file
import os
import io
import docx2txt
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


# ============================================
# COMPLETE SKILL DATABASE
# Each skill has: category, synonyms, YouTube learning link
# Synonyms help match different forms (e.g., "os" = "operating systems")
# ============================================

skill_data = {

    # ==================== PROGRAMMING LANGUAGES ====================
    "python": {
        "category": "Programming",
        "synonyms": ["python", "py"],
        "youtube": "https://www.youtube.com/results?search_query=python+full+course+2025"
    },
    "java": {
        "category": "Programming",
        "synonyms": ["java", "oops", "object oriented programming"],
        "youtube": "https://www.youtube.com/results?search_query=java+full+course+2025"
    },
    "c++": {
        "category": "Programming",
        "synonyms": ["c++", "cpp", "c plus plus"],
        "youtube": "https://www.youtube.com/results?search_query=c%2B%2B+full+course"
    },
    "javascript": {
        "category": "Programming",
        "synonyms": ["javascript", "js", "nodejs", "node.js", "node"],
        "youtube": "https://www.youtube.com/results?search_query=javascript+full+course"
    },
    "typescript": {
        "category": "Programming",
        "synonyms": ["typescript", "ts"],
        "youtube": "https://www.youtube.com/results?search_query=typescript+full+course"
    },
    "c#": {
        "category": "Programming",
        "synonyms": ["c#", "c sharp", ".net"],
        "youtube": "https://www.youtube.com/results?search_query=c+sharp+full+course"
    },
    "php": {
        "category": "Programming",
        "synonyms": ["php"],
        "youtube": "https://www.youtube.com/results?search_query=php+full+course"
    },
    "swift": {
        "category": "Programming",
        "synonyms": ["swift", "ios"],
        "youtube": "https://www.youtube.com/results?search_query=swift+full+course"
    },
    "kotlin": {
        "category": "Programming",
        "synonyms": ["kotlin"],
        "youtube": "https://www.youtube.com/results?search_query=kotlin+full+course"
    },
    "go": {
        "category": "Programming",
        "synonyms": ["go", "golang"],
        "youtube": "https://www.youtube.com/results?search_query=golang+full+course"
    },
    "rust": {
        "category": "Programming",
        "synonyms": ["rust"],
        "youtube": "https://www.youtube.com/results?search_query=rust+full+course"
    },

    # ==================== AI / MACHINE LEARNING ====================
    "machine learning": {
        "category": "AI/ML",
        "synonyms": ["machine learning", "ml"],
        "youtube": "https://www.youtube.com/results?search_query=machine+learning+full+course"
    },
    "deep learning": {
        "category": "AI/ML",
        "synonyms": ["deep learning", "neural networks", "cnn", "rnn"],
        "youtube": "https://www.youtube.com/results?search_query=deep+learning+full+course"
    },
    "tensorflow": {
        "category": "AI/ML",
        "synonyms": ["tensorflow", "tf"],
        "youtube": "https://www.youtube.com/results?search_query=tensorflow+tutorial"
    },
    "keras": {
        "category": "AI/ML",
        "synonyms": ["keras"],
        "youtube": "https://www.youtube.com/results?search_query=keras+tutorial"
    },
    "scikit-learn": {
        "category": "AI/ML",
        "synonyms": ["scikit-learn", "sklearn"],
        "youtube": "https://www.youtube.com/results?search_query=scikit+learn+tutorial"
    },
    "numpy": {
        "category": "AI/ML",
        "synonyms": ["numpy"],
        "youtube": "https://www.youtube.com/results?search_query=numpy+tutorial"
    },
    "pandas": {
        "category": "AI/ML",
        "synonyms": ["pandas"],
        "youtube": "https://www.youtube.com/results?search_query=pandas+tutorial"
    },
    "nlp": {
        "category": "AI/ML",
        "synonyms": ["nlp", "natural language processing", "spacy", "nltk"],
        "youtube": "https://www.youtube.com/results?search_query=nlp+full+course"
    },
    "computer vision": {
        "category": "AI/ML",
        "synonyms": ["computer vision", "opencv", "cv"],
        "youtube": "https://www.youtube.com/results?search_query=computer+vision+full+course"
    },
    "data science": {
        "category": "AI/ML",
        "synonyms": ["data science", "data scientist"],
        "youtube": "https://www.youtube.com/results?search_query=data+science+full+course"
    },

    # ==================== WEB FRAMEWORKS ====================
    "flask": {
        "category": "Web Framework",
        "synonyms": ["flask"],
        "youtube": "https://www.youtube.com/results?search_query=flask+tutorial"
    },
    "django": {
        "category": "Web Framework",
        "synonyms": ["django"],
        "youtube": "https://www.youtube.com/results?search_query=django+tutorial"
    },
    "react": {
        "category": "Web Framework",
        "synonyms": ["react", "reactjs", "react.js"],
        "youtube": "https://www.youtube.com/results?search_query=react+js+full+course"
    },
    "angular": {
        "category": "Web Framework",
        "synonyms": ["angular", "angularjs"],
        "youtube": "https://www.youtube.com/results?search_query=angular+full+course"
    },
    "vue": {
        "category": "Web Framework",
        "synonyms": ["vue", "vuejs"],
        "youtube": "https://www.youtube.com/results?search_query=vue+js+full+course"
    },
    "next.js": {
        "category": "Web Framework",
        "synonyms": ["next.js", "nextjs"],
        "youtube": "https://www.youtube.com/results?search_query=next+js+full+course"
    },
    "api": {
        "category": "Web Framework",
        "synonyms": ["api", "rest api", "restful", "fastapi", "graphql"],
        "youtube": "https://www.youtube.com/results?search_query=rest+api+tutorial"
    },
    "html": {
        "category": "Web Framework",
        "synonyms": ["html", "css", "html5", "css3"],
        "youtube": "https://www.youtube.com/results?search_query=html+css+full+course"
    },
    "bootstrap": {
        "category": "Web Framework",
        "synonyms": ["bootstrap", "tailwind"],
        "youtube": "https://www.youtube.com/results?search_query=bootstrap+tutorial"
    },

    # ==================== DATABASES ====================
    "sql": {
        "category": "Database",
        "synonyms": ["sql", "mysql", "postgresql", "postgres", "oracle"],
        "youtube": "https://www.youtube.com/results?search_query=sql+full+course"
    },
    "mongodb": {
        "category": "Database",
        "synonyms": ["mongodb", "mongo", "nosql"],
        "youtube": "https://www.youtube.com/results?search_query=mongodb+tutorial"
    },
    "dbms": {
        "category": "Database",
        "synonyms": ["dbms", "database management"],
        "youtube": "https://www.youtube.com/results?search_query=dbms+full+course"
    },
    "firebase": {
        "category": "Database",
        "synonyms": ["firebase"],
        "youtube": "https://www.youtube.com/results?search_query=firebase+tutorial"
    },
    "redis": {
        "category": "Database",
        "synonyms": ["redis", "caching"],
        "youtube": "https://www.youtube.com/results?search_query=redis+tutorial"
    },

    # ==================== DEVOPS & CLOUD ====================
    "docker": {
        "category": "DevOps",
        "synonyms": ["docker", "containerization"],
        "youtube": "https://www.youtube.com/results?search_query=docker+tutorial"
    },
    "kubernetes": {
        "category": "DevOps",
        "synonyms": ["kubernetes", "k8s"],
        "youtube": "https://www.youtube.com/results?search_query=kubernetes+tutorial"
    },
    "jenkins": {
        "category": "DevOps",
        "synonyms": ["jenkins", "ci/cd", "cicd"],
        "youtube": "https://www.youtube.com/results?search_query=jenkins+tutorial"
    },
    "terraform": {
        "category": "DevOps",
        "synonyms": ["terraform", "iac"],
        "youtube": "https://www.youtube.com/results?search_query=terraform+tutorial"
    },
    "aws": {
        "category": "Cloud",
        "synonyms": ["aws", "amazon web services", "cloud"],
        "youtube": "https://www.youtube.com/results?search_query=aws+full+course"
    },
    "azure": {
        "category": "Cloud",
        "synonyms": ["azure", "microsoft azure"],
        "youtube": "https://www.youtube.com/results?search_query=azure+full+course"
    },
    "gcp": {
        "category": "Cloud",
        "synonyms": ["gcp", "google cloud"],
        "youtube": "https://www.youtube.com/results?search_query=google+cloud+full+course"
    },
    "git": {
        "category": "DevOps",
        "synonyms": ["git", "github", "gitlab", "version control"],
        "youtube": "https://www.youtube.com/results?search_query=git+github+tutorial"
    },
    "linux": {
        "category": "DevOps",
        "synonyms": ["linux", "unix", "bash", "shell scripting"],
        "youtube": "https://www.youtube.com/results?search_query=linux+full+course"
    },

    # ==================== CORE COMPUTER SCIENCE ====================
    "operating systems": {
        "category": "Core CS",
        "synonyms": ["operating systems", "operating system", "os"],
        "youtube": "https://www.youtube.com/results?search_query=operating+system+full+course"
    },
    "data structures": {
        "category": "Core CS",
        "synonyms": ["data structures", "dsa", "algorithms"],
        "youtube": "https://www.youtube.com/results?search_query=dsa+full+course"
    },
    "computer networks": {
        "category": "Core CS",
        "synonyms": ["computer networks", "cn", "networking"],
        "youtube": "https://www.youtube.com/results?search_query=computer+networks+full+course"
    },
    "software engineering": {
        "category": "Core CS",
        "synonyms": ["software engineering", "sdlc", "agile", "scrum"],
        "youtube": "https://www.youtube.com/results?search_query=software+engineering+full+course"
    },

    # ==================== DATA VISUALIZATION ====================
    "matplotlib": {
        "category": "Visualization",
        "synonyms": ["matplotlib", "seaborn", "data visualization"],
        "youtube": "https://www.youtube.com/results?search_query=matplotlib+seaborn+tutorial"
    },
    "power bi": {
        "category": "Visualization",
        "synonyms": ["power bi", "powerbi"],
        "youtube": "https://www.youtube.com/results?search_query=power+bi+tutorial"
    },
    "tableau": {
        "category": "Visualization",
        "synonyms": ["tableau"],
        "youtube": "https://www.youtube.com/results?search_query=tableau+tutorial"
    },
    "excel": {
        "category": "Visualization",
        "synonyms": ["excel", "google sheets", "spreadsheet"],
        "youtube": "https://www.youtube.com/results?search_query=excel+full+tutorial"
    },

    # ==================== BLOCKCHAIN & WEB3 ====================
    "blockchain": {
        "category": "Blockchain",
        "synonyms": ["blockchain", "web3", "ethereum", "smart contracts", "solidity"],
        "youtube": "https://www.youtube.com/results?search_query=blockchain+full+course"
    },
    "solidity": {
        "category": "Blockchain",
        "synonyms": ["solidity"],
        "youtube": "https://www.youtube.com/results?search_query=solidity+tutorial"
    },

    # ==================== CYBERSECURITY ====================
    "cybersecurity": {
        "category": "Security",
        "synonyms": ["cybersecurity", "cyber security", "ethical hacking", "penetration testing"],
        "youtube": "https://www.youtube.com/results?search_query=cybersecurity+full+course"
    },

    # ==================== MOBILE DEVELOPMENT ====================
    "android": {
        "category": "Mobile",
        "synonyms": ["android", "kotlin"],
        "youtube": "https://www.youtube.com/results?search_query=android+development+full+course"
    },
    "flutter": {
        "category": "Mobile",
        "synonyms": ["flutter", "dart"],
        "youtube": "https://www.youtube.com/results?search_query=flutter+full+course"
    },
    "react native": {
        "category": "Mobile",
        "synonyms": ["react native", "react-native"],
        "youtube": "https://www.youtube.com/results?search_query=react+native+full+course"
    },

    # ==================== DATA ENGINEERING ====================
    "hadoop": {
        "category": "Data Engineering",
        "synonyms": ["hadoop", "spark", "big data", "apache spark"],
        "youtube": "https://www.youtube.com/results?search_query=big+data+hadoop+spark+full+course"
    },
    "kafka": {
        "category": "Data Engineering",
        "synonyms": ["kafka", "apache kafka"],
        "youtube": "https://www.youtube.com/results?search_query=apache+kafka+tutorial"
    },
    "etl": {
        "category": "Data Engineering",
        "synonyms": ["etl", "data pipeline"],
        "youtube": "https://www.youtube.com/results?search_query=etl+tutorial"
    },

    # ==================== SOFT SKILLS ====================
    "communication": {
        "category": "Soft Skills",
        "synonyms": ["communication", "presentation", "interpersonal"],
        "youtube": "https://www.youtube.com/results?search_query=communication+skills"
    },
    "leadership": {
        "category": "Soft Skills",
        "synonyms": ["leadership", "team management", "mentoring"],
        "youtube": "https://www.youtube.com/results?search_query=leadership+skills"
    },
    "problem solving": {
        "category": "Soft Skills",
        "synonyms": ["problem solving", "critical thinking", "analytical"],
        "youtube": "https://www.youtube.com/results?search_query=problem+solving+skills"
    },

    # ==================== OTHER TOOLS ====================
    "jira": {
        "category": "Tools",
        "synonyms": ["jira", "confluence", "trello"],
        "youtube": "https://www.youtube.com/results?search_query=jira+tutorial"
    },
    "figma": {
        "category": "Tools",
        "synonyms": ["figma", "adobe xd"],
        "youtube": "https://www.youtube.com/results?search_query=figma+tutorial"
    },
}

# ============================================
# BUILD SYNONYM LOOKUP TABLE
# Example: "os" → "operating systems", "dsa" → "data structures"
# ============================================

all_skill_synonyms = {}
for skill_name, data in skill_data.items():
    for synonym in data["synonyms"]:
        all_skill_synonyms[synonym] = skill_name


# ============================================
# TEXT EXTRACTION FUNCTIONS
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
    """Detect file type and extract text accordingly"""
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
# ============================================

def extract_skills_from_text(text):
    """
    Find all skills mentioned in text using synonym matching.
    Example: "os" in text → matches "operating systems"
    """
    text_lower = text.lower()
    found_skills = set()

    for synonym, skill_name in all_skill_synonyms.items():
        if synonym in text_lower:
            found_skills.add(skill_name)

    return list(found_skills)


def find_skill_in_text(skill_name, text_lower):
    """Check if a specific skill exists in resume (checks all synonyms)"""
    data = skill_data.get(skill_name)
    if data:
        for synonym in data["synonyms"]:
            if synonym in text_lower:
                return True
    return False


# ============================================
# INTERVIEW QUESTION GENERATOR
# ============================================

def generate_interview_questions(job_description):
    """Generate interview questions based on skills found in JD"""
    jd_lower = job_description.lower()

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
        "blockchain": [
            "What is blockchain? How does it work?",
            "Explain smart contracts with example",
            "Difference between Proof of Work and Proof of Stake?"
        ],
        "cybersecurity": [
            "What is the CIA triad?",
            "Explain common web vulnerabilities (OWASP Top 10)",
            "Difference between encryption and hashing?"
        ],
    }

    questions = []
    for skill, skill_questions in question_bank.items():
        skill_data_entry = skill_data.get(skill, {})
        synonyms = skill_data_entry.get("synonyms", [])
        if skill in jd_lower or any(syn in jd_lower for syn in synonyms):
            questions.extend(skill_questions)

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

    return questions[:12]


# ============================================
# SMART SUGGESTIONS GENERATOR
# ============================================

def generate_smart_suggestions(missing_skills):
    """
    For each missing skill, create:
    - Category-based suggestion text
    - YouTube tutorial link
    """
    suggestions = []

    suggestion_templates = {
        "Programming": "Master {skill} - essential for technical interviews and development roles",
        "AI/ML": "Learn {skill} to build intelligent models and boost your AI/ML profile",
        "Web Framework": "Add {skill} to your stack - highly demanded for full-stack roles",
        "Database": "Strengthen {skill} skills - critical for backend and data roles",
        "DevOps": "Upskill in {skill} for modern deployment and CI/CD pipelines",
        "Cloud": "Get certified in {skill} - cloud skills are top-paying in 2025",
        "Core CS": "Brush up {skill} - frequently asked in technical interviews",
        "Visualization": "Learn {skill} to present data insights effectively",
        "Blockchain": "Explore {skill} - emerging field with high demand and great potential",
        "Security": "Master {skill} - critical for protecting systems and data from threats",
        "Mobile": "Build {skill} skills - mobile development market is booming in 2025",
        "Data Engineering": "Learn {skill} - handle large-scale data processing and pipelines",
        "Soft Skills": "Develop your {skill} - essential for professional growth and leadership",
        "Tools": "Get hands-on with {skill} - industry-standard tool used by top companies",
    }

    for skill in missing_skills:
        data = skill_data.get(skill, {})
        category = data.get("category", "General")
        youtube_link = data.get("youtube", f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial")

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
# ============================================

def generate_pdf_report(job_description, results, interview_questions):
    """Generate professional PDF report with scores, skills, and interview questions"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=22, 
                                   textColor=colors.HexColor('#007bff'), spaceAfter=6, alignment=1)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, 
                                      textColor=colors.grey, alignment=1, spaceAfter=20)
    heading_style = ParagraphStyle('SectionHead', parent=styles['Heading2'], fontSize=14, 
                                     textColor=colors.HexColor('#333333'), spaceBefore=15, spaceAfter=8)
    subheading_style = ParagraphStyle('SubHead', parent=styles['Heading3'], fontSize=12, 
                                        textColor=colors.HexColor('#0056b3'), spaceBefore=10, spaceAfter=5)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=9, 
                                    leading=13, textColor=colors.HexColor('#444444'))
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    matched_style = ParagraphStyle('Matched', parent=styles['Normal'], fontSize=8, 
                                    textColor=colors.HexColor('#2e7d32'), backColor=colors.HexColor('#e8f5e9'))
    missing_style = ParagraphStyle('Missing', parent=styles['Normal'], fontSize=8, 
                                    textColor=colors.HexColor('#c62828'), backColor=colors.HexColor('#ffebee'))
    question_style = ParagraphStyle('Question', parent=styles['Normal'], fontSize=9, 
                                      leading=14, leftIndent=15, textColor=colors.HexColor('#333333'))

    elements = []

    # --- PAGE 1: COVER ---
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("AI Resume Analyzer", title_style))
    elements.append(Paragraph("Professional ATS Analysis Report", subtitle_style))
    date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.grey)
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Job Description Summary", heading_style))
    jd_summary = job_description[:500] + "..." if len(job_description) > 500 else job_description
    elements.append(Paragraph(jd_summary.replace('\n', '<br/>'), normal_style))
    elements.append(PageBreak())

    # --- PAGE 2: RESUME RESULTS ---
    elements.append(Paragraph("Resume Analysis Results", heading_style))
    elements.append(Paragraph(f"Total Resumes Analyzed: {len(results)}", normal_style))
    elements.append(Spacer(1, 0.2*inch))

    for i, resume in enumerate(results):
        elements.append(Paragraph(f"Rank #{i+1}: {resume['filename']}", subheading_style))

        if resume['decision'] == 'Shortlist':
            decision_color = '#2e7d32'
        elif resume['decision'] == 'Consider':
            decision_color = '#f57f17'
        else:
            decision_color = '#c62828'

        score_data = [
            [Paragraph('<b>Metric</b>', normal_style), Paragraph('<b>Score</b>', normal_style), 
             Paragraph('<b>Rating</b>', normal_style)],
            [Paragraph('Similarity Score', normal_style), Paragraph(f"{resume['similarity']}%", normal_style), 
             Paragraph('-', normal_style)],
            [Paragraph('ATS Score', normal_style), Paragraph(f"{resume['ats_score']}%", normal_style), 
             Paragraph(resume['level'], normal_style)],
            [Paragraph('Decision', normal_style), 
             Paragraph(resume['decision'], ParagraphStyle('D', parent=normal_style, textColor=decision_color)), 
             Paragraph('-', normal_style)]
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

        elements.append(Paragraph('<b>✅ Matched Skills:</b>', normal_style))
        if resume.get('matched_skills'):
            elements.append(Paragraph(', '.join(resume['matched_skills']), matched_style))
        else:
            elements.append(Paragraph('None', normal_style))

        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph('<b>❌ Missing Skills:</b>', normal_style))
        if resume.get('missing_skills'):
            elements.append(Paragraph(', '.join(resume['missing_skills']), missing_style))
        else:
            elements.append(Paragraph('None - Perfect Match! 🎉', matched_style))

        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph('<b>💡 Improvement Plan:</b>', normal_style))
        if resume.get('suggestions'):
            for sug in resume['suggestions'][:5]:
                bullet = f"• <b>{sug['skill'].title()}</b> [{sug['category']}]: {sug['description']}"
                elements.append(Paragraph(bullet, normal_style))
        else:
            elements.append(Paragraph('No improvements needed! Perfect profile!', normal_style))

        if i < len(results) - 1:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph('<hr width="100%" color="#dddddd" size="0.5"/>', normal_style))

    elements.append(PageBreak())

    # --- PAGE 3: INTERVIEW QUESTIONS ---
    elements.append(Paragraph("Interview Preparation Questions", heading_style))
    elements.append(Paragraph("Based on Job Description keywords", small_style))
    elements.append(Spacer(1, 0.15*inch))

    for j, question in enumerate(interview_questions, 1):
        elements.append(Paragraph(f"{j}. {question}", question_style))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=colors.grey, alignment=1)
    elements.append(Paragraph("Generated by AI Resume Analyzer | Powered by Flask & Machine Learning", footer_style))
    elements.append(Paragraph("YouTube learning resources available in web version", footer_style))

    doc.build(elements)
    buffer.seek(0)
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
    3. Calculates TF-IDF similarity
    4. Matches skills using synonyms
    5. Calculates weighted ATS score
    6. Generates suggestions & interview questions
    """
    job_description = request.form['job_description']
    resume_files = request.files.getlist('resumes')

    resumes = []
    filenames = []

    for file in resume_files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        resumes.append(extract_text(file_path))
        filenames.append(file.filename)

    if not resumes or not job_description:
        return render_template(
            "matchresume.html",
            message="Please upload resumes and enter job description",
            top_resumes=[], similarity_scores=[], ats_scores=[],
            resume_levels=[], recruiter_decisions=[],
            matched_skills_all=[], missing_skills_all=[],
            improvement_suggestions=[], interview_questions=[]
        )

    # STEP 1: TF-IDF Vectorization & Cosine Similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    all_texts = [job_description] + resumes
    vectors = vectorizer.fit_transform(all_texts).toarray()
    job_vector = vectors[0]
    resume_vectors = vectors[1:]
    similarities = cosine_similarity([job_vector], resume_vectors)[0]

    # STEP 2: Extract skills from JD
    jd_skills = extract_skills_from_text(job_description)
    critical_skills = ["python", "java", "machine learning", "sql", "data structures", "aws", "docker"]

    # STEP 3: Analyze each resume
    results = []

    for i, resume_text in enumerate(resumes):
        resume_lower = resume_text.lower()
        matched_skills = []
        missing_skills = []

        for skill in jd_skills:
            if find_skill_in_text(skill, resume_lower):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Weighted ATS Score (critical skills = 2x)
        if jd_skills:
            total_weight = 0
            earned_weight = 0
            for skill in jd_skills:
                weight = 2 if skill in critical_skills else 1
                total_weight += weight
                if skill in matched_skills:
                    earned_weight += weight
            ats_score = round((earned_weight / total_weight) * 100, 2)
        else:
            ats_score = 0

        # Level
        if ats_score >= 80:
            level = "Excellent"
        elif ats_score >= 60:
            level = "Good"
        elif ats_score >= 40:
            level = "Average"
        else:
            level = "Weak"

        # Decision
        if ats_score >= 75:
            decision = "Shortlist"
        elif ats_score >= 50:
            decision = "Consider"
        else:
            decision = "Reject"

        suggestions = generate_smart_suggestions(missing_skills)

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

    # STEP 4: Sort & limit to top 5
    results = sorted(results, key=lambda x: (x["ats_score"], x["similarity"]), reverse=True)[:5]

    # STEP 5: Extract flat lists for template
    top_resumes = [r["filename"] for r in results]
    similarity_scores = [r["similarity"] for r in results]
    ats_scores = [r["ats_score"] for r in results]
    resume_levels = [r["level"] for r in results]
    recruiter_decisions = [r["decision"] for r in results]
    matched_skills_all = [r["matched_skills"] for r in results]
    missing_skills_all = [r["missing_skills"] for r in results]
    improvement_suggestions = [r["suggestions"] for r in results]

    interview_questions = generate_interview_questions(job_description)

    # STEP 6: Store for PDF download
    app.config['LAST_RESULTS'] = results
    app.config['LAST_JD'] = job_description
    app.config['LAST_QUESTIONS'] = interview_questions

    # STEP 7: Render results
    return render_template(
        "matchresume.html",
        message=f"✅ Analysis complete — Top {len(results)} matching resumes found",
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
    """Generate and download PDF report from last analysis"""
    last_results = app.config.get('LAST_RESULTS')
    last_jd = app.config.get('LAST_JD')
    last_questions = app.config.get('LAST_QUESTIONS')

    if not last_results:
        return "No analysis data found. Please run an analysis first.", 400

    pdf_buffer = generate_pdf_report(last_jd, last_results, last_questions)

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
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)