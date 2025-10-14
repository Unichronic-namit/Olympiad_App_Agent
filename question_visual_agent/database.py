import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )

def fetch_question(question_id):
    """Fetch question with grade, subject, and topic"""
    conn = get_db()
    cur = conn.cursor()
    
    query = """
    SELECT q.question_id, q.question_text, q.option_a, q.option_b, 
           q.option_c, q.option_d, q.difficulty, 
           e.grade, e.exam, e.level,
           sec.section,
           s.topic, s.subtopic
    FROM questions q
    JOIN syllabus s ON q.syllabus_id = s.syllabus_id
    JOIN sections sec ON s.section_id = sec.section_id
    JOIN exam_overview e ON s.exam_overview_id = e.exam_overview_id
    WHERE q.question_id = %s;
    """
    
    cur.execute(query, (question_id,))
    question = cur.fetchone()
    
    conn.close()
    return question

def fetch_questions_by_grade(grade):
    """Fetch all question IDs for a specific grade"""
    conn = get_db()
    cur = conn.cursor()
    
    query = """
    SELECT DISTINCT q.question_id
    FROM questions q
    JOIN syllabus s ON q.syllabus_id = s.syllabus_id
    JOIN exam_overview e ON s.exam_overview_id = e.exam_overview_id
    WHERE e.grade = %s AND q.is_active = TRUE
    ORDER BY q.question_id;
    """
    
    cur.execute(query, (grade,))
    question_ids = [row['question_id'] for row in cur.fetchall()]
    
    conn.close()
    return question_ids

def save_to_database(result):
    """Save analysis result to database"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        query = """
        INSERT INTO question_visual_prompts 
        (question_id, image_required, reason, question_image_prompt, 
         option_a_image_prompt, option_b_image_prompt, 
         option_c_image_prompt, option_d_image_prompt)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        cur.execute(query, (
            result['question_id'],
            result['image_required'],
            result['reason'],
            result.get('question_image_prompt'),
            result.get('option_a_image_prompt'),
            result.get('option_b_image_prompt'),
            result.get('option_c_image_prompt'),
            result.get('option_d_image_prompt')
        ))
        
        record_id = cur.fetchone()['id']
        conn.commit()
        
        print(f"✅ Saved to database with ID: {record_id}")
        return record_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Database error: {str(e)}")
        return None
    finally:
        conn.close()