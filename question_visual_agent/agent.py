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
    
    # Enhanced prompt with detailed instructions
    prompt = f"""You are an expert Educational Content Visualization Specialist with expertise in child psychology, visual learning, and educational design. Your task is to analyze whether visual aids will enhance student learning for a specific question.

# CONTEXT
- Student Grade Level: {q['grade']} (Age: {q['grade'] + 5} years approximately)
- Difficulty Level: {q['difficulty']}
- Exam: {q['exam']}
- Subject/Section: {subject_context}

# YOUR TASK
Analyze if this question needs visual representation and create detailed DALL-E image generation prompts.

# ANALYSIS CRITERIA

## Grade-Specific Guidelines:
**Grades 1-3 (Ages 6-8):**
- Concrete thinkers - need simple, colorful, real-world visuals
- Use cartoon/illustration style
- Bright colors, clear shapes, minimal text
- Focus on familiar objects and concepts

**Grades 4-5 (Ages 9-10):**
- Transitioning to abstract thinking
- Semi-realistic illustrations work well
- Can handle simple diagrams with labels
- Benefit from step-by-step visual explanations

**Grades 6-8 (Ages 11-13):**
- Can process complex information
- Realistic images or detailed diagrams
- Spatial concepts, technical drawings helpful
- Graphs, charts, and infographics useful

**Grades 9-10 (Ages 14-15):**
- Abstract thinkers
- Only need visuals for:
  * Complex scientific diagrams
  * Mathematical graphs
  * Technical schematics
  * Architectural/engineering concepts
- Most text-based questions don't need images

## Content Type Analysis:
- **Physical Objects**: Always benefit from images (animals, tools, devices, buildings)
- **Abstract Concepts**: Rarely need images unless they can be represented symbolically
- **Spatial Relationships**: Always benefit from diagrams
- **Processes/Sequences**: Benefit from step-by-step illustrations
- **Comparisons**: Side-by-side visuals helpful
- **Identification Tasks**: Essential to have images

## Fairness Rules (CRITICAL):
1. If ANY option needs an image, ALL options MUST have images
2. All option images must use the SAME visual style (illustration/photo/diagram)
3. All option images must have the SAME level of detail
4. Images must NOT reveal the correct answer through:
   - Different quality levels
   - Different artistic styles
   - Different color schemes
   - Different levels of realism
5. Keep all images conceptually neutral

# QUESTION TO ANALYZE

**Question ID:** {q['question_id']}
**Question Text:** {q['question_text']}

**Options:**
A) {q['option_a']}
B) {q['option_b']}
C) {q['option_c']}
D) {q['option_d']}

# OUTPUT REQUIREMENTS

Provide a JSON response with these exact fields:

1. **question_id** (integer): {q['question_id']}
2. **grade** (integer): {q['grade']}
3. **image_required** (boolean): true if images will enhance learning, false otherwise
4. **reason** (string): 
   - 2-3 sentences explaining your decision
   - Reference the grade level, subject, and content type
   - Explain educational benefit or why images aren't needed

5. **question_image_prompt** (string or null):
   - If needed, create a DETAILED DALL-E prompt (50-100 words)
   - Specify: style, colors, perspective, composition, mood, lighting
   - Include age-appropriate elements
   - Consider the subject context: {subject_context}
   - Example: "Educational illustration for grade {q['grade']} students showing [subject] in [style], [colors], [perspective], with [specific details], [lighting], [mood], high quality, clear details"

6. **option_a_image_prompt** (string or null):
   - Follow same structure as question_image_prompt
   - Ensure consistency with other options if this is populated
   - Must relate to: {q['option_a']}
   
7. **option_b_image_prompt** (string or null):
   - Must relate to: {q['option_b']}
   
8. **option_c_image_prompt** (string or null):
   - Must relate to: {q['option_c']}
   
9. **option_d_image_prompt** (string or null):
   - Must relate to: {q['option_d']}

# PROMPT ENGINEERING GUIDELINES FOR IMAGE GENERATION

When creating DALL-E prompts, include:

**Required Elements:**
1. **Subject**: What is the main focus? (Consider: {subject_context})
2. **Style**: cartoon, illustration, realistic photo, diagram, infographic, sketch
3. **Age-appropriateness**: "for grade {q['grade']} students", "child-friendly", "educational"
4. **Colors**: "bright colors", "pastel tones", "natural colors", "high contrast"
5. **Perspective**: "front view", "side view", "isometric", "top-down"
6. **Background**: "white background", "simple background", "educational setting"
7. **Detail level**: "simple and clear", "detailed with labels", "minimalist"
8. **Composition**: "centered", "with space around", "close-up"
9. **Quality markers**: "high quality", "sharp focus", "professional", "clear details"

**Example Good Prompts:**

For Grade 2 (Shape identification):
"Colorful educational illustration of a bright red triangle for grade 2 students, simple geometric shape with clean edges, solid color fill, centered on white background, child-friendly cartoon style, high contrast, clear and bold outline, professional educational material quality"

For Grade 5 (Computer parts):
"Semi-realistic educational illustration of a computer keyboard for grade 5 students, showing full keyboard layout with visible keys, modern design, neutral gray and black colors, front-facing perspective, simple white background, clear and detailed, professional textbook quality, well-lit, sharp focus"

For Grade 8 (Scientific concept):
"Detailed technical diagram of a computer circuit board for grade 8 students, realistic style showing electronic components, green PCB with gold circuits, isometric view, educational infographic style, labeled components, professional quality, clear details, technical illustration"

**Bad Prompts to Avoid:**
- "a triangle" (too vague)
- "keyboard" (no context or style)
- "computer thing" (unclear subject)
- "nice picture of mouse" (unprofessional, vague)

# IMPORTANT REMINDERS
- Generate images ONLY when they genuinely enhance understanding
- Maintain visual consistency across all options
- Age-appropriate complexity and style
- Clear, specific, detailed prompts for best results
- Consider cognitive development stage of the target grade
- Subject context is: {subject_context}"""

    # Call OpenAI with enhanced system message
    print("🤖 Calling OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": """You are an expert Educational Content Visualization Specialist. You have:
- 15 years experience in educational content design
- Deep understanding of child cognitive development
- Expertise in visual learning theory
- Professional prompt engineering skills for DALL-E
- Knowledge of age-appropriate content design

Your responses are:
- Detailed and specific
- Educationally sound
- Based on learning science
- Professionally formatted
- Always in valid JSON format

You create DALL-E prompts that are:
- Highly detailed (50-100 words)
- Specific about style, colors, perspective
- Age-appropriate
- Consistent across all options
- Professional quality"""
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    
    print(f"✅ Analysis complete!")
    print(f"   Image Required: {result['image_required']}")
    
    # Validate and enhance prompts if needed
    result = validate_and_enhance_prompts(result)
    
    # Save to database
    print("\n💾 Saving to database...")
    save_to_database(result)
    
    return result

def validate_and_enhance_prompts(result):
    """
    Validate that generated prompts meet quality standards
    """
    # Check if prompts are too short (less than 20 words)
    prompts_to_check = [
        'question_image_prompt',
        'option_a_image_prompt',
        'option_b_image_prompt',
        'option_c_image_prompt',
        'option_d_image_prompt'
    ]
    
    for prompt_key in prompts_to_check:
        prompt = result.get(prompt_key)
        if prompt and len(prompt.split()) < 20:
            print(f"⚠️  Warning: {prompt_key} seems too short. Consider regenerating.")
    
    # Check consistency - if one option has prompt, all should have
    option_prompts = [
        result.get('option_a_image_prompt'),
        result.get('option_b_image_prompt'),
        result.get('option_c_image_prompt'),
        result.get('option_d_image_prompt')
    ]
    
    non_null_count = sum(1 for p in option_prompts if p is not None)
    
    if non_null_count > 0 and non_null_count < 4:
        print(f"⚠️  Warning: Only {non_null_count}/4 options have image prompts. This may create unfair advantages.")
    
    return result