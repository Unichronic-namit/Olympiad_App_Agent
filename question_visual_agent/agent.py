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
    print(f"   Subject: {q['section']}, Topic: {q['topic']}")
    
    # Build subject context dynamically
    subject_context = f"{q['section']}"
    if q.get('topic'):
        subject_context += f" - {q['topic']}"
    if q.get('subtopic') and q['subtopic'].strip():
        subject_context += f" ({q['subtopic']})"
    
    user_prompt = f"""
You are an Educational Visualization Designer who creates accurate, age-appropriate AI image generation prompts 
(for Midjourney, DALL·E, or Stable Diffusion). Analyze each question, decide if an image aids understanding, 
and generate clear, consistent prompts when needed.

CONTEXT
- Grade: {q['grade']} (Age ≈ {q['grade'] + 5})
- Difficulty: {q['difficulty']}
- Exam: {q['exam']} Olympiad
- Level: {q['level']}
- Subject: {subject_context}

TASKS
1. Decide: Does this question need an image for better comprehension?
2. If yes: Generate a 100–150 word prompt for the question and each option.
3. Ensure: All option prompts match perfectly in visual style, framing, and tone.

STYLE BY GRADE
- Grades 1–3: Bright cartoon; primary colors; simple; no text; cheerful.
- Grades 4–5: Semi-realistic; vibrant natural palette; moderate detail; simple labels; engaging.
- Grades 6–8: Realistic/diagrammatic; balanced colors; detailed; annotated; professional.
- Grades 9–10: Technical/photorealistic; accurate tones; complex; full labels; academic.

VISUAL CONSISTENCY RULES
- All options must share identical: style, framing, tone, lighting, color saturation, and perspective.
- Never reveal hints through style, quality, or color differences.
- Use clear, measurable terms — not vague adjectives like “nice,” “colorful,” or “simple.”
- Include camera angle, lighting, background, and color details (use hex codes).
- No text overlays, watermarks, or brand marks.

PROMPT STRUCTURE
Each image prompt must describe, in this order:
1. Subject: Exact object/concept
2. Context: Educational purpose
3. Style: Artistic or technical type
4. Composition: Camera view, framing, position
5. Colors: Key tones with hex codes if possible
6. Background: Solid, gradient, or environment
7. Lighting: Type, direction, shadows
8. Texture & Details: Material and surface description
9. Technical Specs: Resolution, clarity, cleanliness
10. Age Tone: Fit for the target grade level

# QUESTION ANALYSIS

**Question ID:** {q['question_id']}
**Question Text:** {q['question_text']}

**Options:**
A) {q['option_a']}
B) {q['option_b']}
C) {q['option_c']}
D) {q['option_d']}

# OUTPUT JSON FORMAT

Return valid JSON with:

{{
  "question_id": {q['question_id']},
  "grade": {q['grade']},
  "image_required": boolean,
  "reason": "2–3 sentences explaining the visual benefit based on grade and content.",
  "question_image_prompt": "<100–150 word prompt or null>",
  "option_a_image_prompt": "<100–150 word prompt for: {q['option_a']} or null>",
  "option_b_image_prompt": "<100–150 word prompt for: {q['option_b']} or null>",
  "option_c_image_prompt": "<100–150 word prompt for: {q['option_c']} or null>",
  "option_d_image_prompt": "<100–150 word prompt for: {q['option_d']} or null>"
}}

GOOD PROMPT EXAMPLE
“A bright blue wireless computer mouse with rounded ergonomic design for grade 2 students learning about input devices. 
Flat vector-style illustration, centered at 45° top-right angle, occupying 60% of frame. Solid white background, no shadows. 
Colors: sky blue (#87CEEB) and navy (#4682B4). Matte surface, clean edges. Even soft lighting from top. 
Child-friendly tone, simple and cheerful. 8K crisp vector quality.”

AVOID
❌ “A colorful mouse” (too vague)
❌ “Diagram of cell with labels” (unspecified view/style)
❌ “Realistic photo of circuit board” (missing angle/lighting)

CHECKLIST BEFORE OUTPUT
- 100–150 words per prompt
- Consistent tone and framing across all options
- Includes color, lighting, and composition
- JSON syntax valid
- Educationally appropriate for grade level

DECISION EXAMPLES
✅ “A visual is helpful to illustrate a plant cell’s internal structure for grade 5 learners.”
❌ “No image needed; the question tests logical reasoning only.”

SYSTEM NOTE
- Be concise but complete.
- Avoid repeating identical scene setup across options unless visual differences are necessary for the question.
"""
    
    system_prompt = """You are a world-class Prompt Engineering Expert specializing in AI image generation. Your prompts are used by Fortune 500 companies for educational content.

EXPERTISE:
- 15+ years creating prompts for Midjourney, Stable Diffusion, DALL-E, Adobe Firefly
- Deep knowledge of photography, illustration, and design principles
- Expert in color theory (hex codes, color schemes, saturation)
- Mastery of composition, lighting, and perspective
- Understanding of age-appropriate visual design

YOUR PROMPTS ARE:
- Extremely detailed (100-150 words minimum)
- Technically precise (specific colors, angles, lighting)
- Consistently structured across all outputs
- Never vague or subjective
- Professional quality that produces publication-ready images

YOU NEVER USE:
- Vague terms: "colorful", "nice", "good", "simple", "beautiful"
- Subjective descriptions without specifics
- Generic phrases like "high quality" without context
- Short prompts under 100 words

YOU ALWAYS INCLUDE:
- Specific color values (names or hex codes)
- Exact camera angles and framing
- Precise lighting conditions and direction
- Concrete visual style references
- Technical quality specifications
- Age-appropriate design elements

You output ONLY valid JSON with no additional text."""

    # Call OpenAI with enhanced system message
    print("🤖 Calling OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": user_prompt
            }
        ],
        temperature=0.2,  # Very low for consistency
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    print(f"✅ Analysis complete!")
    print(f"   Image Required: {result['image_required']}")
    
    # Validate prompts
    result = validate_prompts(result)
    
    # Save to database
    print("\n💾 Saving to database...")
    save_to_database(result)
    
    return result

