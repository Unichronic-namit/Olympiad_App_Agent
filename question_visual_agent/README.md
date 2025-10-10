# 🎨 Question Visual Analysis Agent

An AI-powered agent that analyzes educational questions and determines whether visual representations (images) would enhance student understanding based on grade level, difficulty, and concept type.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Output Format](#output-format)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This agent uses OpenAI's GPT-4o-mini model to intelligently decide:
- Whether a question needs visual representation
- Where images would help (question text, options, or both)
- What type of images to generate (DALL-E prompts)

The analysis follows educational best practices to ensure visuals enhance learning without giving away answers.

## ✨ Features

- **Smart Visual Analysis**: AI-driven decision making based on grade and difficulty
- **Fair Assessment**: Ensures images don't reveal correct answers
- **Grade-Specific Rules**: 
  - Grades 1-5: Visuals almost always helpful
  - Grades 6-8: Visuals for spatial/real-world items
  - Grades 9-10: Visuals only for complex diagrams/graphs
- **Database Integration**: Automatically saves analysis results
- **DALL-E Ready**: Generates image prompts for question and options
- **Educational Focus**: Only suggests meaningful visuals, not decorative ones

## 🛠 Tech Stack

- **AI Model**: OpenAI GPT-4o-mini
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **Libraries**:
  - `openai` - OpenAI API client
  - `psycopg2-binary` - PostgreSQL adapter
  - `python-dotenv` - Environment variable management

## 📁 Project Structure

```
question_visual_agent/
├── .env                    # Environment variables (not in git)
├── requirements.txt        # Python dependencies
├── main.py                # Application entry point
├── agent.py               # AI analysis logic
└── database.py            # Database operations
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database with questions data
- OpenAI API key

### Steps

1. **Clone or create the project directory**
   ```bash
   mkdir question_visual_agent
   cd question_visual_agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### 1. Create `.env` file

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olympiad_db
DB_USER=postgres
DB_PASSWORD=your_password

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

## 🗄️ Database Setup

### Required Tables

The agent expects these tables to exist in your PostgreSQL database:

#### 1. Questions Data (Must exist)

```sql
-- exam_overview table
CREATE TABLE exam_overview (
  exam_overview_id INTEGER PRIMARY KEY,
  exam VARCHAR(100),
  grade SMALLINT CHECK (grade BETWEEN 1 AND 12),
  level SMALLINT,
  total_questions INTEGER,
  total_marks INTEGER,
  total_time_mins INTEGER
);

-- sections table
CREATE TABLE sections (
  section_id INTEGER PRIMARY KEY,
  exam_overview_id INTEGER REFERENCES exam_overview(exam_overview_id),
  section VARCHAR(100),
  no_of_questions INTEGER,
  marks_per_question INTEGER,
  total_marks INTEGER
);

-- syllabus table
CREATE TABLE syllabus (
  syllabus_id INTEGER PRIMARY KEY,
  exam_overview_id INTEGER REFERENCES exam_overview(exam_overview_id),
  section_id INTEGER REFERENCES sections(section_id),
  topic VARCHAR(200),
  subtopic VARCHAR(200)
);

-- questions table
CREATE TABLE questions (
  question_id INTEGER PRIMARY KEY,
  syllabus_id INTEGER REFERENCES syllabus(syllabus_id),
  difficulty VARCHAR(20),
  question_text TEXT,
  option_a TEXT,
  option_b TEXT,
  option_c TEXT,
  option_d TEXT,
  correct_option VARCHAR(5),
  solution TEXT,
  is_active BOOLEAN DEFAULT TRUE
);
```

#### 2. Visual Prompts Table (Agent creates this)

```sql
-- Table to store analysis results
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
```

## 💻 Usage

### Run the Agent

```bash
python main.py
```

### Input

The program will prompt you:
```
Enter question ID: 
```

Enter the ID of the question you want to analyze (e.g., `5`, `10`, `25`)

### Example Session

```
Enter question ID: 5

🔍 Analyzing Question 5...
   Grade: 3, Difficulty: easy
🤖 Calling OpenAI API...
✅ Analysis complete!
   Image Required: True

💾 Saving to database...
✅ Saved to database with ID: 1

============================================================
📊 FINAL RESULT
============================================================
{
  "question_id": 5,
  "grade": 3,
  "image_required": true,
  "reason": "For grade 3 students, visual representation of shapes helps concrete understanding. The question involves identifying geometric shapes which benefits greatly from visual aids.",
  "question_image_prompt": "Educational illustration showing a simple blue triangle with clear edges and labeled vertices, colorful and child-friendly style, white background",
  "option_a_image_prompt": "Simple circle shape, bright blue color, clean edges, minimalist educational style",
  "option_b_image_prompt": "Simple triangle shape, bright red color, clean edges, minimalist educational style",
  "option_c_image_prompt": "Simple square shape, bright green color, clean edges, minimalist educational style",
  "option_d_image_prompt": "Simple rectangle shape, bright yellow color, clean edges, minimalist educational style"
}
```

## 🔍 How It Works

### Step-by-Step Process

1. **Fetch Question Data**
   - Retrieves question from database with JOIN to get grade level
   - Includes question text, all options, difficulty, and grade

2. **AI Analysis**
   - Sends question details to OpenAI GPT-4o-mini
   - Uses structured prompt with educational guidelines
   - AI decides if images would help learning
   - Generates DALL-E prompts if images are beneficial

3. **Save Results**
   - Stores analysis in `question_visual_prompts` table
   - Includes all image prompts and reasoning
   - Timestamps the analysis

4. **Display Results**
   - Shows formatted JSON output
   - Includes all prompts and decision reasoning

### AI Decision Rules

The agent follows these educational principles:

**Grade 1-5 (Elementary)**
- Visuals almost always helpful
- Concrete visual representations aid understanding
- Images for both questions and options common

**Grade 6-8 (Middle School)**
- Visuals for spatial concepts
- Real-world items benefit from images
- Abstract concepts may not need visuals

**Grade 9-10 (High School)**
- Visuals only for complex diagrams
- Graphs, charts, and scientific models
- Text sufficient for most conceptual questions

**Fairness Rules**
- If options need images, ALL options get images
- Images maintain consistent style
- Visuals don't reveal correct answers
- No decorative or unnecessary images

## 📊 Output Format

### JSON Structure

```json
{
  "question_id": 5,
  "grade": 3,
  "image_required": true,
  "reason": "Explanation of why images help or don't help",
  "question_image_prompt": "DALL-E prompt for question image or null",
  "option_a_image_prompt": "DALL-E prompt for option A or null",
  "option_b_image_prompt": "DALL-E prompt for option B or null",
  "option_c_image_prompt": "DALL-E prompt for option C or null",
  "option_d_image_prompt": "DALL-E prompt for option D or null"
}
```

### Database Record

Saved in `question_visual_prompts` table:
- `id` - Auto-generated record ID
- `question_id` - Reference to questions table
- `image_required` - Boolean flag
- `reason` - Text explanation
- `question_image_prompt` - DALL-E prompt (or null)
- `option_a_image_prompt` - DALL-E prompt (or null)
- `option_b_image_prompt` - DALL-E prompt (or null)
- `option_c_image_prompt` - DALL-E prompt (or null)
- `option_d_image_prompt` - DALL-E prompt (or null)
- `created_at` - Timestamp

## 🐛 Troubleshooting

### Issue: "Question not found"

**Cause**: Question ID doesn't exist or question is inactive.

**Solution**: 
```sql
-- Check if question exists
SELECT * FROM questions WHERE question_id = 5;

-- Check if question has proper joins
SELECT q.*, e.grade 
FROM questions q
JOIN syllabus s ON q.syllabus_id = s.syllabus_id
JOIN exam_overview e ON s.exam_overview_id = e.exam_overview_id
WHERE q.question_id = 5;
```

### Issue: "Database connection error"

**Cause**: Wrong credentials in `.env` or PostgreSQL not running.

**Solution**:
1. Verify PostgreSQL service is running
2. Check credentials in `.env` file
3. Test connection manually:
   ```bash
   psql -h localhost -U postgres -d olympiad_db
   ```

### Issue: "OpenAI API error"

**Cause**: Invalid API key or quota exceeded.

**Solution**:
1. Verify API key in `.env` is correct
2. Check OpenAI account has credits
3. Visit [OpenAI Platform](https://platform.openai.com/account/usage)

### Issue: "Database error when saving"

**Cause**: `question_visual_prompts` table doesn't exist.

**Solution**: Create the table using the SQL in Database Setup section.

## 📝 Notes

- **API Costs**: Each analysis makes 1 OpenAI API call (~$0.0001-0.0003 per question)
- **Response Time**: Takes 2-5 seconds per question depending on API latency
- **Token Usage**: Average 500-800 tokens per analysis
- **Model**: Uses `gpt-4o-mini` for cost-effectiveness and speed

## 🔒 Security

- Never commit `.env` file to version control
- Keep OpenAI API key secure
- Use environment variables for all sensitive data
- Limit database user permissions appropriately

## 🚀 Future Enhancements

- [ ] Batch processing for multiple questions
- [ ] Parallel processing for faster analysis
- [ ] Grade-level batch analysis
- [ ] Image generation integration with DALL-E
- [ ] Web API interface
- [ ] Analytics dashboard
- [ ] Export results to CSV/JSON

## 📄 License

This project is for educational purposes.

## 🤝 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify database schema matches requirements
3. Check OpenAI API status
4. Review console output for error messages

---

Made with ❤️ for better educational content