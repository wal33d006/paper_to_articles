import fitz
import io


def extract_text_from_pdf(file) -> str:
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages = []
    for page in doc:
        pages.append(page.get_text())

    doc.close()
    return "\n".join(pages)


def build_markdown_file(title: str, content: str) -> io.BytesIO:
    output = io.BytesIO()
    output.write(content.encode("utf-8"))
    output.seek(0)
    return output


def sanitize_filename(title: str) -> str:
    keepable = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_")
    cleaned = "".join(c if c in keepable else "_" for c in title)
    return cleaned.strip().replace(" ", "_")[:60]