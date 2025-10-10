import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_question, save_to_database

load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_question(question_id):
    """Main function - analyze if question needs images"""
    
    # Get question from database
    q = fetch_question(question_id)
    
    if not q:
        return {"error": "Question not found"}
    
    print(f"\n🔍 Analyzing Question {question_id}...")
    print(f"   Grade: {q['grade']}, Difficulty: {q['difficulty']}")
    
    # Prepare prompt
    prompt = f"""You are an Educational Visualization Expert.

Analyze the question and decide if visual representation helps based on grade, difficulty, and concept type.

Rules:
- Grades 1–5 → visuals almost always helpful
- Grades 6–8 → visuals for spatial or real-world items
- Grades 9–10 → visuals only for diagrams, graphs, or complex models
- Never create decorative or irrelevant visuals.

Additional Guidelines:
- Visuals may be added for the question text, for all options, or for both — depending on where they help most.
- Never provide an image for only one or a few options unless it is absolutely necessary (for example, if the question itself asks about identifying a visual concept like shapes or animals).
- If visuals are helpful for the options, ensure that **all options** have images of similar style and detail to maintain fairness and avoid giving answer hints.
- Avoid giving an unfair hint: if only one option has a distinctive image, it might reveal the correct answer.
  In such cases, either:
  - provide images for all options (if they can be represented visually), or
  - avoid adding any option-specific visuals at all.
- Ensure visuals are conceptually neutral and do not indicate correctness in any way.
- Do NOT generate unnecessary visuals. If text is already self-explanatory, keep all image prompts as null.
- The goal is to enhance understanding, not to decorate. Only include images that genuinely help the student grasp the concept better.

Question:
question_id: {q['question_id']}
Grade: {q['grade']}
Difficulty: {q['difficulty']}
Text: {q['question_text']}
A: {q['option_a']}
B: {q['option_b']}
C: {q['option_c']}
D: {q['option_d']}

Return output in strict JSON with:
- question_id
- grade
- image_required (true/false)
- reason
- question_image_prompt (or null)
- option_a_image_prompt (or null)
- option_b_image_prompt (or null)
- option_c_image_prompt (or null)
- option_d_image_prompt (or null)"""

    # Call OpenAI
    print("🤖 Calling OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    print(f"✅ Analysis complete!")
    print(f"   Image Required: {result['image_required']}")
    
    # Save to database
    print("\n💾 Saving to database...")
    save_to_database(result)
    
    return result