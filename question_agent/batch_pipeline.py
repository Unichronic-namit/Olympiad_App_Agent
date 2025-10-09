"""
Automated Batch Pipeline for All Exam Overviews

🔹 What We Are Doing:
Automatically processes ALL exam overviews from the database and runs the question generation pipeline for each one.

🔹 Features:
- Fetches all exam overviews from database
- Processes each exam overview sequentially
- Progress tracking and logging
- Error recovery and resume capability
- Summary reporting
"""

import os
import asyncio
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from simple_pipeline import run_pipeline

# Load environment
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_all_exam_overviews() -> List[Dict[str, Any]]:
    """Fetch all exam overviews from database"""
    print("Fetching all exam overviews from database...")
    
    with SessionLocal() as session:
        query = text("""
            SELECT exam_overview_id, exam, grade, level, total_questions, total_marks, total_time_mins
            FROM exam_overview
            ORDER BY exam, grade, level
        """)
        result = session.execute(query)
        exam_overviews = []
        
        for row in result:
            exam_overviews.append({
                "exam_overview_id": row.exam_overview_id,
                "exam": row.exam,
                "grade": row.grade,
                "level": row.level,
                "total_questions": row.total_questions,
                "total_marks": row.total_marks,
                "total_time_mins": row.total_time_mins
            })
    
    print(f"Found {len(exam_overviews)} exam overviews to process:")
    for exam in exam_overviews:
        print(f"  - {exam['exam']} Grade {exam['grade']} Level {exam['level']} ({exam['total_questions']} questions)")
    
    return exam_overviews

def check_exam_has_questions(exam_overview_id: int) -> bool:
    """Check if exam already has questions generated"""
    with SessionLocal() as session:
        query = text("""
            SELECT COUNT(*) as question_count
            FROM questions q
            JOIN syllabus s ON q.syllabus_id = s.syllabus_id
            WHERE s.exam_overview_id = :exam_id
        """)
        result = session.execute(query, {"exam_id": exam_overview_id})
        count = result.scalar()
        return count > 0

def get_exam_question_count(exam_overview_id: int) -> int:
    """Get current question count for an exam"""
    with SessionLocal() as session:
        query = text("""
            SELECT COUNT(*) as question_count
            FROM questions q
            JOIN syllabus s ON q.syllabus_id = s.syllabus_id
            WHERE s.exam_overview_id = :exam_id
        """)
        result = session.execute(query, {"exam_id": exam_overview_id})
        return result.scalar()

def log_batch_progress(current: int, total: int, exam_info: Dict[str, Any], status: str, details: str = ""):
    """Log progress for batch processing"""
    progress_percent = (current / total) * 100
    print(f"\n{'='*80}")
    print(f"BATCH PROGRESS: {current}/{total} ({progress_percent:.1f}%)")
    print(f"Current Exam: {exam_info['exam']} Grade {exam_info['grade']} Level {exam_info['level']}")
    print(f"Status: {status}")
    if details:
        print(f"Details: {details}")
    print(f"{'='*80}\n")

