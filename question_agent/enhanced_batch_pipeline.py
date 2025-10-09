"""
Enhanced Batch Pipeline with Configuration Support

This version includes:
- Configuration-based processing
- Filtering options
- Resume capability
- Better error handling
- Progress tracking
"""

import os
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from simple_pipeline import run_pipeline
from batch_config import BatchConfig, DEFAULT_CONFIG, TEST_CONFIG, PRODUCTION_CONFIG

# Load environment
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Setup logging
def setup_logging(config: BatchConfig):
    """Setup logging based on configuration"""
    if config.log_to_file:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.log_file_path),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    return logging.getLogger(__name__)

def get_filtered_exam_overviews(config: BatchConfig) -> List[Dict[str, Any]]:
    """Fetch exam overviews with filtering applied"""
    logger = logging.getLogger(__name__)
    logger.info("Fetching exam overviews with filters applied...")
    
    with SessionLocal() as session:
        # Build dynamic query based on filters
        where_conditions = []
        params = {}
        
        if config.exam_filter:
            where_conditions.append("exam = ANY(:exam_filter)")
            params["exam_filter"] = config.exam_filter
        
        if config.grade_filter:
            where_conditions.append("grade = ANY(:grade_filter)")
            params["grade_filter"] = config.grade_filter
        
        if config.level_filter:
            where_conditions.append("level = ANY(:level_filter)")
            params["level_filter"] = config.level_filter
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = text(f"""
            SELECT exam_overview_id, exam, grade, level, total_questions, total_marks, total_time_mins
            FROM exam_overview
            WHERE {where_clause}
            ORDER BY exam, grade, level
        """)
        
        result = session.execute(query, params)
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
    
    logger.info(f"Found {len(exam_overviews)} exam overviews matching filters:")
    for exam in exam_overviews:
        logger.info(f"  - {exam['exam']} Grade {exam['grade']} Level {exam['level']} ({exam['total_questions']} questions)")
    
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

async def process_single_exam_with_retry(exam_info: Dict[str, Any], config: BatchConfig, current: int, total: int) -> Dict[str, Any]:
    """Process a single exam with retry logic"""
    logger = logging.getLogger(__name__)
    exam_overview_id = exam_info["exam_overview_id"]
    exam = exam_info["exam"]
    grade = exam_info["grade"]
    level = exam_info["level"]
    
    logger.info(f"Processing {current}/{total}: {exam} Grade {grade} Level {level}")
    
    # Check if exam already has questions
    existing_count = get_exam_question_count(exam_overview_id)
    if config.skip_existing and existing_count > 0:
        logger.info(f"Skipping {exam} Grade {grade} Level {level} - already has {existing_count} questions")
        return {
            "exam_overview_id": exam_overview_id,
            "exam": exam,
            "grade": grade,
            "level": level,
            "status": "skipped",
            "questions_before": existing_count,
            "questions_after": existing_count,
            "questions_generated": 0,
            "error": None,
            "retries": 0
        }
    
    # Process with retries
    last_error = None
    for attempt in range(config.max_retries + 1):
        try:
            start_time = time.time()
            
            # Run the pipeline for this exam
            await run_pipeline(exam=exam, grade=grade, level=level)
            
            # Get final question count
            final_count = get_exam_question_count(exam_overview_id)
            questions_generated = final_count - existing_count
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Completed {exam} Grade {grade} Level {level}: {questions_generated} questions in {duration:.1f}s")
            
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
                "error": None,
                "retries": attempt
            }
            
        except Exception as e:
            last_error = e
            if attempt < config.max_retries:
                logger.warning(f"⚠️  Attempt {attempt + 1} failed for {exam} Grade {grade} Level {level}: {e}")
                logger.info(f"Retrying in {config.delay_between_exams} seconds...")
                await asyncio.sleep(config.delay_between_exams)
            else:
                logger.error(f"❌ Failed {exam} Grade {grade} Level {level} after {config.max_retries + 1} attempts: {e}")
    
    # All retries failed
    return {
        "exam_overview_id": exam_overview_id,
        "exam": exam,
        "grade": grade,
        "level": level,
        "status": "failed",
        "questions_before": existing_count,
        "questions_after": existing_count,
        "questions_generated": 0,
        "duration_seconds": 0,
        "error": str(last_error),
        "retries": config.max_retries
    }

