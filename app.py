import os
from pathlib import Path
from datetime import datetime
import json

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "app" / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "pptx", "png", "jpg", "jpeg", "webp", "docx", "xlsx", "csv"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- App --------------------
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")


# -------------------- Admin Login --------------------
login_manager = LoginManager()
login_manager.login_view = "admin_login"
login_manager.init_app(app)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

class AdminUser(UserMixin):
    id = "admin"

@login_manager.user_loader
def load_user(user_id):
    return AdminUser() if user_id == "admin" else None


# -------------------- Content --------------------
PROFILE = {
    "name": "Sydney Rebecca Sala",
    "tagline": "BUSINESS • STRATEGY • INNOVATION",
    "intro": "I turn ideas into structured strategies and real-world solutions.",
    # (optional) you can use this in about.html if you want:
    "email": "your@email.com",
    "phone": "+39XXXXXXXXXX",
    "linkedin": "https://www.linkedin.com/in/your-username",
    "instagram": "https://www.instagram.com/your-username",
}

DATA_FILE = BASE_DIR / "data" / "projects.json"

def load_projects():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_projects(projects):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


PROJECTS = load_projects()

SCHOOL = [
    {
        "period": "2025 – Present",
        "school": "Albert School × Mines Paris",
        "program": "Bachelor in Business & Data / AI (International Degree)",
        "location": "France (International program)",
        "highlights": [
            "International degree program combining business, data and AI",
        ],
        "logo": "schools/albert.png"
    },
    {
        "period": "2024 – 2025",
        "school": "Politecnico di Milano",
        "program": "Physical Engineering",
        "location": "Milan, Italy",
        "highlights": [
            "Linear Algebra — 27/30",
            "Telecommunications — 30/30",
        ],
        "logo": "schools/polimi.png"
    },
    {
        "period": "2019 – 2024",
        "school": "Liceo Gonzaga (Cambridge)",
        "program": "Liceo Scientifico",
        "location": "Italy",
        "highlights": [
            "Cambridge track",
        ],
        "logo": "schools/gonzaga.png"
    }
]

INTERESTS = [
    {
        "icon": "🌍",
        "title": "International Exposure & Market Observation",
        "details": "Curious about how culture and consumer behavior vary across countries. Travel helps me observe positioning and market dynamics."
    },
    {
        "icon": "🏃‍♀️",
        "title": "Discipline & Performance Mindset",
        "details": "Sport reinforces consistency, structure and long-term focus — the same mindset I apply to strategic projects."
    },
    {
        "icon": "♻️",
        "title": "Sustainability & Responsible Growth",
        "details": "Interested in how businesses integrate environmental responsibility into scalable growth models."
    },
    {
        "icon": "💻",
        "title": "Building & Coding",
        "details": "I enjoy building functional prototypes — turning strategy into execution."
    },
    {
        "icon": "🚀",
        "title": "Entrepreneurship & Innovation",
        "details": "Passionate about creating new ideas and transforming them into scalable products and opportunities."
    },
    {
        "icon": "🎵",
        "title": "Music & Creative Industries",
        "details": "Interested in the intersection between creativity, technology and business in the music industry."
    }
]

SKILLS = [
    {
        "category": "Strategy & Business",
        "list": [
            "Market Entry Strategy",
            "Business Development",
            "Growth & Expansion",
            "Brand Positioning",
            "Go-to-Market Strategy"
        ]
    },
    {
        "category": "Data & Analysis",
        "list": [
            "Data-driven decision making",
            "KPI design & analysis",
            "Market research",
            "Performance metrics (CPA, CVR, CTR)",
            "Forecasting models"
        ]
    },
    {
        "category": "Tools & Tech",
        "list": [
            "Python",
            "Streamlit",
            "Excel / Google Sheets",
            "WordPress",
            "PowerPoint / Deck building"
        ]
    },
    {
        "category": "Languages",
        "list": [
            "Italian (native)",
            "English (fluent)",
            "Spanish (intermediate)"
        ]
    }
]

