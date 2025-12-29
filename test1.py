from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

models = client.models.list()

for m in models:
    print("MODEL NAME:", m.name)
    print("RAW MODEL OBJECT:", m)
    print("-" * 50)
