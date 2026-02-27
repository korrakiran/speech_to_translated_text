import os
import sys
import mimetypes
from sarvamai import SarvamAI
from dotenv import load_dotenv

# --------- Load API Key ---------
load_dotenv()
API_KEY = os.getenv("sarv_api")

if not API_KEY:
    raise ValueError("SARV_API not found in .env file")

# --------- Argument Handling ---------
if len(sys.argv) > 1:
    audio_file_path = sys.argv[1]
else:
    # Default to Bowrampet.m4a if it exists and no argument provided
    default_file = "Bowrampet 2.m4a"
    if os.path.exists(default_file):
        audio_file_path = default_file
    else:
        print("Usage: python main.py <path_to_audio_file>")
        print(f"Default file '{default_file}' not found.")
        sys.exit(1)

if not os.path.exists(audio_file_path):
    print(f"Error: File not found: {audio_file_path}")
    sys.exit(1)

# --------- Content-Type Detection ---------
# Simple mapping for common extensions to Sarvam-allowed MIME types
extension_map = {
    '.m4a': 'audio/x-m4a',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.aac': 'audio/aac',
    '.flac': 'audio/flac',
    '.ogg': 'audio/ogg'
}

ext = os.path.splitext(audio_file_path)[1].lower()
content_type = extension_map.get(ext) or mimetypes.guess_type(audio_file_path)[0] or "application/octet-stream"

# --------- API Client ---------
client = SarvamAI(api_subscription_key=API_KEY)

print(f"Processing audio file: {audio_file_path} ...")
print(f"Detected Content-Type: {content_type}")

# --------- Transcription ---------
with open(audio_file_path, "rb") as f:
    response = client.speech_to_text.transcribe(
        file=(os.path.basename(audio_file_path), f, content_type),
        model="saaras:v3",
        mode="transcribe",
        language_code="unknown"  # Auto-detect language
    )

# --------- Process Result ---------
transcript = response.transcript.strip()

if not transcript:
    print("\nNo speech detected in the audio file.")
    sys.exit(0)

print("\n---- Transcription ----")
print(transcript)

# --------- Translation ---------
response = client.text.translate(
    input=transcript,
    source_language_code="auto",
    target_language_code="en-IN",
    speaker_gender="Male",
    mode="formal",
    model="mayura:v1",
    numerals_format="international"
)

# Extract translated text
if hasattr(response, "translated_text"):
    translated_text = response.translated_text
elif isinstance(response, dict):
    translated_text = response.get("translated_text", response)
else:
    translated_text = response

print("\n---- Final English Output ----")
print(translated_text)