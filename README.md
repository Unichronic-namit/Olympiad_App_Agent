# 🤖 Olympiad Question Generator Pipeline

**Automated Question Generation using AI Agents with Structured Output and Guardrails**

Automatically creates Olympiad questions for any exam, grade, and level using an AI agent with structured output validation, guardrails, and parallel processing.

## 📋 Overview

This question generator pipeline:
1. **Gets exam sections** from database based on exam, grade, and level
2. **Fetches syllabus topics** for each section
3. **Generates questions in parallel** using AI agent with guardrails
4. **Saves to database** with duplicate checking and validation
5. **Returns summary** of total questions created

## 🗂️ Project Structure

```
question_agent/
├── README.md              # This documentation
├── requirements.txt       # Python dependencies
├── __init__.py           # Package exports
├── simple_pipeline.py    # Main pipeline execution
├── agent_definition.py   # AI agent with guardrails
├── schemas.py           # Pydantic models for validation
└── prompts.py           # System prompts & prompt generation
```

## 🚀 Quick Start

### Installation
```bash
cd question_agent
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_database_connection_string
```

### Run Pipeline
```bash
python simple_pipeline.py
```

Or modify the main section for your specific exam:
```python
if __name__ == "__main__":
    asyncio.run(run_pipeline(exam="IMO", grade=6, level=2))
```

## 🔄 Complete Pipeline Flow

### **Step 1: Fetch Exam Overview**
`fetch_exam_overview_id(exam, grade, level)`

**What it does:** Finds the exam_overview_id for the specified exam, grade, and level

**Database Query:**
```sql
SELECT exam_overview_id
FROM exam_overview
WHERE LOWER(exam) = LOWER('IMO')
  AND grade = 6
  AND level = 2
LIMIT 1
```

**Console Output:**
```
Starting Olympiad Question Generator Pipeline
============================================================
```

---

### **Step 2: Get Exam Sections**
`get_exam_sections(exam_overview_id)`

**What it does:** Fetches all sections for the specified exam

**Database Query:**
```sql
SELECT s.section_id, s.section, s.no_of_questions, s.marks_per_question
FROM sections s
WHERE s.exam_overview_id = :exam_id
ORDER BY s.section_id
```

**Example Output:**
```python
[
    {
        "section_id": 1,
        "section_name": "Mathematics",
        "questions_needed": 10,
        "marks_per_question": 1
    },
    {
        "section_id": 2,
        "section_name": "Science", 
        "questions_needed": 8,
        "marks_per_question": 2
    }
]
```

**Console Output:**
```
Getting exam sections...
Found 2 sections:
  - Mathematics
  - Science
```

---

### **Step 3: Get Topics from Syllabus**
`get_section_topics(exam_overview_id, section_id)`

**What it does:** For each section, gets relevant topics from syllabus table

**Database Query:**
```sql
SELECT syllabus_id, topic, subtopic
FROM syllabus
WHERE exam_overview_id = :exam_id AND section_id = :section_id
ORDER BY syllabus_id
```

**Example Output for Mathematics:**
```python
[
    {
        "syllabus_id": 101,
        "topic": "Algebra",
        "subtopic": "Linear Equations"
    },
    {
        "syllabus_id": 102,
        "topic": "Geometry",
        "subtopic": "Area and Perimeter"
    }
]
```

**Console Output:**
```
Getting topics for each section...
  - Mathematics: 5 topics found
  - Science: 3 topics found
```

---

### **Step 4: Generate Questions with AI Agent**
`generate_questions_with_agent(section_info, topics, exam, grade, level)` **[PARALLEL]**

**What it does:** Uses AI agent with guardrails to generate structured questions

#### **🤖 Agent Configuration:**
```python
question_agent = Agent(
    name="Question Generator",
    instructions=SYSTEM_PROMPT,
    output_type=QuestionBatch,
    output_guardrails=[structure_output_guardrail]
)
```

#### **🛡️ Built-in Guardrails:**
- **Structure Validation:** Ensures valid QuestionBatch format
- **Content Appropriateness:** Age-appropriate for specified grade
- **Unique Options:** No duplicate or banned options
- **Educational Standards:** Factually accurate content

#### **📝 User Prompt Generation:**
`make_user_prompt_for_section()` creates context-aware prompts:

**Key Features:**
- **Exam/Grade/Level Context:** Tailored difficulty and content
- **Topic Integration:** Uses both topic and subtopic when available
- **Structured Output:** JSON schema enforcement
- **Quality Requirements:** Unique, educational, age-appropriate

#### **⚡ Parallel Execution:**
```python
# All sections run simultaneously!
tasks = [generate_questions_for_section(section_info, topics, exam, grade, level) 
         for section_info, topics in section_data]
results = await asyncio.gather(*tasks)
```

