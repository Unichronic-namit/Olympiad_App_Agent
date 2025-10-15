import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Create images folder if it doesn't exist
IMAGES_FOLDER = "generated_images"
Path(IMAGES_FOLDER).mkdir(exist_ok=True)

def generate_image(prompt, question_id, image_type="question", option=None):
    """
    Generate image from prompt using external API
    
    Args:
        prompt (str): The detailed image generation prompt
        question_id (int): Question ID for naming
        image_type (str): "question" or "option"
        option (str): "a", "b", "c", or "d" if image_type is "option"
    
    Returns:
        dict: {"success": bool, "file_path": str or None, "error": str or None}
    """
    
    api_key = os.getenv("IMAGE_GEN_API_KEY")
    api_url = os.getenv("IMAGE_GEN_API_URL")
    
    if not api_key or not api_url:
        return {
            "success": False,
            "file_path": None,
            "error": "IMAGE_GEN_API_KEY or IMAGE_GEN_API_URL not found in .env"
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
        # Stability AI API headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Stability AI specific payload
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            # Stability AI returns JSON with base64 image
            data = response.json()
            
            # Extract base64 image from response
            import base64
            if "artifacts" in data and len(data["artifacts"]) > 0:
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                
                # Save image
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"✅ Image saved: {file_path}")
                return {
                    "success": True,
                    "file_path": file_path,
                    "error": None
                }
            else:
                error_msg = "No image data in response"
                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "file_path": None,
                    "error": error_msg
                }
        else:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "file_path": None,
                "error": error_msg
            }
    
    except requests.exceptions.Timeout:
        error_msg = "Request timed out after 60 seconds"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "file_path": None,
            "error": error_msg
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