"""
Olympiad Question Generator Pipeline

🔹 What We Are Doing:
Building a pipeline that automatically creates Olympiad questions for given exam,grade and level.
Questions come from syllabus topics and get stored in the questions table.

🔹 Steps:
1. Get exam & section info
2. Get topics from syllabus
3. Ask Agents to generate questions (parallel for all sections)
4. Save questions in database
5. Done!
"""

import os
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from agent_definition import generate_questions_with_agent

# Load environment
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_exam_sections(exam_overview_id: int) -> List[Dict[str, Any]]:
    """Get Exam & Section Info"""
    print("Getting exam sections...")

    with SessionLocal() as session:
        query = text("""
            SELECT s.section_id, s.section, s.no_of_questions, s.marks_per_question
            FROM sections s
            WHERE s.exam_overview_id = :exam_id
            ORDER BY s.section_id
        """)
        result = session.execute(query, {"exam_id": exam_overview_id})
        sections = []

        for row in result:
            sections.append({
                "section_id": row.section_id,
                "section_name": row.section,
                "questions_needed": row.no_of_questions,
                "marks_per_question": row.marks_per_question
            })

        print(f"Found {len(sections)} sections:")
        for section in sections:
            print(f"  - {section['section_name']}")

        return sections

def get_section_topics(exam_overview_id: int, section_id: int) -> List[Dict[str, Any]]:
    """Get Topics from Syllabus"""
    with SessionLocal() as session:

        # Get topics for this section
        query = text("""
            SELECT syllabus_id, topic, subtopic
            FROM syllabus
            WHERE exam_overview_id = :exam_id AND section_id = :section_id
            ORDER BY syllabus_id
        """)
        result = session.execute(query, {"exam_id": exam_overview_id, "section_id": section_id})
        topics = []

        for row in result:
            topics.append({
                "syllabus_id": row.syllabus_id,
                "topic": row.topic,
                "subtopic": row.subtopic or ""
            })

        return topics

async def generate_questions_for_section(section_info: Dict[str, Any], topics: List[Dict[str, Any]], exam: str, grade: int, level: int) -> Dict[str, Any]:
    """Ask to Generate Questions using OpenAI Agent with Guardrails"""
    return await generate_questions_with_agent(section_info, topics, exam, grade, level)

def save_questions_to_db(questions: List[Dict[str, Any]], section_name: str) -> int:
    """Save Questions in Database"""
    if not questions:
        return 0

    saved_count = 0
    with SessionLocal() as session:
        for q in questions:
            try:
                # Check for duplicates
                check_query = text("""
                    SELECT question_id FROM questions
                    WHERE LOWER(question_text) = LOWER(:question_text)
                """)
                existing_rows = session.execute(check_query, {"question_text": q["question_text"]}).fetchall()
                if existing_rows:
                    existing_ids = [row[0] for row in existing_rows]
                    print(f"NOTICE: Duplicate detected. Existing question_ids: {existing_ids}")

                # Insert new question
                insert_query = text("""
                    INSERT INTO questions (
                        syllabus_id, difficulty, question_text,
                        option_a, option_b, option_c, option_d,
                        correct_option, solution, is_active,
                        created_at, updated_at
                    ) VALUES (
                        :syllabus_id, :difficulty, :question_text,
                        :option_a, :option_b, :option_c, :option_d,
                        :correct_option, :solution, :is_active,
                        NOW(), NOW()
                    )
                    RETURNING question_id
                """)

                result = session.execute(insert_query, {
                    "syllabus_id": q["syllabus_id"],
                    "difficulty": q["difficulty"],
                    "question_text": q["question_text"],
                    "option_a": q["option_a"],
                    "option_b": q["option_b"],
                    "option_c": q["option_c"],
                    "option_d": q["option_d"],
                    "correct_option": q["correct_option"],
                    "solution": q["solution"],
                    "is_active": q.get("is_active", True)
                })
                saved_count += 1

                new_question_id = result.scalar()
                # Only print inserted ID if duplicates exist
                if existing_rows:
                    print(f"Duplicate detected. New inserted question_id: {new_question_id}")

            except Exception as e:
                print(f"ERROR: Error saving question: {e}")
                continue

        session.commit()
        print(f"SAVED: {section_name}: {saved_count} questions saved")

    return saved_count

def fetch_exam_overview_id(exam: str, grade: int, level: int) -> int:
    """Fetch exam_overview_id from database based on exam, grade, and level"""
    with SessionLocal() as session:
        query = text("""
            SELECT exam_overview_id
            FROM exam_overview
            WHERE LOWER(exam) = LOWER(:exam)
              AND grade = :grade
              AND level = :level
            LIMIT 1
        """)
        result = session.execute(query, {"exam": exam, "grade": grade, "level": level})
        exam_overview_id = result.scalar()

        if not exam_overview_id:
            raise ValueError(f"No exam found for {exam} Grade {grade} Level {level}")

        return exam_overview_id

async def run_pipeline(exam: str, grade: int, level: int):
    """Main Pipeline - Run all steps"""
    print("Starting Olympiad Question Generator Pipeline")
    print("=" * 60)

    # Fetch exam_overview_id
    exam_overview_id = fetch_exam_overview_id(exam=exam, grade=grade, level=level)

    # Get Exam & Section Info
    sections = get_exam_sections(exam_overview_id=exam_overview_id)

    if not sections:
        print("ERROR: No sections found for exam_overview_id:", exam_overview_id)
        return

    # Get topics for each section
    print("\nGetting topics for each section...")
    section_data = []

    for section in sections:
        topics = get_section_topics(exam_overview_id=exam_overview_id, section_id=section["section_id"])
        print(f"  - {section['section_name']}: {len(topics)} topics found")

        if topics:
            section_data.append((section, topics))
        else:
            print(f"  WARNING: Skipping {section['section_name']} - no topics found")

    # Generate questions for all sections (parallel)
    print(f"\nGenerating questions for {len(section_data)} sections in parallel...")

    # Create all tasks and section names in parallel
    tasks = [generate_questions_for_section(section_info, topics, exam, grade, level) for section_info, topics in section_data]
    section_names = [section_info["section_name"] for section_info,topics in section_data]

    # Run all tasks in parallel
    results = await asyncio.gather(*tasks)

    # Save all questions
    print(f"\nSaving questions to database...")
    total_saved = 0

    for i, (section_name, result) in enumerate(zip(section_names, results)):
        questions = result.get("questions", [])
        saved = save_questions_to_db(questions, section_name)
        total_saved += saved

    #Summary
    print("\n" + "=" * 60)
    print("Pipeline Complete!")
    print(f"Total questions saved: {total_saved}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_pipeline(exam="IGKO", grade=6, level=1))