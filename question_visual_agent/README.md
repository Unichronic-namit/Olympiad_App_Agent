# 🎨 Question Visual Analysis Agent

An advanced AI-powered system that analyzes educational olympiad questions and generates detailed, professional image generation prompts using OpenAI's GPT-4o-mini. The system intelligently decides when visual aids would enhance student learning and creates publication-ready prompts optimized for any AI image generator (DALL-E, Midjourney, Stable Diffusion, etc.).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [Token Usage & Cost Optimization](#token-usage--cost-optimization)
- [Prompt Engineering](#prompt-engineering)
- [Output Examples](#output-examples)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This system is designed for educational content creators who need to enhance olympiad exam questions with appropriate visual aids. It uses advanced AI to:

1. **Analyze** each question's educational context (grade, difficulty, subject)
2. **Decide** if visual representation would improve comprehension
3. **Generate** extremely detailed image prompts (100-150 words) with precise specifications
4. **Ensure** all option images maintain perfect visual consistency
5. **Track** token usage and costs for optimization

## ✨ Features

### Core Capabilities
- ✅ **Intelligent Visual Analysis**: AI-driven decision on whether images enhance learning
- ✅ **Grade-Specific Design**: Age-appropriate styles for grades 1-10 (ages 6-15)
- ✅ **Detailed Prompts**: 100-150 word prompts with 10 mandatory elements
- ✅ **Universal Compatibility**: Works with any AI image generator
- ✅ **Fair Assessment**: Ensures visual consistency across all options
- ✅ **Batch Processing**: Parallel analysis of all questions in a grade
- ✅ **Token Optimization**: Reduced token usage by 90% through smart prompt engineering
- ✅ **Image Generation**: Integrated image generation using Stability AI or Hugging Face (NEW)
- ✅ **Automated Workflow**: From prompt analysis to image generation in one flow (NEW)

### Quality Assurance
- 📊 Word count validation (minimum 80 words)
- 🚫 Vague term detection (colorful, nice, good, simple)
- ⚖️ Fairness validation (all options have consistent images)
- 📝 Token usage logging for cost analysis
- 💾 Automatic database storage

## 🏗 Architecture

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Question Visual Agent       │
│  (agent.py)                 │
│                             │
│  • Fetch question data      │
│  • Build context            │
│  • Call OpenAI API          │
│  • Validate prompts         │
│  • Log token usage          │
└──────┬──────────────────────┘
       │
       ├──► Database (PostgreSQL)
       │    • question_visual_prompts
       │    • Store analysis results
       │
       └──► Token Log (token_usage_log.txt)
            • Track API costs
            • Monitor optimization
```

## 🛠 Tech Stack

- **AI Model**: OpenAI GPT-4o-mini
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **Libraries**:
  - `openai` (>=1.104.1,<2) - OpenAI API client
  - `psycopg2-binary==2.9.10` - PostgreSQL adapter
  - `python-dotenv==1.1.1` - Environment management
  - `requests==2.31.0` - HTTP library for image generation APIs

## 📁 Project Structure

```
question_visual_agent/
├── .env                      # Environment variables (NEVER commit!)
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── pipeline.svg            # System architecture diagram
├── token_usage_log.txt     # Token usage tracking (auto-generated)
│
├── main.py                 # CLI interface
├── agent.py                # Core AI analysis logic
├── database.py             # Database operations
├── image_generator.py      # Image generation module (NEW)
├── test_image_generator.py # Test script for image generation (NEW)
│
└── generated_images/       # Generated images stored here (auto-created)
    ├── q_2010_question.png
    ├── q_2010_option_a.png
    ├── q_2010_option_b.png
    └── ...
```

## 🚀 Installation

### 1. Prerequisites

- Python 3.11 or higher
- PostgreSQL database with olympiad question data
- OpenAI API key
- Git (optional)

### 2. Clone or Download

```bash
git clone <repository-url>
cd question_visual_agent
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create `.env` File

```bash
# Copy example (if provided) or create new
touch .env  # macOS/Linux
type nul > .env  # Windows
```

### 2. Add Configuration

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olympiad_db
DB_USER=postgres
DB_PASSWORD=your_password

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Image Generation API Configuration (NEW)
IMAGE_GEN_API_KEY=your_stability_or_huggingface_api_key
IMAGE_GEN_API_URL=https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image
```

### 3. Get API Keys

#### OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create new secret key
5. Copy to `.env` file

#### Image Generation API Key (Choose One)

**Option A: Stability AI (Paid, High Quality)**
1. Visit [Stability AI](https://platform.stability.ai/)
2. Sign up and add payment method
3. Get API key from dashboard
4. API URL: `https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image`
5. Cost: ~$0.002-0.004 per image

**Option B: Hugging Face (FREE, Good Quality)** ⭐ Recommended
1. Visit [Hugging Face](https://huggingface.co/)
2. Sign up (free, no credit card)
3. Settings → Access Tokens → New Token
4. Copy token
5. API URL: `https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0`
6. Cost: FREE!

## 🗄️ Database Setup

### Required Tables

#### 1. Existing Question Data

```sql
-- exam_overview
CREATE TABLE exam_overview (
  exam_overview_id INTEGER PRIMARY KEY,
  exam VARCHAR(100),
  grade SMALLINT CHECK (grade BETWEEN 1 AND 12),
  level SMALLINT
);

-- sections
CREATE TABLE sections (
  section_id INTEGER PRIMARY KEY,
  exam_overview_id INTEGER REFERENCES exam_overview(exam_overview_id),
  section VARCHAR(100)
);

-- syllabus
CREATE TABLE syllabus (
  syllabus_id INTEGER PRIMARY KEY,
  exam_overview_id INTEGER REFERENCES exam_overview(exam_overview_id),
  section_id INTEGER REFERENCES sections(section_id),
  topic VARCHAR(200),
  subtopic VARCHAR(200)
);

-- questions
CREATE TABLE questions (
  question_id INTEGER PRIMARY KEY,
  syllabus_id INTEGER REFERENCES syllabus(syllabus_id),
  difficulty VARCHAR(20),
  question_text TEXT,
  option_a TEXT,
  option_b TEXT,
  option_c TEXT,
  option_d TEXT,
  is_active BOOLEAN DEFAULT TRUE
);
```

#### 2. Analysis Results Table (Create This)

```sql
CREATE TABLE question_visual_prompts (
  id SERIAL PRIMARY KEY,
  question_id INT REFERENCES questions(question_id),
  image_required BOOLEAN,
  reason TEXT,
  question_image_prompt TEXT,
  option_a_image_prompt TEXT,
  option_b_image_prompt TEXT,
  option_c_image_prompt TEXT,
  option_d_image_prompt TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_question_visual_prompts_qid 
ON question_visual_prompts(question_id);
```

### Fix Sequences (If Needed)

```sql
-- If you get primary key conflicts
SELECT setval('question_visual_prompts_id_seq', 
              (SELECT COALESCE(MAX(id), 0) FROM question_visual_prompts), 
              true);
```

## 💻 Usage

### Run the Application

```bash
python main.py
```

### Option 1: Analyze Single Question

```
Choose an option:
1. Analyze a single question by ID
2. Analyze all questions for a specific grade
0. Exit

Enter your choice: 1
Enter question ID: 2010
```

**Output:**
```
🔍 Analyzing Question 2010...
🤖 Calling OpenAI API...

📊 Token Usage:
   Prompt: 2,847 tokens
   Completion: 523 tokens
   Total: 3,370 tokens
✅ Token usage logged to token_usage_log.txt

✅ Analysis complete!
   Image Required: True

🔍 Validating prompt quality...
✅ Question: 142 words
✅ Option A: 138 words
✅ Option B: 145 words
✅ Option C: 140 words
✅ Option D: 137 words

✅ All 4 options have images - Fair assessment maintained

💾 Saving to database...
✅ Saved to database with ID: 42
```

---

### Generate Images from Prompts (NEW)

After analyzing questions, you can generate images using the stored prompts:

#### Method 1: Using Python Script

```python
from image_generator import generate_images_for_question
from database import get_db

# Fetch prompts from database
conn = get_db()
cur = conn.cursor()
cur.execute("""
    SELECT question_id, image_required, question_image_prompt,
           option_a_image_prompt, option_b_image_prompt,
           option_c_image_prompt, option_d_image_prompt
    FROM question_visual_prompts
    WHERE question_id = 2010
""")
prompts_data = cur.fetchone()
conn.close()

# Generate all images
if prompts_data['image_required']:
    results = generate_images_for_question(2010, prompts_data)
```

#### Method 2: Test Single Image

```bash
python test_image_generator.py
```

**Output:**
```
🧪 Testing Image Generator

🎨 Generating image: q_1984_question.png
   Prompt preview: A bright cartoon illustration of Earth with a thick layer of colorful gases...

✅ Image saved: generated_images/q_1984_question.png

✅ Test successful!
📁 Image saved at: generated_images/q_1984_question.png
```

---

### Image Generation Features

The `image_generator.py` module provides:

**1. Single Image Generation:**
```python
from image_generator import generate_image

result = generate_image(
    prompt="Your detailed 100-150 word prompt...",
    question_id=2010,
    image_type="option",
    option="a"
)

if result['success']:
    print(f"Image saved at: {result['file_path']}")
```

**2. Batch Generation for Question:**
```python
from image_generator import generate_images_for_question

prompts = {
    "question_image_prompt": "...",
    "option_a_image_prompt": "...",
    "option_b_image_prompt": "...",
    "option_c_image_prompt": "...",
    "option_d_image_prompt": "..."
}

results = generate_images_for_question(2010, prompts)
print(f"Generated: {results['images_generated']} images")
print(f"Failed: {results['images_failed']} images")
```

**Image Naming Convention:**
- Question: `q_2010_question.png`
- Option A: `q_2010_option_a.png`
- Option B: `q_2010_option_b.png`
- Option C: `q_2010_option_c.png`
- Option D: `q_2010_option_d.png`

All images saved in: `generated_images/` folder (auto-created)

---

### Option 2: Batch Process by Grade

```
Enter your choice: 2
Enter grade (1-12): 5
Enter number of parallel workers (default 5): 10
```

**Features:**
- Parallel processing (10 workers = 10 questions simultaneously)
- Real-time progress tracking
- Summary statistics
- All results saved to database

**Output:**
```
🎯 ANALYZING ALL QUESTIONS FOR GRADE 5
📚 Fetching question IDs for grade 5...
✅ Found 45 questions for grade 5
🚀 Starting parallel processing with 10 workers...

✅ Progress: 10/45 questions completed
✅ Progress: 20/45 questions completed
✅ Progress: 30/45 questions completed
✅ Progress: 40/45 questions completed
✅ Progress: 45/45 questions completed

📊 SUMMARY FOR GRADE 5
Total Questions: 45
Successfully Analyzed: 45
Images Required: 28
No Images Needed: 17
Errors: 0
```

## 📊 Token Usage & Cost Optimization

### Token Breakdown

**Before Optimization:**
- User Prompt: ~2,000 tokens (sent every API call)
- System Prompt: ~300 tokens
- **Total per call: ~2,300 tokens**

**After Optimization:**
- User Prompt: ~200 tokens (sent every API call) ✅ **90% reduction!**
- System Prompt: ~2,500 tokens (cached by OpenAI)
- **Total per call: ~200 new tokens**

### Cost Analysis

**GPT-4o-mini Pricing:**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Per Question Cost:**
```
Input:  200 tokens × $0.00015 = $0.00003
Output: 500 tokens × $0.00060 = $0.00030
Total: ~$0.00033 per question
```

**Batch Processing (100 questions):**
- Cost: ~$0.033
- Time: ~2-3 minutes (with 10 workers)

### View Token Logs

```bash
cat token_usage_log.txt

# Output:
============================================================
Timestamp: 2025-01-15 14:23:45
Question ID: 2010
Prompt Tokens: 2847
Completion Tokens: 523
Total Tokens: 3370
============================================================
```

## 🎨 Prompt Engineering

### System Prompt (Static, ~2,500 tokens)

Contains:
- Expert persona and credentials
- Grade-specific visual guidelines (1-3, 4-5, 6-8, 9-10)
- When images ARE/NOT required
- Visual consistency rules
- 10-element prompt structure
- 3 detailed examples (150+ words each)
- Forbidden terms list
- Quality requirements

### User Prompt (Dynamic, ~200 tokens)

Contains only:
- Question ID, grade, difficulty
- Exam type and level
- Subject/topic
- Question text
- 4 options
- Brief task instruction

### 10-Element Prompt Structure

Every image prompt includes:
1. **Subject**: Precise object description
2. **Context**: Educational purpose
3. **Style**: Artistic approach (flat/realistic/diagram)
4. **Composition**: Angle, framing, position
5. **Colors**: Hex codes (#87CEEB)
6. **Background**: Solid white, gradient, etc.
7. **Lighting**: Type, direction, shadows
8. **Details**: Texture, finish, surface
9. **Technical**: Resolution, sharpness
10. **Tone**: Age-appropriate style

## 📸 Output Examples

### Example 1: Grade 2 - Computer Mouse

```json
{
  "question_id": 101,
  "grade": 2,
  "image_required": true,
  "reason": "Grade 2 students learning about input devices benefit significantly from visual identification of physical objects like computer mice.",
  "option_a_image_prompt": "A bright blue wireless computer mouse with rounded ergonomic shape, designed for teaching grade 2 students about input devices. Flat vector illustration style with bold black outlines. Mouse positioned in center of frame, occupying 60% of image space, shown from 45-degree top-right angle. Solid white background (#FFFFFF) with no shadows. Mouse colored in vibrant sky blue (#87CEEB) with darker navy blue (#4682B4) accent on scroll wheel. Two visible buttons clearly defined with thin separator line. Smooth cartoon-style rendering with minimal detail, no texture complexity. Soft even lighting from directly above, creating flat appearance. Matte plastic finish suggested through color flatness. High contrast against white background for clarity. Child-friendly and engaging. No text, labels, branding, or logos visible. Clean professional educational illustration suitable for young learners. 8K resolution, sharp clean edges, vector-style quality with no gradients."
}
```

### Example 2: Grade 8 - Circuit Board

```json
{
  "question_id": 205,
  "grade": 8,
  "image_required": true,
  "reason": "Visualizing computer hardware components through a circuit board image helps grade 8 students understand technical concepts in computer architecture.",
  "question_image_prompt": "Professional overhead macro photograph of a computer motherboard circuit board for teaching grade 8 technology students about computer hardware components. Photorealistic style with extreme detail. Rectangular green PCB centered in frame, occupying 75% of image. Standard FR-4 fiberglass green color (#2F4F2F) with golden-yellow copper traces (#FFD700) creating intricate pathways. Multiple components visible: black RAM slots, aluminum heat sinks in silver, colored capacitors, square microchips with pins. Shot from 90-degree angle. Bright white LED studio lighting eliminating harsh shadows. Sharp focus showing solder joints and fine details. Modern 2020s hardware. Clean white background (#FFFFFF) fading to light gray. Glossy PCB surface with matte components. Technical accuracy essential. No human elements. Product photography quality. 8K resolution, macro lens sharpness."
}
```

### Example 3: No Images Required

```json
{
  "question_id": 310,
  "grade": 7,
  "image_required": false,
  "reason": "This logical reasoning question tests abstract thinking skills and does not require visual aids as the text clearly conveys all necessary information.",
  "question_image_prompt": null,
  "option_a_image_prompt": null,
  "option_b_image_prompt": null,
  "option_c_image_prompt": null,
  "option_d_image_prompt": null
}
```

## 🐛 Troubleshooting

### Issue: "Question not found"

**Cause**: Question ID doesn't exist or is inactive.

**Solution**:
```sql
SELECT * FROM questions WHERE question_id = 2010;
-- Check if question exists and is_active = TRUE
```

### Issue: Database connection error

**Cause**: Wrong credentials or PostgreSQL not running.

**Solution**:
1. Verify PostgreSQL service is running
2. Check `.env` credentials
3. Test connection:
   ```bash
   psql -h localhost -U postgres -d olympiad_db
   ```

### Issue: OpenAI API error

**Cause**: Invalid API key or quota exceeded.

**Solution**:
1. Verify API key in `.env`
2. Check account credits at [OpenAI Platform](https://platform.openai.com/account/usage)
3. Ensure API key has proper permissions

### Issue: "Only X/4 options have images"

**Cause**: AI decided not all options need images.

**Impact**: May give unfair hints to students.

**Solution**: Review the question - if all options should have images, the AI might be making incorrect decisions. Consider refining the question or manually adjusting.

### Issue: Prompts contain vague terms

**Warning**: `⚠️  Option A: Contains vague terms: colorful, nice`

**Cause**: AI occasionally uses forbidden terms despite instructions.

**Solution**: This is tracked automatically. The prompt is still saved, but you may want to regenerate or manually edit.

### Issue: Image generation fails with "text_prompts: cannot be blank"

**Cause**: Using wrong API format for your image generation service.

**Solution**: The code is configured for Stability AI. If using Hugging Face, update `image_generator.py`:

**For Hugging Face:**
```python
# Change payload to:
payload = {
    "inputs": prompt
}

# And response handling to:
if response.status_code == 200:
    # Hugging Face returns image bytes directly
    with open(file_path, 'wb') as f:
        f.write(response.content)
```

**For Stability AI:** (Current code)
```python
# Keep existing code with text_prompts and base64 decoding
```

### Issue: Image generation timeout

**Cause**: Image generation takes 30-60 seconds per image.

**Solution**: 
- Timeout is set to 60 seconds (reasonable)
- If consistently timing out, check your API key and internet connection
- Consider generating images overnight for large batches

### Issue: "No image data in response"

**Cause**: Stability AI response format changed or API issue.

**Solution**:
1. Check Stability AI API status
2. Verify your API key is valid and has credits
3. Check the response format in their documentation

## 📝 Best Practices

1. **Run batch processing during off-peak hours** for better API performance
2. **Monitor token_usage_log.txt** regularly to track costs
3. **Back up database** before running large batch operations
4. **Use parallel workers wisely** (5-10 is optimal, don't exceed 20)
5. **Review validation warnings** for quality assurance
6. **Test with single questions** before batch processing

## 🔒 Security

- ⚠️ **NEVER** commit `.env` file to version control
- 🔐 Keep OpenAI API key secure and private
- 💾 Regularly backup `question_visual_prompts` table
- 🔑 Use read-only database user for production if possible

## 📈 Performance

- **Single Question Analysis**: ~3-5 seconds
- **Single Image Generation**: ~30-60 seconds (Stability AI) or ~10-20 seconds (Hugging Face)
- **Batch (100 questions, 10 workers)**: ~2-3 minutes (analysis only)
- **Batch Image Generation (100 questions × 5 images)**: ~4-8 hours
- **Token Usage**: ~200 tokens per question (optimized)
- **Analysis Cost**: ~$0.0003 per question
- **Image Cost**: FREE (Hugging Face) or ~$0.002-0.004 per image (Stability AI)

## 🚀 Future Enhancements

- [ ] Integrated workflow (analyze → generate images in one command)
- [ ] Image quality validation after generation
- [ ] Retry mechanism for failed image generations
- [ ] Progress bar for batch image generation
- [ ] Image compression and optimization
- [ ] Multiple image size options (512px, 1024px, 2048px)
- [ ] Web interface for easier access
- [ ] Multi-language support
- [ ] Custom prompt templates per subject
- [ ] Analytics dashboard for token usage and image generation stats
- [ ] Automatic cost alerts
- [ ] Background job queue for large batch processing

## 📄 License

This project is for educational purposes.

## 👥 Authors

Your Team - Educational Technology Division

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini API
- PostgreSQL community
- Python open-source community

---

**Made with ❤️ for better educational content**