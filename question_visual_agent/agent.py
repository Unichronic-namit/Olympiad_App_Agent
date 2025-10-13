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
    prompt = f"""You are an expert Educational Content Visualization Specialist with 15+ years of experience in creating educational imagery and prompt engineering for AI image generation systems.

# CONTEXT
- Student Grade Level: {q['grade']} (Age: {q['grade'] + 5} years approximately)
- Difficulty Level: {q['difficulty']}
- Exam: {q['exam']} Olympiad
- Level: {q['level']}
- Subject/Section: {subject_context}

# YOUR MISSION
1. Analyze if this question needs visual aids for better learning
2. If yes, create EXTREMELY DETAILED, SPECIFIC image generation prompts that will work with ANY AI image generator (Midjourney, Stable Diffusion, DALL-E, etc.)

# GRADE-SPECIFIC VISUAL REQUIREMENTS

**Grades 1-3 (Ages 6-8):**
- Style: Bright cartoon illustrations, simple shapes
- Colors: Primary colors (red, blue, yellow), high saturation
- Complexity: Single subject, minimal background elements
- Text: None or very minimal labels
- Mood: Cheerful, friendly, welcoming

**Grades 4-5 (Ages 9-10):**
- Style: Semi-realistic illustrations with some detail
- Colors: Vibrant but natural color palettes
- Complexity: Main subject + 2-3 supporting elements
- Text: Simple labels acceptable
- Mood: Engaging, informative

**Grades 6-8 (Ages 11-13):**
- Style: Realistic illustrations or clean diagrams
- Colors: Natural, balanced, professional
- Complexity: Multiple elements, layered information
- Text: Labels, annotations, brief descriptions
- Mood: Professional, educational

**Grades 9-10 (Ages 14-15):**
- Style: Technical, photorealistic, or schematic
- Colors: Professional, accurate to reality
- Complexity: Detailed, multi-layered information
- Text: Technical labels, measurements, annotations
- Mood: Academic, precise

# QUESTION ANALYSIS

**Question ID:** {q['question_id']}
**Question Text:** {q['question_text']}

**Options:**
A) {q['option_a']}
B) {q['option_b']}
C) {q['option_c']}
D) {q['option_d']}

# CRITICAL RULES FOR VISUAL CONSISTENCY

1. **All option images MUST be identical in:**
   - Visual style (cartoon/realistic/diagram)
   - Image dimensions and framing
   - Color saturation and tone
   - Level of detail
   - Background type and color
   - Lighting conditions
   - Perspective/camera angle

2. **Images must NOT give hints through:**
   - Better quality for correct answer
   - Different artistic styles
   - More detail on one option
   - Different color schemes
   - Size variations

# PROMPT STRUCTURE REQUIREMENTS

Each image prompt MUST include ALL these elements in this order:

1. **SUBJECT** (What): Precisely describe the main object/concept
   - Be specific: Not "a device" but "a wireless computer mouse with ergonomic design"
   
2. **CONTEXT** (Why): Educational purpose
   - Example: "for teaching grade 3 students about input devices"

3. **STYLE** (How): Artistic approach
   - Specific styles: "flat design illustration", "photorealistic render", "technical line drawing"
   - NOT vague: "nice drawing", "good image"

4. **COMPOSITION** (Layout):
   - Camera angle: "straight-on view", "45-degree angle", "bird's eye view"
   - Framing: "centered in frame", "occupying 70% of image"
   - Position: "object positioned in center", "slightly left of center"

5. **COLORS** (Palette):
   - Specific colors: "bright cherry red", "navy blue", "lime green"
   - Color scheme: "monochromatic blue scheme", "complementary orange and blue"
   - NOT vague: "colorful", "nice colors"

6. **BACKGROUND**:
   - Specific: "solid white background", "soft gradient from light blue to white", "blurred classroom setting"
   - NOT vague: "simple background"

7. **LIGHTING**:
   - Type: "soft diffused lighting", "bright studio lighting", "natural daylight"
   - Direction: "light from top-left", "evenly lit"
   - Shadows: "minimal shadows", "soft drop shadow"

8. **DETAILS & TEXTURE**:
   - Surface: "smooth plastic texture", "matte finish", "glossy surface"
   - Details: "visible buttons", "brand logo removed", "clean edges"

9. **TECHNICAL SPECS**:
   - Quality: "high resolution", "sharp focus", "8K quality"
   - Format notes: "no text overlays", "no watermarks", "clean professional image"

10. **AGE-APPROPRIATE ELEMENTS**:
    - For 1-5: "child-friendly", "non-threatening", "engaging and fun"
    - For 6-10: "educational and clear", "professional quality"

# EXAMPLE EXCELLENT PROMPTS

**Grade 2 - Computer Mouse (Option):**
"A bright blue wireless computer mouse with rounded ergonomic shape, designed for teaching grade 2 students about input devices. Flat illustration style with bold outlines. Mouse positioned in center of frame, occupying 60% of image space, shown from 45-degree top-right angle. Solid white background with no shadows. Mouse colored in vibrant sky blue (#87CEEB) with darker blue (#4682B4) accent on scroll wheel. Two visible buttons clearly defined. Smooth cartoon-style rendering with minimal detail. Soft even lighting from top. Matte plastic texture appearance. High contrast against white background. Child-friendly and simple. No text, labels, or branding. Clean professional educational illustration. 8K resolution, sharp edges, vector-style quality."

**Grade 5 - Plant Cell (Question):**
"A detailed cross-section diagram of a plant cell for teaching grade 5 biology students. Semi-realistic scientific illustration style. Cell shown in center, taking up 80% of frame, with cutaway view revealing internal structures. Light green cell wall (#90EE90) as outer layer, cell membrane just inside in darker green (#228B22). Visible organelles: large central vacuole in pale blue (#E0F4FF), nucleus in light purple (#DDA0DD) with darker nucleolus, multiple green chloroplasts (#3CB371), mitochondria in pink (#FFB6C1), endoplasmic reticulum network in light yellow (#FFFACD). Each organelle clearly distinguished by color and shape. White background for clarity. Soft educational lighting from top-left creating gentle shadows. Labels removed (for educational testing). Clean line work, smooth gradients. Professional textbook quality. Medium detail level appropriate for grade 5. 4K resolution, crisp edges, scientific accuracy."

**Grade 8 - Circuit Board (Question):**
"Professional overhead photograph of a computer circuit board (motherboard) for teaching grade 8 technology students. Photorealistic style. Rectangular green PCB (printed circuit board) centered in frame, occupying 75% of image. Standard motherboard green color (#2F4F2F) with golden-yellow copper traces (#FFD700) creating complex pathways across surface. Multiple components visible: black rectangular RAM slots on left side, silver heat sinks on processors, small cylindrical capacitors in various colors, square microchips with visible pins. Shot from directly above (90-degree top-down view). Shallow depth of field with center in sharp focus, edges slightly softer. Bright white LED studio lighting from multiple angles eliminating harsh shadows. Clean professional tech photography. Glossy and matte surface textures visible. Extreme detail showing solder points and component labels. Modern contemporary hardware (2020s era). White background fading to light gray at edges. Technical accuracy essential. No hands or tools visible. Product photography quality. 8K resolution, macro photography sharpness."

# BAD PROMPTS TO AVOID

❌ "A colorful mouse" 
   - Too vague, no style, no context

❌ "Computer keyboard in nice colors for students"
   - "Nice colors" is subjective, no specific palette

❌ "Educational diagram of a cell with labels"
   - No style specified, which organelles?, what view?

❌ "Realistic photo of circuit board"
   - What angle? What lighting? What background?

# OUTPUT JSON FORMAT

Return valid JSON with:

{{
  "question_id": {q['question_id']},
  "grade": {q['grade']},
  "image_required": boolean,
  "reason": "2-3 sentences explaining decision based on grade level, content type, and learning benefit",
  "question_image_prompt": "DETAILED 100-150 word prompt following ALL 10 requirements above" OR null,
  "option_a_image_prompt": "DETAILED 100-150 word prompt for: {q['option_a']}" OR null,
  "option_b_image_prompt": "DETAILED 100-150 word prompt for: {q['option_b']}" OR null,
  "option_c_image_prompt": "DETAILED 100-150 word prompt for: {q['option_c']}" OR null,
  "option_d_image_prompt": "DETAILED 100-150 word prompt for: {q['option_d']}" OR null
}}

# CRITICAL REMINDERS

- EVERY prompt must be 100-150 words minimum
- Include SPECIFIC colors with hex codes when possible
- Describe EXACT positioning and framing
- Specify PRECISE lighting conditions
- Name CONCRETE visual style (not "good" or "nice")
- All option prompts must match in style and quality
- Never use vague terms like "colorful", "nice", "good", "simple"
- Think like you're instructing a photographer or illustrator who's never seen the subject"""

    # Call OpenAI with enhanced system message
    print("🤖 Calling OpenAI API...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": """You are a world-class Prompt Engineering Expert specializing in AI image generation. Your prompts are used by Fortune 500 companies for educational content.

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
            },
            {
                "role": "user", 
                "content": prompt
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