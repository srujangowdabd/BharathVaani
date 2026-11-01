# BharatVaani – Civic AI

BharatVaani is an AI-powered civic complaint management backend designed to support multilingual citizen complaints in India.

## Features
- Speech-to-text transcription using Sarvam AI Saaras v3.
- Supports multiple Indian languages.
- AI-based civic complaint classification.
- Automatic department identification
- Complaint priority detection (High, Medium, Low).
- REST API built using FastAPI.

## Technologies Used
- Python
- FastAPI
- Sarvam AI
- REST API
- JSON

## API Endpoints
- `GET /` – Check backend status.
- `POST /transcribe` – Convert speech into text.
- `POST /analyze` – Analyze and classify civic complaints.

## Setup

1. Clone the repository.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Create a `.env` file and add your Sarvam API key.
4. Run the application:

   `uvicorn main:app --reload`

5. Open `http://127.0.0.1:8000/docs` to explore the API.

## Author
Srujan Gowda