async def run_enhanced_batch_pipeline(config: BatchConfig = DEFAULT_CONFIG):
    """Run enhanced batch pipeline with configuration"""
    logger = setup_logging(config)
    logger.info("Starting Enhanced Batch Pipeline")
    logger.info("=" * 80)
    
    # Get filtered exam overviews
    exam_overviews = get_filtered_exam_overviews(config)
    
    if not exam_overviews:
        logger.info("No exam overviews found matching the filters!")
        return []
    
    # Apply max_exams limit
    if config.max_exams:
        exam_overviews = exam_overviews[:config.max_exams]
        logger.info(f"Limited to first {config.max_exams} exams")
    
    total_exams = len(exam_overviews)
    logger.info(f"Processing {total_exams} exam overviews...")
    
    # Track results
    results = []
    completed = 0
    skipped = 0
    failed = 0
    total_questions_generated = 0
    total_duration = 0
    
    start_time = time.time()
    
    # Process each exam
    for i, exam_info in enumerate(exam_overviews, 1):
        try:
            result = await process_single_exam_with_retry(exam_info, config, i, total_exams)
            results.append(result)
            
            # Update counters
            if result["status"] == "completed":
                completed += 1
                total_questions_generated += result["questions_generated"]
                total_duration += result.get("duration_seconds", 0)
            elif result["status"] == "skipped":
                skipped += 1
            else:
                failed += 1
                if not config.continue_on_error:
                    logger.error("Stopping batch processing due to error (continue_on_error=False)")
                    break
            
            # Add delay between exams
            if i < total_exams and config.delay_between_exams > 0:
                await asyncio.sleep(config.delay_between_exams)
                
        except Exception as e:
            logger.error(f"Unexpected error processing exam {i}: {e}")
            if not config.continue_on_error:
                break
    
    end_time = time.time()
    total_batch_duration = end_time - start_time
    
    # Print final summary
    logger.info("\n" + "=" * 80)
    logger.info("ENHANCED BATCH PIPELINE COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Total Exams Processed: {total_exams}")
    logger.info(f"  ✅ Completed: {completed}")
    logger.info(f"  ⏭️  Skipped: {skipped}")
    logger.info(f"  ❌ Failed: {failed}")
    logger.info(f"Total Questions Generated: {total_questions_generated}")
    logger.info(f"Total Processing Time: {total_batch_duration:.1f} seconds")
    logger.info(f"Average Time per Exam: {total_batch_duration/total_exams:.1f} seconds")
    logger.info("=" * 80)
    
    # Print detailed results
    if config.verbose:
        logger.info("\nDETAILED RESULTS:")
        logger.info("-" * 80)
        for result in results:
            status_icon = "✅" if result["status"] == "completed" else "⏭️" if result["status"] == "skipped" else "❌"
            retry_info = f" (retries: {result.get('retries', 0)})" if result.get('retries', 0) > 0 else ""
            logger.info(f"{status_icon} {result['exam']} Grade {result['grade']} Level {result['level']}: "
                       f"{result['questions_generated']} questions generated{retry_info}")
            if result["error"]:
                logger.info(f"   Error: {result['error']}")
    
    return results

# Convenience functions for different use cases
async def run_test_batch():
    """Run batch pipeline with test configuration"""
    return await run_enhanced_batch_pipeline(TEST_CONFIG)

async def run_production_batch():
    """Run batch pipeline with production configuration"""
    return await run_enhanced_batch_pipeline(PRODUCTION_CONFIG)

async def run_imo_only_batch():
    """Run batch pipeline for IMO exams only"""
    from batch_config import IMO_ONLY_CONFIG
    return await run_enhanced_batch_pipeline(IMO_ONLY_CONFIG)

async def run_grade_6_only_batch():
    """Run batch pipeline for Grade 6 exams only"""
    from batch_config import GRADE_6_ONLY_CONFIG
    return await run_enhanced_batch_pipeline(GRADE_6_ONLY_CONFIG)

if __name__ == "__main__":
    # Choose your processing mode:
    
    # Mode 1: Test run (3 exams only)
    # asyncio.run(run_test_batch())
    
    # Mode 2: Production run (all exams, skip existing)
    asyncio.run(run_production_batch())
    
    # Mode 3: IMO only
    # asyncio.run(run_imo_only_batch())
    
    # Mode 4: Grade 6 only
    # asyncio.run(run_grade_6_only_batch())
    
    # Mode 5: Custom configuration
    # custom_config = BatchConfig(
    #     exam_filter=["IMO", "IEO"],
    #     grade_filter=[6, 7],
    #     skip_existing=True,
    #     max_exams=10
    # )
    # asyncio.run(run_enhanced_batch_pipeline(custom_config))