VOLUNTEERING = [
    {
        "icon": "📚",
        "title": "L’Aquilone",
        "period": "2023–2025",
        "details": "Provided academic support to children, helping them with homework, study methods and confidence building."
    },
    {
        "icon": "🤝",
        "title": "ANPIL",
        "period": "2022–2025",
        "details": "Volunteered in community activities and social support initiatives organized by the association."
    }
]


def find_project(slug: str):
    for p in PROJECTS:
        if p.get("slug") == slug:
            return p
    return None


# -------------------- Routes --------------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        profile=PROFILE,
        projects=PROJECTS,
        school=SCHOOL,
        interests=INTERESTS,
        skills=SKILLS,
        volunteering=VOLUNTEERING,
    )

@app.route("/about")
def about():
    return render_template("about.html", profile=PROFILE)

@app.route("/work")
def work():
    return render_template("work.html", profile=PROFILE, projects=PROJECTS)

@app.route("/work/<slug>")
def project_detail(slug):
    project = find_project(slug)
    if not project:
        abort(404)
    return render_template("project_detail.html", profile=PROFILE, project=project)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Message received. (Next step: connect to email.)")
        return redirect(url_for("contact"))
    return render_template("contact.html", profile=PROFILE)


# -------------------- Admin --------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            login_user(AdminUser())
            return redirect(url_for("admin_panel"))
        flash("Wrong password.")
    return render_template("admin_login.html", profile=PROFILE)

@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_panel():
    """
    Create new projects (in-memory) and upload files to existing ones.
    NOTE: This starter stores projects in memory; restarting the server resets them.
    """
    if request.method == "POST":
        slug = request.form.get("slug", "").strip()
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        period = request.form.get("period", "").strip()
        summary = request.form.get("summary", "").strip()
        role = request.form.get("role", "").strip()
        tags_raw = request.form.get("tags", "").strip()
        tools_raw = request.form.get("tools", "").strip()
        deliverables_raw = request.form.get("deliverables", "").strip()
        highlights_raw = request.form.get("highlights", "").strip()
        kpis_raw = request.form.get("kpis", "").strip()
        links_raw = request.form.get("links", "").strip()

        if not slug or not title:
            flash("Slug and Title are required.")
            return redirect(url_for("admin_panel"))

        if find_project(slug):
            flash("That slug already exists. Use a different one.")
            return redirect(url_for("admin_panel"))

        # Parse multi-line fields
        tags = [t.strip() for t in tags_raw.split("\n") if t.strip()]
        tools = [t.strip() for t in tools_raw.split("\n") if t.strip()]
        deliverables = [d.strip() for d in deliverables_raw.split("\n") if d.strip()]
        highlights = [h.strip() for h in highlights_raw.split("\n") if h.strip()]
        kpis = [k.strip() for k in kpis_raw.split("\n") if k.strip()]

        links = []
        for line in links_raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            # format: Label | https://...
            if "|" in line:
                label, url = [x.strip() for x in line.split("|", 1)]
                links.append({"label": label, "url": url})
            else:
                links.append({"label": "Link", "url": line})

        PROJECTS.insert(0, {
            "slug": slug,
            "title": title,
            "company": company,
            "period": period,
            "summary": summary,
            "role": role,
            "tags": tags,
            "tools": tools,
            "deliverables": deliverables,
            "highlights": highlights,
            "kpis": kpis,
            "links": links,
            "files": [],
        })
        save_projects(PROJECTS)

        flash("Project created.")
        return redirect(url_for("admin_panel"))

    return render_template("admin.html", profile=PROFILE, projects=PROJECTS)

@app.route("/admin/upload/<slug>", methods=["POST"])
@login_required
def upload_file(slug):
    project = find_project(slug)
    if not project:
        abort(404)

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(url_for("admin_panel"))

    if not allowed_file(file.filename):
        flash("File type not allowed.")
        return redirect(url_for("admin_panel"))

    safe_name = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stored_name = f"{timestamp}-{safe_name}"
    file.save(str(UPLOAD_DIR / stored_name))

    project["files"].insert(0, {
        "original": safe_name,
        "stored": stored_name,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_projects(PROJECTS)


    flash("Uploaded.")
    return redirect(url_for("admin_panel"))


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)

@app.route("/thank-you")
def thank_you():
    return render_template("thankyou.html", profile=PROFILE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
