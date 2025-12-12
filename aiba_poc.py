import os
from groq import Groq
from dotenv import load_dotenv

# Load your secret API key from the .env file
load_dotenv()

# Initialize Groq API client
# Groq will automatically use GROQ_API_KEY from environment, or you can pass it explicitly
api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
client = Groq(api_key=api_key) if api_key else Groq()

# --- STEP 1: READ (LOAD THE TEXT INPUT) ---
# Option 1: Read from a text file
text_file_path = "meeting_transcript.txt"  # Change this to your text file path

print("AIBA is reading... Loading the text input...")

try:
    # Try to read from file
    with open(text_file_path, "r", encoding="utf-8") as text_file:
        transcript_text = text_file.read()
    print("✅ Text loaded from file!")
except FileNotFoundError:
    # Option 2: Use direct text input if file doesn't exist
    print(f"⚠️  File '{text_file_path}' not found. Using direct text input...")
    transcript_text = """
    Paste your meeting transcript or text here.
    Replace this with your actual text content.
    """
    print("✅ Using direct text input!")
# print("\n--- Full Transcript ---") # You can uncomment this to see the full text
# print(transcript_text)


# --- STEP 2: UNDERSTAND (ANALYZE THE TRANSCRIPT) ---
# This is where the magic happens. We create a "prompt" to instruct the AI.
prompt = f"""
You are AIBA, an expert AI Business Analyst. Your task is to analyze the following meeting transcript.
Please read through the text and extract the following information in a clear, structured format:

1.  **Main Objective:** What is the single most important goal of the project being discussed?
2.  **Key Requirements:** List the specific functional or non-functional requirements mentioned. Use a bulleted list.
3.  **Identified Stakeholders/Users:** Who are the key people or roles mentioned in the discussion?
4.  **Decisions Made:** What clear decisions were agreed upon during the meeting?
5.  **Action Items:** List any tasks that need to be completed, and who is assigned to them (if mentioned).

Here is the transcript:
---
{transcript_text}
---
"""

print("\nAIBA is thinking... Analyzing the transcript to generate the BRD summary...")

# Try different Groq models in order of preference
models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
analysis_result = None
error_occurred = None

for model in models_to_try:
    try:
        print(f"Trying model: {model}...")
        # Analyze using Groq
        analysis_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a world-class AI Business Analyst designed to create structured summaries from meeting transcripts."},
                {"role": "user", "content": prompt}
            ]
        )
        analysis_result = analysis_response.choices[0].message.content
        print(f"✅ Successfully used model: {model}")
        break
    except Exception as e:
        error_occurred = e
        error_str = str(e).lower()
        # Check for quota/rate limit errors
        if "insufficient_quota" in error_str or "rate_limit" in error_str or "429" in error_str:
            print(f"⚠️  Model {model} failed: Quota/Rate limit issue. Trying next model...")
            continue
        # Check for model not found errors
        elif "model_not_found" in error_str or "does not exist" in error_str or "404" in error_str:
            print(f"⚠️  Model {model} not available. Trying next model...")
            continue
        # For other errors, still try next model but log it
        else:
            print(f"⚠️  Model {model} failed: {str(e)[:100]}... Trying next model...")
            continue

# Check if we got a result
if analysis_result is None:
    print("\n❌ Error: Could not analyze transcript with any available model.")
    print(f"Last error: {error_occurred}")
    print("\nPlease check:")
    print("1. Your GROQ_API_KEY is correct in .env file")
    print("2. You have available credits/quota in your Groq account")
    print("3. Your API key is valid at https://console.groq.com/")
    exit(1)

# --- STEP 3: REPORT (OUTPUT THE ANALYSIS) ---

print("✅ Analysis Complete! Here is the draft summary:")
print("--------------------------------------------------")
print(analysis_result)
print("--------------------------------------------------")