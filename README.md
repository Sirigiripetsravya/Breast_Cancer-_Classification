# OpenAI Topic-to-PDF Flask App

This Flask web app lets a user enter a topic, generates detailed structured content with OpenAI, and automatically converts the result into a downloadable PDF using `reportlab`.

## Features

- Topic input via a simple web form
- Prompted academic-style structured output from OpenAI
- Automatic PDF creation with:
  - Section headings
  - Paragraph spacing
  - Bullet list rendering
  - Page numbers
- Instant browser download of the generated PDF

## Prompt Behavior

The app uses this instruction set while generating content:

- You are a professional academic content writer.
- Include:
  1. Title
  2. Introduction
  3. Background / History (if applicable)
  4. Key Concepts / Main Explanation
  5. Applications / Uses
  6. Advantages
  7. Disadvantages (if applicable)
  8. Future Scope
  9. Conclusion
- Make it clear, organized, detailed, and suitable for a 5-8 page PDF.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Add environment values:

   ```bash
   cp .env.example .env
   ```

3. Set at least:

   - `OPENAI_API_KEY`
   - (optional) `OPENAI_MODEL`
   - (optional) `FLASK_SECRET_KEY`

## Run

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## Notes

- Existing notebook files in `Breast cancer/` are untouched.
- `.env` is loaded automatically on startup via `python-dotenv`.
- If `OPENAI_API_KEY` is missing, the app shows an error message on submission.
