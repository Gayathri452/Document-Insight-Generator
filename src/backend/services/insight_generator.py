
import os
import logging
from google import genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables (in case they weren't loaded by main.py)
load_dotenv()

# Get API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment!")

# Create client
client = genai.Client(api_key=api_key) if api_key else None

# Model configuration
MODEL_NAME = "models/gemini-2.5-flash"


def _extract_response_text(response) -> str:
    """Robustly extract text content from various GenAI response shapes."""
    if not response:
        return ""
    # Newer client uses generations with `.content`
    if hasattr(response, "generations") and response.generations:
        try:
            return response.generations[0].content
        except Exception:
            pass
    # Some helpers expose `.text`
    if hasattr(response, "text") and response.text:
        return response.text
    # Fallback to string representation
    return str(response)


# ---------------- CORE FUNCTION ----------------
def generate_insights(chunks: list[str]) -> str:
    """
    Generate structured insights from retrieved document chunks using Gemini.
    Raises RuntimeError on failure so callers can log and return appropriate HTTP errors.
    """
    if not chunks:
        return "No relevant content found."

    # Join text with clear separation
    joined_text = "\n\n".join(chunks)

    # Construct a clean prompt for Gemini
    prompt = f"""
You are a professional document analyst. 

Analyze the following document excerpts and provide structured output:

1. Executive Summary (3-4 lines)
2. Key Insights (bullet points)
3. Risks / Issues (if any)
4. Actionable Recommendations

Document Excerpts:
{joined_text}
"""

    # Use try/except to catch API errors and let the caller handle them
    try:
        if not client:
            raise RuntimeError("Gemini API client not initialized. Check GEMINI_API_KEY environment variable.")
        
        logger.debug(f"Calling Gemini API with model {MODEL_NAME}, chunk count: {len(chunks)}")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        result_text = _extract_response_text(response)
        if not result_text:
            logger.warning("Gemini API returned empty content")
            raise RuntimeError("No insights were generated")
        logger.debug(f"Successfully generated insights (length: {len(result_text)})")
        return result_text
    except Exception as e:
        logger.exception(f"Failed to generate insights: {type(e).__name__}: {e}")
        raise RuntimeError(f"Insight generation failed: {str(e)}") from e
