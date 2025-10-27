import os
import psycopg2
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_db_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )

def fetch_question_prompts(question_id):
    """Fetch image prompts for a specific question"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
    SELECT question_id, question_image_prompt, 
           option_a_image_prompt, option_b_image_prompt,
           option_c_image_prompt, option_d_image_prompt
    FROM question_visual_prompts
    WHERE question_id = %s AND image_required = true;
    """
    
    cur.execute(query, (question_id,))
    result = cur.fetchone()
    
    conn.close()
    return result

def create_image_folder(question_id):
    """Create folder for storing images of a question"""
    folder_path = Path("generated_images") / f"question_{question_id}"
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def generate_image_with_gemini(prompt, output_path):
    """Generate image using Gemini 2.5 Flash Image model"""
    try:
        print(f"   Generating image: {output_path.name}")
        
        from PIL import Image
        from io import BytesIO
        
        # Create model instance
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        
        # Generate image
        print("   Calling Gemini API...")
        response = model.generate_content(prompt)
        
        # Track token usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else 0
            candidates_tokens = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
            total_tokens = usage.total_token_count if hasattr(usage, 'total_token_count') else 0
            
            # Calculate cost (Gemini 2.5 Flash pricing as of 2025)
            # Input: $0.075 per 1M tokens
            # Output: $0.30 per 1M tokens
            input_cost = (prompt_tokens / 1_000_000) * 0.075
            output_cost = (candidates_tokens / 1_000_000) * 0.30
            total_cost = input_cost + output_cost
            
            print(f"   📊 Tokens: {prompt_tokens} in + {candidates_tokens} out = {total_tokens} total")
            print(f"   💰 Cost: ${total_cost:.6f}")
        else:
            print(f"   ⚠️  Token usage not available")
        
        # Check if response has content
        if not response.candidates:
            raise Exception("No image generated in response")
        
        # Extract image data
        candidate = response.candidates[0]
        if not candidate.content.parts:
            raise Exception("No image data in response parts")
        
        # Get inline image data
        part = candidate.content.parts[0]
        
        if not hasattr(part, 'inline_data') or not part.inline_data:
            if len(candidate.content.parts) > 1:
                part = candidate.content.parts[1]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                raise Exception("No inline_data found in response")
        
        # Convert bytes to image and save
        image_bytes = part.inline_data.data
        image = Image.open(BytesIO(image_bytes))
        image.save(output_path)
        
        print(f"   ✅ Saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def generate_images_batch_experimental(prompts_data, question_id, folder):
    """EXPERIMENTAL: Generate all images using a single combined prompt for context"""
    
    print("\n🧪 EXPERIMENTAL BATCH MODE - Combining prompts for context")
    print("-" * 60)
    
    images_generated = 0
    images_failed = 0
    
    try:
        from PIL import Image
        from io import BytesIO
        
        # Use just the first prompt for testing (generate ONE image)
        combined_prompt = prompts_data.get('question_image_prompt', '')
        
        if not combined_prompt:
            combined_prompt = prompts_data.get('option_a_image_prompt', '')
        
        print(f"   📝 Combined prompt length: {len(combined_prompt)} characters")
        print(f"   🤖 Calling Gemini API (experimental batch)...")
        
        # Create model instance
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        
        # Generate image
        response = model.generate_content(combined_prompt)
        
        # Track token usage
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else 0
            candidates_tokens = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
            total_tokens = usage.total_token_count if hasattr(usage, 'total_token_count') else 0
            
            input_cost = (prompt_tokens / 1_000_000) * 0.075
            output_cost = (candidates_tokens / 1_000_000) * 0.30
            total_cost = input_cost + output_cost
            
            print(f"\n   📊 Batch Tokens: {prompt_tokens} in + {candidates_tokens} out = {total_tokens} total")
            print(f"   💰 Batch Cost: ${total_cost:.6f}")
        
        # Check if response has content
        if not response.candidates:
            raise Exception("No image generated in response")
        
        # Extract image data (Gemini typically returns only one image per call)
        candidate = response.candidates[0]
        if not candidate.content.parts:
            # Debug: Check if it's a text response instead
            print(f"\n⚠️  Response debug: {len(response.candidates)} candidates")
            if hasattr(candidate, 'content'):
                print(f"   Content type: {type(candidate.content)}")
                if hasattr(candidate.content, 'parts'):
                    print(f"   Parts: {len(candidate.content.parts)}")
                    for i, p in enumerate(candidate.content.parts):
                        print(f"   Part {i}: {type(p)}, has text={hasattr(p, 'text')}")
            raise Exception("No image data in response parts - possibly returned text instead of image")
        
        # Get inline image data
        part = candidate.content.parts[0]
        
        if not hasattr(part, 'inline_data') or not part.inline_data:
            if len(candidate.content.parts) > 1:
                part = candidate.content.parts[1]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                # Debug what we got
                print(f"⚠️  No inline_data found. Part type: {type(part)}")
                if hasattr(part, 'text'):
                    print(f"   Got text response instead: {part.text[:200]}...")
                raise Exception("No inline_data found in response - Gemini returned text instead of image")
        
        # Convert bytes to image and save (will only save one image)
        image_bytes = part.inline_data.data
        image = Image.open(BytesIO(image_bytes))
        
        # Save the single generated image as "question.png" (since batch only returns one)
        output_path = folder / "question_batch_experiment.png"
        image.save(output_path)
        
        print(f"   ✅ Saved experimental batch image: {output_path.name}")
        print(f"   ⚠️  NOTE: Gemini API returns only ONE image per call, not 5 separate images")
        print(f"   💡 Individual image generation is still recommended for full control")
        
        images_generated = 1
        
    except Exception as e:
        print(f"   ❌ Batch generation error: {str(e)}")
        images_failed = 5
    
    return images_generated, images_failed

def generate_images_for_question(question_id, use_batch_experiment=False):
    """Generate all images for a single question"""
    
    print(f"\n{'='*60}")
    print(f"🎨 GENERATING IMAGES FOR QUESTION {question_id}")
    print(f"{'='*60}\n")
    
    # Fetch prompts from database
    print("📚 Fetching prompts from database...")
    prompts_data = fetch_question_prompts(question_id)
    
    if not prompts_data:
        print(f"❌ No image prompts found for question {question_id}")
        print("   Make sure the question has image_required = true")
        return
    
    print("✅ Prompts found!\n")
    
    # Create folder for this question's images
    folder = create_image_folder(question_id)
    print(f"📁 Output folder: {folder}\n")
    
    # Choose generation mode
    if use_batch_experiment:
        print("🔬 Using EXPERIMENTAL batch mode")
        images_generated, images_failed = generate_images_batch_experimental(prompts_data, question_id, folder)
    else:
        print("🖼️  Using INDIVIDUAL mode (default)")
        images_generated, images_failed = generate_images_individual(prompts_data, folder)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully generated: {images_generated} images")
    print(f"❌ Failed: {images_failed} images")
    print(f"📁 Images saved in: {folder}")
    if not use_batch_experiment:
        print(f"\n💡 Note: Individual token usage and cost shown above for each image")
    print(f"{'='*60}\n")

def generate_images_individual(prompts_data, folder):
    """Generate images individually (standard mode)"""
    
    images_generated = 0
    images_failed = 0
    
    # Question image
    if prompts_data['question_image_prompt']:
        output_path = folder / "question.png"
        result = generate_image_with_gemini(prompts_data['question_image_prompt'], output_path)
        if result:
            images_generated += 1
            # Track cost (will need to return from function if you want exact tracking)
        else:
            images_failed += 1
    
    # Option images
    options = ['a', 'b', 'c', 'd']
    for opt in options:
        prompt_key = f'option_{opt}_image_prompt'
        if prompts_data.get(prompt_key):
            output_path = folder / f"option_{opt}.png"
            result = generate_image_with_gemini(prompts_data[prompt_key], output_path)
            if result:
                images_generated += 1
            else:
                images_failed += 1
    
    return images_generated, images_failed

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 IMAGE GENERATOR - GEMINI API")
    print("="*60)
    
    # Get question ID from user
    question_id = input("\nEnter question ID: ").strip()
    
    # Ask for mode
    print("\nChoose generation mode:")
    print("1. Individual (default) - Generate each image separately")
    print("2. Batch Experiment - Combine all prompts for context")
    mode_choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
    
    use_batch = (mode_choice == "2")
    
    try:
        question_id = int(question_id)
        generate_images_for_question(question_id, use_batch_experiment=use_batch)
    except ValueError:
        print("❌ Invalid question ID! Please enter a number.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
