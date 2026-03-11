from io import BytesIO

from flask import Flask, render_template, request, send_file
from model import find_schemes, get_scheme_by_id

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ImportError:
    A4 = None
    simpleSplit = None
    stringWidth = None
    canvas = None

app = Flask(__name__)


def build_scheme_pdf(scheme):
    if canvas is None:
        raise RuntimeError("PDF export requires the 'reportlab' package. Install it with: pip install reportlab")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left_margin = 50
    right_margin = 50
    top_margin = 60
    bottom_margin = 50
    content_width = width - left_margin - right_margin
    y = height - top_margin

    def new_page():
        nonlocal y
        pdf.showPage()
        y = height - top_margin

    def ensure_space(required_height):
        nonlocal y
        if y - required_height < bottom_margin:
            new_page()

    def draw_text_block(text, font_name="Helvetica", font_size=11, gap=16):
        nonlocal y
        safe_text = text if text and text != "Not specified" else "Not specified"
        lines = []
        for paragraph in str(safe_text).splitlines() or [""]:
            lines.extend(simpleSplit(paragraph or " ", font_name, font_size, content_width))

        line_height = font_size + 4
        ensure_space(max(line_height * max(len(lines), 1), gap))
        pdf.setFont(font_name, font_size)
        for line in lines:
            if y - line_height < bottom_margin:
                new_page()
                pdf.setFont(font_name, font_size)
            pdf.drawString(left_margin, y, line)
            y -= line_height
        y -= gap - 4

    def draw_heading(text, font_name="Helvetica-Bold", font_size=14):
        nonlocal y
        ensure_space(font_size + 14)
        pdf.setFont(font_name, font_size)
        pdf.drawString(left_margin, y, text)
        y -= font_size + 6

    title = scheme.get("name", "Scheme Details")
    title_font = "Helvetica-Bold"
    title_size = 18
    title_lines = simpleSplit(title, title_font, title_size, content_width)
    ensure_space((title_size + 6) * max(len(title_lines), 1) + 16)
    pdf.setFont(title_font, title_size)
    for line in title_lines:
        pdf.drawString(left_margin, y, line)
        y -= title_size + 6

    pdf.setLineWidth(1)
    pdf.line(left_margin, y, width - right_margin, y)
    y -= 20

    category = scheme.get("category") or "Not specified"
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left_margin, y, "Category:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left_margin + stringWidth("Category:", "Helvetica-Bold", 11) + 8, y, str(category))
    y -= 24

    tags = scheme.get("tags")
    if tags and tags != "Not specified":
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(left_margin, y, "Tags:")
        pdf.setFont("Helvetica", 11)
        draw_text_block(str(tags), gap=12)

    sections = [
        ("About the Scheme", scheme.get("about")),
        ("Eligibility Criteria", scheme.get("eligibility")),
        ("Benefits", scheme.get("benefits")),
        ("Documents Required", scheme.get("documents")),
        ("How to Apply", scheme.get("application_process")),
        ("Official Website", scheme.get("official_link")),
    ]

    for heading, value in sections:
        draw_heading(heading)
        draw_text_block(value)

    pdf.save()
    buffer.seek(0)
    return buffer

@app.route("/", methods=["GET", "POST"])
def home():

    schemes = []
    form_data = {}

    if request.method == "POST":
        language   = request.form.get("language", "English")
        age        = request.form.get("age", "")
        occupation = request.form.get("occupation", "")
        gender     = request.form.get("gender", "")
        state      = request.form.get("state", "")
        query      = request.form.get("query", "")

        form_data = {
            "language":   language,
            "age":        age,
            "occupation": occupation,
            "gender":     gender,
            "state":      state,
            "query":      query,
        }

        schemes = find_schemes(
            query=query,
            language=language,
            age=age,
            occupation=occupation,
            gender=gender,
            state=state,
        )

    return render_template("index.html", schemes=schemes, form_data=form_data)


@app.route("/scheme/<int:scheme_id>")
def scheme_detail(scheme_id):
    language = request.args.get("lang", "English")
    scheme = get_scheme_by_id(scheme_id, language=language)
    if scheme is None:
        return "Scheme not found", 404
    return render_template("scheme_detail.html", scheme=scheme)


@app.route("/scheme/<int:scheme_id>/pdf")
def download_scheme_pdf(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if scheme is None:
        return "Scheme not found", 404

    try:
        pdf_buffer = build_scheme_pdf(scheme)
    except RuntimeError as exc:
        return str(exc), 500

    safe_name = "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "" for ch in scheme["name"]).strip()
    filename = f"{safe_name or 'scheme-details'}.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=False)

    
