import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

# Configure logging if not already configured by the app environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
MODEL_NAME = "models/gemini-2.5-flash"
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY is not set in environment or .env file!")
    logger.error("Please create a .env file with: GEMINI_API_KEY=your_key_here")

client = genai.Client(api_key=api_key) if api_key else None

app = FastAPI()

# Include file upload analyze router
try:
    from .routes import analyze
except ImportError:
    # Fallback when imported directly by uvicorn
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from routes import analyze

app.include_router(analyze.router, prefix="/analyze", tags=["Analyze"])

# ---------------- SCHEMA ----------------
class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    result: str

# ---------------- ROUTES ----------------

@app.get("/")
def health_check():
    return {"status": "ok"}


def _extract_response_text(response) -> str:
    if hasattr(response, "generations") and response.generations:
        return response.generations[0].content
    if hasattr(response, "text"):
        return response.text
    return str(response)


@app.post("/analyze/text", response_model=AnalyzeResponse)
def analyze_document(req: AnalyzeRequest):
    if not client:
        raise HTTPException(status_code=500, detail="LLM client is not configured")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"""
You are an expert document analyst.

Analyze the document and return:
1. Summary
2. Key points
3. Risks (if any)
4. Recommendations

Document:
{req.text}
""",
            supported_actions=["generateContent"],
        )

        result_text = _extract_response_text(response)
        return {"result": result_text}

    except Exception as e:
        logger.exception("Text analyze failed: %s", e)
        raise HTTPException(status_code=500, detail="Insight generation failed")
