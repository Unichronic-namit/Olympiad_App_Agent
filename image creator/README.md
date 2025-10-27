# Image Generator - Gemini API

Simple image generator that reads prompts from database and generates images using Google's Gemini API.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in this folder with:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olympiad_db
DB_USER=postgres
DB_PASSWORD=your_password

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the API key to your `.env` file

## Usage

Run the script:

```bash
python image_generator.py
```

Enter a question ID when prompted.

## Output

Images will be saved in:
```
generated_images/
└── question_2010/
    ├── question.png
    ├── option_a.png
    ├── option_b.png
    ├── option_c.png
    └── option_d.png
```

## Notes

- Only generates images for questions where `image_required = true`
- Each question gets its own folder
- Prompts come from the `question_visual_prompts` table
