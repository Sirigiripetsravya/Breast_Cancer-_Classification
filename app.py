import os
import re
from io import BytesIO
from typing import List
from xml.sax.saxutils import escape

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "replace-me-in-production")

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
SYSTEM_MESSAGE = "You are a professional academic content writer."
PROMPT_TEMPLATE = """
Generate a well-structured, organized, and detailed document about the given topic.

Topic: {topic}

The document must follow this structure:

1. Title
2. Introduction
3. Background / History (if applicable)
4. Key Concepts / Main Explanation
5. Applications / Uses
6. Advantages
7. Disadvantages (if applicable)
8. Future Scope
9. Conclusion

Rules:
- Use clear headings.
- Use bullet points where necessary.
- Use simple but professional language.
- Make it detailed enough for a 5-8 page PDF.
- Avoid repeating information.
- Make it suitable for academic or presentation use.
- Proper spacing between sections.

Generate clean formatted text ready for PDF creation.
Do not include markdown code fences or XML/HTML tags.
""".strip()

SECTION_HINTS = (
    "title",
    "introduction",
    "background",
    "history",
    "key concepts",
    "main explanation",
    "applications",
    "uses",
    "advantages",
    "disadvantages",
    "future scope",
    "conclusion",
)


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it before generating content.")
    return OpenAI(api_key=api_key)


def extract_output_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    chunks: List[str] = []
    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            text_value = getattr(content, "text", None)
            if isinstance(text_value, str):
                chunks.append(text_value)
            elif hasattr(text_value, "value") and isinstance(text_value.value, str):
                chunks.append(text_value.value)
    return "\n".join(chunks).strip()


def build_prompt(topic: str) -> str:
    return PROMPT_TEMPLATE.format(topic=topic)


def generate_content(topic: str) -> str:
    client = get_openai_client()
    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": build_prompt(topic)},
        ],
        temperature=0.3,
        max_output_tokens=7000,
    )

    content = extract_output_text(response)
    if not content:
        raise RuntimeError("OpenAI returned an empty response.")
    return content


def clean_heading(line: str) -> str:
    heading = line.strip()
    heading = re.sub(r"^#{1,6}\s*", "", heading)
    heading = re.sub(r"^\d+[\.\)]\s*", "", heading)
    return heading.rstrip(":").strip()


def looks_like_heading(line: str) -> bool:
    candidate = clean_heading(line).lower()
    if not candidate:
        return False
    if any(candidate.startswith(section) for section in SECTION_HINTS):
        return True
    return line.endswith(":") and len(candidate) <= 110 and "." not in candidate


def add_page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 15 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(topic: str, content: str) -> BytesIO:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=21,
        leading=25,
        spaceAfter=10,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=17,
        spaceBefore=8,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "BodyCopy",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15,
        spaceAfter=4,
    )

    story = [Paragraph(escape(topic), title_style), Spacer(1, 4)]
    bullet_items: List[str] = []

    def flush_bullets() -> None:
        if not bullet_items:
            return
        list_flowable = ListFlowable(
            [
                ListItem(Paragraph(escape(item), body_style), leftIndent=8)
                for item in bullet_items
            ],
            bulletType="bullet",
            leftIndent=16,
            spaceAfter=6,
        )
        story.append(list_flowable)
        bullet_items.clear()

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            flush_bullets()
            story.append(Spacer(1, 5))
            continue

        bullet_match = re.match(r"^[-*•]\s+(.+)$", line)
        numbered_item_match = re.match(r"^\d+[\.\)]\s+(.+)$", line)

        if bullet_match:
            bullet_items.append(bullet_match.group(1).strip())
            continue
        if numbered_item_match and not looks_like_heading(line):
            bullet_items.append(numbered_item_match.group(1).strip())
            continue

        flush_bullets()

        if looks_like_heading(line):
            story.append(Paragraph(escape(clean_heading(line)), heading_style))
            continue

        cleaned_line = line.replace("**", "").replace("__", "")
        story.append(Paragraph(escape(cleaned_line), body_style))

    flush_bullets()

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer


@app.route("/")
def index():
    return render_template("index.html", model_name=DEFAULT_MODEL)


@app.post("/generate")
def generate_pdf():
    topic = request.form.get("topic", "").strip()
    if not topic:
        flash("Please enter a topic first.")
        return redirect(url_for("index"))

    try:
        generated_content = generate_content(topic)
        pdf_buffer = build_pdf(topic, generated_content)
    except Exception as exc:  # noqa: BLE001
        flash(f"Unable to generate PDF: {exc}")
        return redirect(url_for("index"))

    safe_topic = re.sub(r"[^a-zA-Z0-9_-]+", "_", topic).strip("_") or "generated_document"
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{safe_topic}.pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
