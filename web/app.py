import json
import io
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import config

os.environ["LANGCHAIN_API_KEY"] = config.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = str(config.langsmith_tracing).lower()
os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project

from flask import Flask, render_template, request, Response, stream_with_context, send_file
from backend.pipeline import stream_pipeline
from backend.document import extract_text_from_pdf, build_markdown_file, sanitize_filename

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    paper_file = request.files.get("paper_file")

    if not paper_file or paper_file.filename == "":
        def error_stream():
            yield f"data: error: {json.dumps('Please upload a PDF file.')}\n\n"

        return Response(stream_with_context(error_stream()), mimetype="text/event-stream")

    if not paper_file.filename.endswith(".pdf"):
        def error_stream():
            yield f"data: error: {json.dumps('Only PDF files are supported.')}\n\n"

        return Response(stream_with_context(error_stream()), mimetype="text/event-stream")

    try:
        raw_text = extract_text_from_pdf(paper_file)
    except Exception as e:
        def error_stream():
            yield f"data: error: {json.dumps('Could not read the PDF. Please make sure it is a text-based PDF, not a scanned image.')}\n\n"

        return Response(stream_with_context(error_stream()), mimetype="text/event-stream")

    def generate():
        try:
            last_result = None
            for chunk in stream_pipeline(raw_text):
                yield f"data: {chunk}"
                if "result: " in chunk:
                    payload_str = chunk.split("result: ", 1)[1].strip()
                    last_result = json.loads(payload_str)

            if last_result:
                import threading
                from backend.evaluators import run_evaluations

                def run_evals():
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        print(f"Running evals on keys: {list(last_result.keys())}")
                        scores = run_evaluations(last_result, raw_text)
                        print(f"Evaluation scores: {scores}")
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"Evaluation error: {e}")
                    finally:
                        loop.close()

                thread = threading.Thread(target=run_evals, daemon=True)
                thread.start()

        except ValueError as e:
            yield f"data: error: {json.dumps(str(e))}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: error: {json.dumps('Something unexpected went wrong. Please try again.')}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()

    if not data:
        return "No data provided.", 400

    posts = {
        "technical": data.get("technical"),
        "general": data.get("general"),
        "eli5": data.get("eli5")
    }

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for audience, post in posts.items():
            if not post:
                continue
            title = post.get("title", audience)
            content = post.get("content", "")
            filename = f"{sanitize_filename(title)}.md"
            md_buffer = build_markdown_file(title, content)
            zip_file.writestr(filename, md_buffer.read())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="blog_posts.zip"
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080, threaded=True)
