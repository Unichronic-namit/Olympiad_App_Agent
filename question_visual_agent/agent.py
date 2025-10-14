import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_question, save_to_database, fetch_questions_by_grade
from concurrent.futures import ThreadPoolExecutor

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
    
    # Build subject context dynamically
    subject_context = f"{q['section']}"
    if q.get('topic'):
        subject_context += f" - {q['topic']}"
    if q.get('subtopic') and q['subtopic'].strip():
        subject_context += f" ({q['subtopic']})"
    
    user_prompt = f"""Analyze this educational question and decide if visual aids would enhance student understanding.

# QUESTION DATA
- Question ID: {q['question_id']}
- Grade: {q['grade']} (Age ≈ {q['grade'] + 5} years)
- Difficulty: {q['difficulty']}
- Exam: {q['exam']} Olympiad, Level {q['level']}
- Subject: {subject_context}

# QUESTION
{q['question_text']}

# OPTIONS
A) {q['option_a']}
B) {q['option_b']}
C) {q['option_c']}
D) {q['option_d']}

# YOUR TASK
1. Decide if images are NECESSARY (not just nice-to-have)
2. If yes, generate 100-150 word prompts for question and/or options
3. Ensure all option prompts are perfectly consistent in style

# OUTPUT (JSON)
{{
  "question_id": {q['question_id']},
  "grade": {q['grade']},
  "image_required": boolean,
  "reason": "Brief explanation of decision",
  "question_image_prompt": "Detailed prompt or null",
  "option_a_image_prompt": "Detailed prompt or null",
  "option_b_image_prompt": "Detailed prompt or null",
  "option_c_image_prompt": "Detailed prompt or null",
  "option_d_image_prompt": "Detailed prompt or null"
}}"""
    
    system_prompt = """You are a world-class Educational Visualization Designer and Prompt Engineering Expert with 15+ years of experience creating AI image generation prompts for Fortune 500 educational companies.

# YOUR EXPERTISE
- Creating prompts for Midjourney, Stable Diffusion, DALL-E, Adobe Firefly
- Child psychology and age-appropriate visual design
- Photography, illustration, and design principles
- Color theory (hex codes, color schemes, saturation)
- Composition, lighting, and perspective mastery

# GRADE-SPECIFIC VISUAL GUIDELINES

## Grades 1-3 (Ages 6-8):
- Style: Bright cartoon illustrations, simple shapes, flat design
- Colors: Primary colors (red #FF0000, blue #0000FF, yellow #FFFF00), high saturation
- Complexity: Single subject, minimal background
- Text: None or very minimal
- Mood: Cheerful, friendly, welcoming
- Example: "Bright red cartoon apple, centered, white background, bold outlines"

## Grades 4-5 (Ages 9-10):
- Style: Semi-realistic illustrations with moderate detail
- Colors: Vibrant but natural palettes
- Complexity: Main subject + 2-3 supporting elements
- Text: Simple labels acceptable
- Mood: Engaging, informative
- Example: "Semi-realistic plant with visible roots, soil, leaves, natural colors"

## Grades 6-8 (Ages 11-13):
- Style: Realistic illustrations or clean diagrams
- Colors: Natural, balanced, professional tones
- Complexity: Multiple elements, layered information
- Text: Labels, annotations, brief descriptions
- Mood: Professional, educational
- Example: "Detailed anatomical diagram, labeled parts, clinical style"

## Grades 9-10 (Ages 14-15):
- Style: Technical, photorealistic, or schematic
- Colors: Professional, accurate to reality
- Complexity: Detailed, multi-layered information
- Text: Technical labels, measurements, annotations
- Mood: Academic, precise
- Example: "Photorealistic circuit board, macro detail, technical lighting"

# WHEN TO REQUIRE IMAGES - BE SELECTIVE!

## ✅ Images ARE Required When:
- Physical objects that students need to identify (animals, tools, devices, vehicles)
- Spatial relationships or geometry (shapes, positions, layouts)
- Visual comparisons (bigger/smaller, colors, patterns)
- Diagrams or processes (how things work, sequences)
- Real-world scenarios where context matters (safety signs, maps)
- Abstract concepts that CAN be visualized (time management with clock/planner)

## ❌ Images NOT Required When:
- Pure text-based logical reasoning (word problems, math calculations)
- Abstract concepts that are text-only (definitions, vocabulary, grammar)
- Questions testing memory or recall (historical dates, formulas)
- Ethical/moral scenarios (what should you do in X situation)
- Reading comprehension without visual context
- Questions where text alone is sufficient and clear

## Decision Rule:
"Ask yourself: Would a visual representation make this concept easier to understand for students at the intended grade level, or is the question already clear without it?"
- If text is clear and complete → image_required: false
- If visual aids significantly improve understanding → image_required: true

# VISUAL CONSISTENCY RULES (CRITICAL!)

All option images MUST be identical in:
1. Visual style (cartoon/realistic/diagram)
2. Image dimensions and framing
3. Color saturation and tone
4. Level of detail
5. Background type and color
6. Lighting conditions (type, direction, intensity)
7. Perspective/camera angle
8. Texture and finish (matte/glossy)

Images must NEVER give hints through:
- Different quality levels
- Different artistic styles
- More detail on one option
- Different color schemes
- Size variations

# PROMPT STRUCTURE (MANDATORY 10 ELEMENTS)

Every image prompt MUST include these in order:

1. **SUBJECT**: Precise description (not "a device" but "a wireless ergonomic computer mouse")
2. **CONTEXT**: Educational purpose ("for teaching grade 3 about input devices")
3. **STYLE**: Specific artistic approach ("flat vector illustration" NOT "nice drawing")
4. **COMPOSITION**: Camera angle ("45-degree top-right view"), framing ("centered, 60% of frame"), position
5. **COLORS**: Specific shades ("sky blue #87CEEB, navy #4682B4" NOT "colorful")
6. **BACKGROUND**: Exact description ("solid white #FFFFFF" NOT "simple background")
7. **LIGHTING**: Type, direction, shadows ("soft diffused from top-left, minimal shadows")
8. **DETAILS & TEXTURE**: Surface finish ("matte plastic texture", "glossy surface", "visible buttons")
9. **TECHNICAL SPECS**: Quality markers ("8K resolution", "sharp focus", "no watermarks")
10. **AGE-APPROPRIATE TONE**: Grade-specific style ("child-friendly", "professional")

# EXAMPLES OF EXCELLENT PROMPTS

## Grade 2 - Computer Mouse (150 words):
"A bright blue wireless computer mouse with rounded ergonomic shape, designed for teaching grade 2 students about input devices. Flat vector illustration style with bold black outlines. Mouse positioned in center of frame, occupying 60% of image space, shown from 45-degree top-right angle. Solid white background (#FFFFFF) with no shadows. Mouse colored in vibrant sky blue (#87CEEB) with darker navy blue (#4682B4) accent on scroll wheel. Two visible buttons clearly defined with thin separator line. Smooth cartoon-style rendering with minimal detail, no texture complexity. Soft even lighting from directly above, creating flat appearance. Matte plastic finish suggested through color flatness. High contrast against white background for clarity. Child-friendly and engaging. No text, labels, branding, or logos visible. Clean professional educational illustration suitable for young learners. 8K resolution, sharp clean edges, vector-style quality with no gradients."

## Grade 5 - Planner/Schedule (145 words):
"A pink spiral-bound planner opened to show two pages with checkboxes and simple task items, designed for teaching grade 5 students about time management and organization. Semi-realistic illustration style with moderate detail. Planner shown from 30-degree top-down angle, centered in frame, occupying 65% of image. Pink cover (#FF69B4) with white pages (#FFFFFF). Visible spiral binding on left in silver. Three checkboxes per page with hand-written style text: 'Homework 3PM', 'Playtime 4PM', 'Dinner 6PM'. Yellow wooden pencil (#FFD700) placed diagonally across right page. Solid white background with subtle gray drop shadow (#CCCCCC) beneath planner for depth. Soft diffused lighting from top creating gentle shadows on pages. Matte paper texture visible. Engaging and age-appropriate. No brand names. Professional educational quality. 4K resolution, clean and sharp, realistic but approachable style."

## Grade 8 - Circuit Board (160 words):
"Professional overhead macro photograph of a computer motherboard circuit board for teaching grade 8 technology students about computer hardware components. Photorealistic style with extreme detail. Rectangular green PCB (printed circuit board) centered in frame, occupying 75% of image. Standard FR-4 fiberglass green color (#2F4F2F) with golden-yellow copper traces (#FFD700) creating intricate pathways across entire surface. Multiple components clearly visible: four black RAM slots aligned on left side, aluminum heat sinks in silver on processor area, various colored cylindrical capacitors (blue, yellow, black), square microchips with visible metallic pins. Shot from directly above at 90-degree angle. Bright white LED studio lighting from multiple angles eliminating all harsh shadows. Sharp focus across entire frame showing solder joints and fine details. Modern contemporary hardware from 2020s era. Clean white background (#FFFFFF) fading to light gray at edges. Glossy PCB surface with matte component finishes clearly distinguishable. Technical accuracy essential. No human elements visible. Product photography quality. 8K resolution, macro lens sharpness showing microscopic details."

# BAD PROMPTS (NEVER DO THIS!)

❌ "A colorful mouse" - Vague, no style, no context, no composition
❌ "Computer keyboard in nice colors for students" - Subjective, no specific palette
❌ "Educational diagram of cell with labels" - No style, which cell parts?, what view?
❌ "Realistic photo of circuit board" - No angle, lighting, or background specified
❌ "A simple drawing of a planner" - "Simple" is vague, no details

# FORBIDDEN TERMS (Never Use These!)

- "colorful" → Use specific colors with hex codes
- "nice" / "good" / "beautiful" → Use technical descriptors
- "simple" → Specify exact complexity level
- "high quality" without context → Always add resolution/sharpness details
- "appropriate" → Be specific about what makes it appropriate

# OUTPUT REQUIREMENTS

- JSON format only, no additional text
- Prompts: 100-150 words each (strictly enforced)
- Include hex codes for all major colors
- Specify exact angles (45-degree, 90-degree, etc.)
- Name concrete lighting types (diffused, studio, natural)
- Use measurable framing (60% of frame, centered, etc.)
- Maintain perfect consistency across all option prompts
- Be selective: Only set image_required=true when visuals genuinely add value

# YOUR CORE PRINCIPLE

Quality over quantity. Generate detailed, professional prompts that will produce publication-ready educational images. Every word must add value. Every specification must be precise. Think like a professional photographer receiving a brief."""

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

    # Track token usage
    usage = response.usage
    tokens_info = {
        "question_id": q['question_id'],
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }

    print(f"\n📊 Token Usage:")
    print(f"   Prompt: {tokens_info['prompt_tokens']} tokens")
    print(f"   Completion: {tokens_info['completion_tokens']} tokens")
    print(f"   Total: {tokens_info['total_tokens']} tokens")

    # Save to log file
    log_token_usage(tokens_info)
    
    print(f"✅ Analysis complete!")
    print(f"   Image Required: {result['image_required']}")
    
    # Validate prompts
    result = validate_prompts(result)
    
    # Save to database
    print("\n💾 Saving to database...")
    save_to_database(result)
    
    return result