**Console Output:**
```
Generating questions for 2 sections in parallel...
Time taken for completion (Mathematics) - 8.45
Time taken for completion (Science) - 7.23
SUCCESS: Generated 10 questions for Mathematics
SUCCESS: Generated 8 questions for Science
```

---

### **Step 5: Save Questions to Database**
`save_questions_to_db(questions, section_name)`

**What it does:** Saves generated questions with comprehensive duplicate checking

#### **Duplicate Detection:**
```sql
SELECT question_id FROM questions
WHERE LOWER(question_text) = LOWER(:question_text)
```

#### **Insert with Full Tracking:**
```sql
INSERT INTO questions (
    syllabus_id, difficulty, question_text,
    option_a, option_b, option_c, option_d,
    correct_option, solution, is_active,
    created_at, updated_at
) VALUES (...)
RETURNING question_id
```

**Advanced Features:**
- **Duplicate Logging:** Reports existing question IDs when duplicates found
- **New ID Tracking:** Shows newly inserted question IDs
- **Error Recovery:** Individual question failures don't stop the pipeline
- **Batch Processing:** Efficient database operations

**Console Output:**
```
Saving questions to database...
NOTICE: Duplicate detected. Existing question_ids: [1245]
Duplicate detected. New inserted question_id: 1847
SAVED: Mathematics: 9 questions saved
SAVED: Science: 8 questions saved
```

---

### **Step 6: Pipeline Summary**

**Final Console Output:**
```
============================================================
Pipeline Complete!
Total questions saved: 17
============================================================
```

## 🔧 Key Features

### **🤖 Advanced AI Agent Integration**
- **Structured Output:** Pydantic schema validation
- **Smart Guardrails:** Content and format validation
- **Context-Aware:** Adapts to exam/grade/level
- **Error Recovery:** Graceful handling of failures

### **🛡️ Comprehensive Guardrails**
- **Structure Validation:** Ensures valid JSON output
- **Content Filtering:** Age-appropriate questions
- **Option Uniqueness:** No duplicate or banned options
- **Educational Standards:** Factually accurate content

### **⚡ High-Performance Processing**
- **Parallel Generation:** All sections simultaneously
- **Async Architecture:** Non-blocking operations
- **Efficient Database:** Batch operations with duplicate handling
- **Performance Tracking:** Execution time monitoring

### **📝 Flexible Schema System**
```python
class QuestionItem(BaseModel):
    syllabus_id: int
    difficulty: Literal["easy", "medium", "hard"]
    question_text: str = Field(..., min_length=10)
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: Literal["A", "B", "C", "D"]
    solution: str = Field(..., min_length=10)
    is_active: bool = True

class QuestionBatch(BaseModel):
    questions: List[QuestionItem] = Field(..., min_length=1)
    skipped_count: int = 0
```

## 🔄 End-to-End Example

**Input:** Any exam configuration (e.g., "IMO", Grade 6, Level 1)

**Process:**
1. **Exam Lookup:** Find exam_overview_id for IMO Grade 6 Level 1
2. **Sections Found:** Mathematics (15q), Logic (10q), Algebra (12q)
3. **Topics Retrieved:** Quadratic equations, Set theory, Prime numbers, etc.
4. **AI Generation:** 37 unique questions created in parallel
5. **Database Save:** All questions stored with full metadata
6. **Result:** Ready for exam deployment!

**Total Time:** ~15-30 seconds (thanks to parallel processing!)

## 🚨 Robust Error Handling

- **Missing Exam Data:** Clear error messages for invalid exam/grade/level
- **Empty Topics:** Graceful skipping of sections without syllabus data
- **AI Generation Failures:** Returns empty array, doesn't crash pipeline
- **Duplicate Questions:** Automatic detection and logging
- **Database Errors:** Individual question failures are isolated
- **Guardrail Violations:** Invalid questions are filtered out
- **Network Issues:** Retry logic and timeout handling

## 📊 Dependencies

Core requirements in `requirements.txt`:
```
openai>=1.0.0
pydantic>=2.0.0
python-dotenv
sqlalchemy
psycopg2-binary
```

## 🎯 Ideal Use Cases

- **Multi-Exam Support:** IMO, IEO, ICSO, NSO, IHO, etc.
- **Grade Flexibility:** Elementary to High School (any grade)
- **Level Adaptation:** Beginner to Advanced difficulty
- **Batch Generation:** Large-scale question bank creation
- **Educational Content:** School assessments and practice tests
- **Competitive Exams:** Olympiad preparation materials

## 🔧 Configuration Options

### **Custom Exam Support**
Simply update your database with:
- `exam_overview` table: exam, grade, level combinations
- `sections` table: sections per exam with question requirements  
- `syllabus` table: topics and subtopics per section

### **Agent Customization**
Modify `SYSTEM_PROMPT` for different:
- Subject specializations
- Question formats
- Difficulty adjustments
- Language preferences

---

*Built for scalable, reliable, and intelligent question generation across all educational levels* 🚀