async def process_single_exam(exam_info: Dict[str, Any], current: int, total: int) -> Dict[str, Any]:
    """Process a single exam overview"""
    exam_overview_id = exam_info["exam_overview_id"]
    exam = exam_info["exam"]
    grade = exam_info["grade"]
    level = exam_info["level"]
    
    log_batch_progress(current, total, exam_info, "STARTING")
    
    # Check if exam already has questions
    existing_count = get_exam_question_count(exam_overview_id)
    if existing_count > 0:
        log_batch_progress(current, total, exam_info, "SKIPPED", f"Already has {existing_count} questions")
        return {
            "exam_overview_id": exam_overview_id,
            "exam": exam,
            "grade": grade,
            "level": level,
            "status": "skipped",
            "questions_before": existing_count,
            "questions_after": existing_count,
            "questions_generated": 0,
            "error": None
        }
    
    start_time = time.time()
    
    try:
        # Run the pipeline for this exam
        await run_pipeline(exam=exam, grade=grade, level=level)
        
        # Get final question count
        final_count = get_exam_question_count(exam_overview_id)
        questions_generated = final_count - existing_count
        
        end_time = time.time()
        duration = end_time - start_time
        
        log_batch_progress(current, total, exam_info, "COMPLETED", 
                          f"Generated {questions_generated} questions in {duration:.1f}s")
        
        return {
            "exam_overview_id": exam_overview_id,
            "exam": exam,
            "grade": grade,
            "level": level,
            "status": "completed",
            "questions_before": existing_count,
            "questions_after": final_count,
            "questions_generated": questions_generated,
            "duration_seconds": duration,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        log_batch_progress(current, total, exam_info, "FAILED", f"Error: {str(e)}")
        
        return {
            "exam_overview_id": exam_overview_id,
            "exam": exam,
            "grade": grade,
            "level": level,
            "status": "failed",
            "questions_before": existing_count,
            "questions_after": existing_count,
            "questions_generated": 0,
            "duration_seconds": duration,
            "error": str(e)
        }

async def run_batch_pipeline(skip_existing: bool = False, max_exams: Optional[int] = None):
    """Run pipeline for all exam overviews"""
    print("Starting Automated Batch Pipeline for All Exam Overviews")
    print("=" * 80)
    
    # Get all exam overviews
    exam_overviews = get_all_exam_overviews()
    
    if not exam_overviews:
        print("No exam overviews found in database!")
        return
    
    # Limit number of exams if specified
    if max_exams:
        exam_overviews = exam_overviews[:max_exams]
        print(f"Limited to first {max_exams} exams")
    
    total_exams = len(exam_overviews)
    print(f"\nProcessing {total_exams} exam overviews...")
    
    # Track results
    results = []
    completed = 0
    skipped = 0
    failed = 0
    total_questions_generated = 0
    
    # Process each exam sequentially (to avoid overwhelming the API)
    for i, exam_info in enumerate(exam_overviews, 1):
        result = await process_single_exam(exam_info, i, total_exams)
        results.append(result)
        
        # Update counters
        if result["status"] == "completed":
            completed += 1
            total_questions_generated += result["questions_generated"]
        elif result["status"] == "skipped":
            skipped += 1
        else:
            failed += 1
    
    # Print final summary
    print("\n" + "=" * 80)
    print("BATCH PIPELINE COMPLETE!")
    print("=" * 80)
    print(f"Total Exams Processed: {total_exams}")
    print(f"  ✅ Completed: {completed}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"Total Questions Generated: {total_questions_generated}")
    print("=" * 80)
    
    # Print detailed results
    print("\nDETAILED RESULTS:")
    print("-" * 80)
    for result in results:
        status_icon = "✅" if result["status"] == "completed" else "⏭️" if result["status"] == "skipped" else "❌"
        print(f"{status_icon} {result['exam']} Grade {result['grade']} Level {result['level']}: "
              f"{result['questions_generated']} questions generated")
        if result["error"]:
            print(f"   Error: {result['error']}")
    
    return results

async def run_batch_pipeline_with_resume():
    """Run batch pipeline with resume capability"""
    print("Starting Batch Pipeline with Resume Capability")
    print("=" * 80)
    
    # Get all exam overviews
    exam_overviews = get_all_exam_overviews()
    
    if not exam_overviews:
        print("No exam overviews found in database!")
        return
    
    # Filter out exams that already have questions
    remaining_exams = []
    for exam in exam_overviews:
        if not check_exam_has_questions(exam["exam_overview_id"]):
            remaining_exams.append(exam)
        else:
            count = get_exam_question_count(exam["exam_overview_id"])
            print(f"⏭️  Skipping {exam['exam']} Grade {exam['grade']} Level {exam['level']} - already has {count} questions")
    
    if not remaining_exams:
        print("All exams already have questions generated!")
        return
    
    print(f"\nFound {len(remaining_exams)} exams that need question generation")
    
    # Process remaining exams
    await run_batch_pipeline(skip_existing=False, max_exams=len(remaining_exams))

if __name__ == "__main__":
    # Choose your processing mode:
    
    # Mode 1: Process all exams (including those with existing questions)
    # asyncio.run(run_batch_pipeline(skip_existing=False))
    
    # Mode 2: Process all exams (including those with existing questions)
    asyncio.run(run_batch_pipeline(skip_existing=False))
    
    # Mode 3: Process limited number of exams for testing
    # asyncio.run(run_batch_pipeline(skip_existing=True, max_exams=3))