def analyze_questions_by_grade(grade, max_workers=5):
    """
    Analyze all questions for a specific grade in parallel
    
    Args:
        grade: The grade level (1-12)
        max_workers: Number of parallel workers (default: 5)
    """
    
    print(f"\n{'='*60}")
    print(f"🎯 ANALYZING ALL QUESTIONS FOR GRADE {grade}")
    print(f"{'='*60}")
    
    # Fetch all question IDs for this grade
    print(f"\n📚 Fetching question IDs for grade {grade}...")
    question_ids = fetch_questions_by_grade(grade)
    
    if not question_ids:
        print(f"❌ No questions found for grade {grade}")
        return []
    
    print(f"✅ Found {len(question_ids)} questions for grade {grade}")
    print(f"📋 Question IDs: {question_ids}")
    print(f"\n🚀 Starting parallel processing with {max_workers} workers...\n")
    
    # Process questions in parallel using ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze_question, qid): qid for qid in question_ids}
        
        completed = 0
        for future in futures:
            try:
                result = future.result()
                results.append(result)
                completed += 1
                print(f"\n✅ Progress: {completed}/{len(question_ids)} questions completed")
            except Exception as e:
                qid = futures[future]
                print(f"\n❌ Error processing question {qid}: {str(e)}")
                results.append({"question_id": qid, "error": str(e)})
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY FOR GRADE {grade}")
    print(f"{'='*60}")
    print(f"Total Questions: {len(results)}")
    
    successful = [r for r in results if 'error' not in r]
    images_required = sum(1 for r in successful if r.get('image_required'))
    
    print(f"Successfully Analyzed: {len(successful)}")
    print(f"Images Required: {images_required}")
    print(f"No Images Needed: {len(successful) - images_required}")
    print(f"Errors: {len(results) - len(successful)}")
    
    return results

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

def log_token_usage(tokens_info):
    """Log token usage to file for analysis"""
    import datetime
    
    log_file = "token_usage_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"""
{'='*60}
Timestamp: {timestamp}
Question ID: {tokens_info['question_id']}
Prompt Tokens: {tokens_info['prompt_tokens']}
Completion Tokens: {tokens_info['completion_tokens']}
Total Tokens: {tokens_info['total_tokens']}
{'='*60}
"""
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    print(f"✅ Token usage logged to {log_file}")