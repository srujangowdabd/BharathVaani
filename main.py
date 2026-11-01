from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sarvamai import SarvamAI
from dotenv import load_dotenv
import tempfile
import os


# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)
# ============================================
# SARVAM AI CONFIGURATION
# ============================================

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    raise RuntimeError(
        "SARVAM_API_KEY not found in .env file"
    )

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)

print("Sarvam AI connected successfully!")

app = FastAPI()


# ============================================
# APP
# ============================================

app = FastAPI()


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# SARVAM AI
# ============================================

print("Connecting to Sarvam AI...")

sarvam = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)

print("Sarvam AI connected successfully!")


# ============================================
# LANGUAGE MAPPING
# ============================================

LANGUAGE_CODES = {

    "kn": "kn-IN",
    "kn-IN": "kn-IN",

    "ta": "ta-IN",
    "ta-IN": "ta-IN",

    "te": "te-IN",
    "te-IN": "te-IN",

    "hi": "hi-IN",
    "hi-IN": "hi-IN",

    "ml": "ml-IN",
    "ml-IN": "ml-IN",

    "mr": "mr-IN",
    "mr-IN": "mr-IN",

    "gu": "gu-IN",
    "gu-IN": "gu-IN",

    "bn": "bn-IN",
    "bn-IN": "bn-IN",

    "pa": "pa-IN",
    "pa-IN": "pa-IN",

    "en": "en-IN",
    "en-IN": "en-IN"
}


# ============================================
# HOME
# ============================================

@app.get("/")
def home():

    return {
        "message": "BharatVaani Civic AI Backend is running"
    }


# ============================================
# SPEECH → TEXT
# ============================================

@app.post("/transcribe")
async def transcribe(

    file: UploadFile = File(...),

    language: str = Form("kn")
):

    print("\n==============================")
    print("Speech transcription request")
    print("==============================")

    print("Received language:", language)

    # Convert frontend language to Sarvam language code

    language_code = LANGUAGE_CODES.get(
        language,
        "kn-IN"
    )

    print(
        "Sarvam language:",
        language_code
    )


    # ========================================
    # SAVE AUDIO TEMPORARILY
    # ========================================

    suffix = os.path.splitext(
        file.filename or ""
    )[1]

    if not suffix:

        suffix = ".webm"


    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        audio_data = await file.read()

        temp.write(audio_data)

        temp_path = temp.name


    try:

        print("Sending audio to Saaras v3...")


        # ====================================
        # SARVAM SPEECH TO TEXT
        # ====================================

        with open(temp_path, "rb") as audio_file:

            response = sarvam.speech_to_text.transcribe(

                file=audio_file,

                model="saaras:v3",

                mode="transcribe",

                language_code=language_code
            )


        transcript = response.transcript


        print(
            "Transcript:",
            transcript
        )


        return {

            "language": response.language_code,

            "text": transcript.strip()

        }


    except Exception as e:

        print(
            "Sarvam transcription error:",
            str(e)
        )

        return {

            "error": str(e)

        }


    finally:

        if os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================
# AI COMPLAINT ANALYSIS
# ============================================

@app.post("/analyze")
async def analyze_complaint(
    complaint: str = Form(...)
):

    try:

        print("====================================")
        print("AI COMPLAINT ANALYSIS")
        print("Complaint:", complaint)
        print("====================================")

        response = client.chat.completions(
            model="sarvam-105b",

            messages=[
                {
                    "role": "system",
                    "content": """
You are BharatVaani Civic AI.

Your job is to classify Indian citizen complaints.

Analyze the complaint and return:

1. category
2. department
3. priority

Allowed categories:

- Road & Infrastructure
- Water Supply
- Waste Management
- Street Lighting
- Electricity
- Public Transport
- Drainage & Sewage
- Healthcare
- Education
- Police & Safety
- Other

Priority rules:

High = emergency, accident risk, dangerous situation,
major water/electricity failure, public safety issue.

Medium = normal civic problem requiring government action.

Low = minor or non-urgent issue.

Return ONLY the requested JSON structure.
"""
                },

                {
                    "role": "user",
                    "content": complaint
                }
            ],

            temperature=0.1,

            request_options={
                "additional_body_parameters": {
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "civic_complaint",
                            "strict": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "category": {
                                        "type": "string"
                                    },
                                    "department": {
                                        "type": "string"
                                    },
                                    "priority": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "category",
                                    "department",
                                    "priority"
                                ],
                                "additionalProperties": False
                            }
                        }
                    }
                }
            }
        )

        # Get AI response

        raw_text = response.choices[0].message.content

        print("SARVAM RESPONSE:")
        print(raw_text)

        # Convert JSON text into Python object

        import json

        result = json.loads(raw_text)

        return {
            "original_text": complaint,
            "category": result["category"],
            "department": result["department"],
            "priority": result["priority"]
        }

    except Exception as e:

        print("❌ AI ANALYSIS ERROR:")
        print(str(e))

        return {
            "error": str(e)
        }