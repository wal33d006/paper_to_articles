# Paper to Articles

Upload a research paper (PDF) and get three blog posts instantly — one for technical readers, one for a general audience, and one explained like you're five. Powered by a multi-agent LangGraph pipeline running on Google Gemini.

## How it works

A LangGraph pipeline runs three parallel writer agents, each tailored to a different audience. A judge agent reviews the output and triggers rewrites if quality falls short. Results stream to the browser in real time and can be downloaded as Markdown files.

## Setup

### Prerequisites

- Python 3.12
- A [Google AI Studio](https://aistudio.google.com) API key (Gemini)
- Optional: [LangSmith](https://smith.langchain.com) API key for tracing
- Optional: [Confident AI](https://app.confident-ai.com) API key for LLM evaluation

### Local development

**1. Clone and create a virtual environment**

```bash
git clone <repo-url>
cd paper_to_articles
python3.12 -m venv .venv
source .venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r web/requirements.txt
pip install -e .
```

**3. Set environment variables**

Copy the example env file and fill in your keys:

```bash
cp .env.example .env.local
```

```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=paper-to-articles
CONFIDENT_API_KEY=your_confident_api_key_here
```

**4. Run**

```bash
python web/app.py
```

Open [http://localhost:8080](http://localhost:8080), upload a PDF, and watch the articles generate.

## Deployment (Google Cloud Run)

**1. Build and push the Docker image**

```bash
docker build --platform=linux/amd64 -t us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO>/<IMAGE>:latest .
docker push us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO>/<IMAGE>:latest
```

**2. Store secrets in GCP Secret Manager**

```bash
printf '%s' "your_key" | gcloud secrets create GOOGLE_API_KEY --data-file=- --project=<PROJECT_ID>
printf '%s' "your_key" | gcloud secrets create LANGCHAIN_API_KEY --data-file=- --project=<PROJECT_ID>
printf '%s' "your_key" | gcloud secrets create DEEPEVAL_API_KEY --data-file=- --project=<PROJECT_ID>
```

**3. Deploy**

```bash
gcloud run deploy paper-to-articles \
  --image=us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO>/<IMAGE>:latest \
  --region=us-central1 \
  --project=<PROJECT_ID> \
  --no-cpu-throttling \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=<PROJECT_ID>,LANGCHAIN_TRACING_V2=true,LANGCHAIN_PROJECT=paper-to-articles
```

## Project structure

```
agents/       LangGraph pipeline, Gemini agents, evaluation
web/          Flask app, templates, static files
Dockerfile    Production container (Gunicorn)
pyproject.toml Python package config
```
