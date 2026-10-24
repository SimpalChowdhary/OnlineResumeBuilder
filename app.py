import re
from io import BytesIO
from xml.sax.saxutils import escape

from flask import Flask, render_template, request, send_file
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

FIELDS = {
    "full_name": "Full name",
    "email": "Email",
    "phone": "Phone number",
    "summary": "Professional summary",
    "education": "Education",
    "experience": "Work experience",
    "skills": "Technical skills",
    "projects": "Projects",
}
REQUIRED_FIELDS = ("full_name", "email")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def read_resume_form(form):
    """Return the supported form fields without persisting them."""
    return {field: form.get(field, "").strip() for field in FIELDS}


def validate_resume(resume):
    errors = []
    for field in REQUIRED_FIELDS:
        if not resume[field]:
            errors.append(f"{FIELDS[field]} is required.")

    if resume["email"] and not EMAIL_PATTERN.fullmatch(resume["email"]):
        errors.append("Enter a valid email address.")
    return errors


def add_pdf_paragraph(story, text, style):
    """Escape user text before passing it to ReportLab's markup parser."""
    safe_text = escape(text or "Not provided").replace("\n", "<br/>")
    story.append(Paragraph(safe_text, style))


def create_resume_pdf(resume):
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=f"{resume['full_name']} - Resume",
        author=resume["full_name"],
    )

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324d"),
        fontSize=22,
        spaceAfter=6,
    )
    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#526579"),
        fontSize=9,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "ResumeSection",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#176b67"),
        fontSize=12,
        leading=15,
        spaceBefore=9,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=3,
    )

    contact = " | ".join(value for value in (resume["email"], resume["phone"]) if value)
    story = []
    add_pdf_paragraph(story, resume["full_name"], name_style)
    add_pdf_paragraph(story, contact or "Contact details not provided", contact_style)

    for field in ("summary", "education", "experience", "skills", "projects"):
        story.append(Paragraph(FIELDS[field], section_style))
        add_pdf_paragraph(story, resume[field], body_style)

    document.build(story)
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET", "POST"])
def index():
    resume = read_resume_form(request.form) if request.method == "POST" else {}
    errors = validate_resume(resume) if request.method == "POST" else []
    if request.method == "POST" and not errors:
        return render_template("resume.html", resume=resume)
    return render_template("index.html", fields=FIELDS, resume=resume, errors=errors)


@app.post("/download")
def download():
    resume = read_resume_form(request.form)
    errors = validate_resume(resume)
    if errors:
        return render_template(
            "index.html", fields=FIELDS, resume=resume, errors=errors
        ), 400

    pdf = create_resume_pdf(resume)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="resume.pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
