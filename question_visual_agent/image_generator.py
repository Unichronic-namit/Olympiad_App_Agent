import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Create images folder if it doesn't exist
IMAGES_FOLDER = "gemini_generated_images"
Path(IMAGES_FOLDER).mkdir(exist_ok=True)

def generate_image(prompt, question_id, image_type="question", option=None):
    """
    Generate image from prompt using Gemini API
    
    Args:
        prompt (str): The detailed image generation prompt
        question_id (int): Question ID for naming
        image_type (str): "question" or "option"
        option (str): "a", "b", "c", or "d" if image_type is "option"
    
    Returns:
        dict: {"success": bool, "file_path": str or None, "error": str or None}
    """
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return {
            "success": False,
            "file_path": None,
            "error": "GEMINI_API_KEY not found in .env"
        }
    
    # Build filename
    if image_type == "question":
        filename = f"q_{question_id}_question.png"
    else:
        filename = f"q_{question_id}_option_{option}.png"
    
    file_path = os.path.join(IMAGES_FOLDER, filename)
    
    print(f"\n🎨 Generating image: {filename}")
    print(f"   Prompt preview: {prompt[:80]}...")
    
    try:
        # Configure Gemini with API key
        genai.configure(api_key=api_key)
        
        # Create model instance
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        
        # Generate image
        print("   Calling Gemini API...")
        response = model.generate_content(prompt)
        
        # Check if response has content
        if not response.candidates:
            error_msg = "No image generated in response"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "file_path": None,
                "error": error_msg
            }
        
        # Extract image data
        candidate = response.candidates[0]
        if not candidate.content.parts:
            error_msg = "No image data in response parts"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "file_path": None,
                "error": error_msg
            }
        
        # Get inline image data
        part = candidate.content.parts[0]
        
        if not hasattr(part, 'inline_data') or not part.inline_data:
            part=candidate.content.parts[1]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                error_msg = "No inline_data found in response"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "file_path": None,
                    "error": error_msg
                }
        
        # Convert bytes to image and save
        image_bytes = part.inline_data.data
        image = Image.open(BytesIO(image_bytes))
        image.save(file_path)
        
        print(f"✅ Image saved: {file_path}")
        return {
            "success": True,
            "file_path": file_path,
            "error": None
        }
    
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "file_path": None,
            "error": error_msg
        }

def generate_images_for_question(question_id, prompts_data):
    """
    Generate all images for a question (question + 4 options)
    
    Args:
        question_id (int): Question ID
        prompts_data (dict): Dictionary containing all prompts from AI analysis
    
    Returns:
        dict: Results for all generated images
    """
    
    results = {
        "question_id": question_id,
        "images_generated": 0,
        "images_failed": 0,
        "details": {}
    }
    
    print(f"\n{'='*60}")
    print(f"🎨 GENERATING IMAGES FOR QUESTION {question_id}")
    print(f"{'='*60}")
    
    # Generate question image
    if prompts_data.get('question_image_prompt'):
        result = generate_image(
            prompt=prompts_data['question_image_prompt'],
            question_id=question_id,
            image_type="question"
        )
        results['details']['question'] = result
        if result['success']:
            results['images_generated'] += 1
        else:
            results['images_failed'] += 1
    
    # Generate option images
    options = ['a', 'b', 'c', 'd']
    for opt in options:
        prompt_key = f'option_{opt}_image_prompt'
        if prompts_data.get(prompt_key):
            result = generate_image(
                prompt=prompts_data[prompt_key],
                question_id=question_id,
                image_type="option",
                option=opt
            )
            results['details'][f'option_{opt}'] = result
            if result['success']:
                results['images_generated'] += 1
            else:
                results['images_failed'] += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully generated: {results['images_generated']} images")
    print(f"❌ Failed: {results['images_failed']} images")
    
    return results