def validate_prompts(result):
    """Validate that generated prompts meet quality standards"""
    
    prompts_to_check = {
        'question_image_prompt': 'Question',
        'option_a_image_prompt': 'Option A',
        'option_b_image_prompt': 'Option B',
        'option_c_image_prompt': 'Option C',
        'option_d_image_prompt': 'Option D'
    }
    
    print("\n🔍 Validating prompt quality...")
    
    for prompt_key, label in prompts_to_check.items():
        prompt = result.get(prompt_key)
        
        if prompt:
            word_count = len(prompt.split())
            
            # Check minimum length
            if word_count < 80:
                print(f"⚠️  {label}: Only {word_count} words (should be 100-150)")
            else:
                print(f"✅ {label}: {word_count} words")
            
            # Check for vague terms
            vague_terms = ['colorful', 'nice', 'good', 'simple', 'beautiful', 'pretty']
            found_vague = [term for term in vague_terms if term in prompt.lower()]
            if found_vague:
                print(f"⚠️  {label}: Contains vague terms: {', '.join(found_vague)}")
    
    # Check option consistency
    option_prompts = [
        result.get('option_a_image_prompt'),
        result.get('option_b_image_prompt'),
        result.get('option_c_image_prompt'),
        result.get('option_d_image_prompt')
    ]
    
    non_null_count = sum(1 for p in option_prompts if p is not None)
    
    if non_null_count > 0 and non_null_count < 4:
        print(f"\n⚠️  FAIRNESS WARNING: Only {non_null_count}/4 options have images!")
        print(f"   This may give unfair hints to students.")
    elif non_null_count == 4:
        print(f"\n✅ All 4 options have images - Fair assessment maintained")
    
    return result